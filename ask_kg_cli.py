#!/usr/bin/env python3
"""
ArchE Knowledge Graph CLI - Direct KG Queries Without LLM Calls
Allows querying ArchE's internal Knowledge Graph for concepts from agi.txt
and comparing answers to real-world understanding.
"""

import sys
import json
import time
import argparse
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.spr_manager import SPRManager
from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessorAdapter
from Three_PointO_ArchE.kg_natural_language_generator import KGNaturalLanguageGenerator
from Three_PointO_ArchE.arche_self_reference_system import ArcheSelfReferenceSystem

# Optional: For real-world comparison
try:
    from Three_PointO_ArchE.llm_tool import generate_text_llm
    LLM_TOOL_AVAILABLE = True
except ImportError:
    LLM_TOOL_AVAILABLE = False

try:
    from Three_PointO_ArchE.web_search_tool import search_web
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False


class KGCli:
    """CLI interface for querying Knowledge Graph directly."""
    
    def __init__(self, enable_comparison: bool = False, document_path: Optional[str] = None):
        """Initialize KG components."""
        spr_file = project_root / "knowledge_graph" / "spr_definitions_tv.json"
        
        if not spr_file.exists():
            print(f"❌ ERROR: SPR file not found at {spr_file}")
            sys.exit(1)
        
        print(f"📚 Loading Knowledge Graph from {spr_file}...")
        self.spr_manager = SPRManager(str(spr_file))
        self.zepto_processor = ZeptoSPRProcessorAdapter()
        self.nlg_generator = KGNaturalLanguageGenerator()  # Natural language generator (NO LLM)
        self.self_ref_system = ArcheSelfReferenceSystem(project_root)  # Self-reference system
        self.enable_comparison = enable_comparison
        self.document_path = document_path
        self.document_content = None
        
        # Load document if specified
        if document_path:
            self._load_document(document_path)
        
        total_sprs = len(self.spr_manager.sprs)
        agi_sprs = sum(1 for spr in self.spr_manager.sprs.values() 
                      if 'agi.txt' in spr.get('source', '').lower())
        
        print(f"✅ Knowledge Graph loaded: {total_sprs:,} total SPRs")
        print(f"   • {agi_sprs:,} SPRs from agi.txt (Mastermind_AI legacy knowledge)")
        print(f"   • {total_sprs - agi_sprs:,} SPRs from other sources")
        
        if document_path:
            print(f"   • Document mode: Querying from {Path(document_path).name}")
        
        if enable_comparison:
            if LLM_TOOL_AVAILABLE:
                print(f"   • Real-world comparison: ENABLED (using LLM)")
            elif WEB_SEARCH_AVAILABLE:
                print(f"   • Real-world comparison: ENABLED (using web search)")
            else:
                print(f"   ⚠️  Real-world comparison requested but no tools available")
        print()
    
    def _load_document(self, document_path: str):
        """Load and parse a document for querying."""
        doc_file = Path(document_path)
        if not doc_file.is_absolute():
            doc_file = project_root / document_path
        
        if not doc_file.exists():
            print(f"⚠️  Warning: Document not found at {doc_file}")
            print(f"   Falling back to Knowledge Graph only")
            return
        
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                self.document_content = f.read()
            print(f"📄 Document loaded: {doc_file.name} ({len(self.document_content):,} characters)")
        except Exception as e:
            print(f"⚠️  Warning: Failed to load document: {e}")
            print(f"   Falling back to Knowledge Graph only")
    
    def _extract_document_sections(self, query: str) -> List[Dict[str, Any]]:
        """Extract relevant sections from loaded document based on query."""
        if not self.document_content:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Split document into sections (by markdown headers)
        sections = []
        current_section = {"title": "", "content": "", "level": 0}
        
        for line in self.document_content.split('\n'):
            # Check for markdown headers
            if line.startswith('#'):
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(current_section.copy())
                
                # Start new section
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                current_section = {
                    "title": title,
                    "content": "",
                    "level": level
                }
            else:
                current_section["content"] += line + "\n"
        
        # Add last section
        if current_section["content"].strip():
            sections.append(current_section)
        
        # Score sections by relevance
        # Extract meaningful query keywords (remove stop words)
        stop_words = {'what', 'is', 'are', 'the', 'a', 'an', 'this', 'that', 'these', 'those', 'how', 'does', 'do', 'tell', 'me', 'about', 'explain', 'define', 'can', 'will', 'would', 'should', 'could'}
        meaningful_query_words = [w for w in query_words if w not in stop_words and len(w) > 2]
        
        scored_sections = []
        for section in sections:
            section_text = (section["title"] + " " + section["content"]).lower()
            section_words = set(section_text.split())
            title_lower = section["title"].lower()
            
            # Calculate relevance score using meaningful words
            if meaningful_query_words:
                common_words = set(meaningful_query_words) & section_words
                relevance = len(common_words) / max(len(meaningful_query_words), 1)
            else:
                # Fallback to all query words if no meaningful words
                common_words = query_words & section_words
                relevance = len(common_words) / max(len(query_words), 1)
            
            # Strong boost if key words appear in title (especially for queries like "What are the Mandates?")
            title_matches = sum(1 for word in meaningful_query_words if word in title_lower)
            if title_matches > 0:
                relevance += title_matches * 0.5  # Increased from 0.3
                # Extra boost if ALL meaningful words are in title
                if title_matches == len(meaningful_query_words) and len(meaningful_query_words) > 0:
                    relevance += 0.3
            
            # Boost for exact phrase matches in title (e.g., "Mandates" in "The Mandates")
            for word in meaningful_query_words:
                if word in title_lower:
                    relevance += 0.2
            
            if relevance > 0.1:  # Only include relevant sections
                scored_sections.append({
                    "section": section,
                    "relevance": relevance
                })
        
        # Sort by relevance
        scored_sections.sort(key=lambda x: x["relevance"], reverse=True)
        
        return [s["section"] for s in scored_sections[:5]]  # Return top 5 sections
    
    def _construct_document_answer(self, document_sections: List[Dict[str, Any]], query: str) -> str:
        """
        Construct a natural language answer from document sections.
        
        Args:
            document_sections: List of relevant document sections
            query: Original query
            
        Returns:
            Formatted answer text
        """
        if not document_sections:
            return ""
        
        parts = []
        parts.append("Based on the referenced document:\n")
        
        for i, section in enumerate(document_sections[:3], 1):  # Top 3 sections
            title = section.get("title", "").strip()
            content = section.get("content", "").strip()
            
            if title:
                parts.append(f"\n**{title}**\n")
            
            # Extract relevant excerpt (first 500 chars, or up to a sentence boundary)
            if len(content) > 500:
                # Try to find a sentence boundary
                excerpt = content[:500]
                last_period = excerpt.rfind('.')
                last_newline = excerpt.rfind('\n')
                cut_point = max(last_period, last_newline)
                if cut_point > 300:  # Only cut at sentence if we have enough content
                    excerpt = content[:cut_point + 1]
                else:
                    excerpt = content[:500] + "..."
            else:
                excerpt = content
            
            if excerpt:
                parts.append(excerpt)
                if len(content) > 500:
                    parts.append("\n")
        
        return "\n".join(parts)
    
    def _is_real_zepto_spr(self, zepto_spr: str) -> bool:
        """
        Check if a Zepto SPR is actually compressed (short, symbolic) 
        or just pseudo-compressed text (long, readable).
        
        Real Zepto SPRs are:
        - Short (typically < 50 characters)
        - Contain symbolic characters (Greek letters, pipes, etc.)
        - Not readable as plain text
        
        Args:
            zepto_spr: The Zepto SPR string to check
            
        Returns:
            True if it's a real Zepto-compressed SPR, False if it's pseudo-compressed
        """
        if not zepto_spr or not zepto_spr.strip() or zepto_spr == 'Ξ':
            return False
        
        # Real Zepto SPRs are short
        if len(zepto_spr) > 50:
            return False
        
        # Real Zepto SPRs contain symbolic characters
        zepto_symbols = ['|', 'Γ', 'Σ', 'Δ', 'Θ', 'Λ', 'Ξ', 'Π', 'Φ', 'Ψ', 'Ω', 
                        'Α', 'Β', 'Ε', 'Η', 'Ι', 'Κ', 'Μ', 'Ν', 'Ο', 'Ρ', 'Τ', 'Υ', 'Χ']
        has_symbols = any(symbol in zepto_spr for symbol in zepto_symbols)
        
        # Real Zepto SPRs are not readable as plain text (no spaces, mostly symbols)
        is_readable = ' ' in zepto_spr or (len([c for c in zepto_spr if c.isalpha() and c.islower()]) > len(zepto_spr) * 0.5)
        
        return has_symbols and not is_readable
    
    def _detect_sprs_with_intent_inference(self, query: str) -> List[Dict[str, Any]]:
        """
        Enhanced SPR detection with intent inference.
        Searches both Guardian pointS format and Zepto SPRs by decompressing them.
        
        This method translates natural language queries (e.g., "What is cognitive resonance?")
        to SPR matches (e.g., CognitiveResonancE) by searching:
        1. Guardian pointS format (exact matches)
        2. SPR terms and definitions
        3. Zepto SPR decompressed content
        4. Semantic variations and keywords
        
        Args:
            query: Natural language query
            
        Returns:
            List of detected SPRs with confidence scores, sorted by relevance
        """
        # Step 1: Use existing SPR detection (searches Guardian pointS, terms, definitions)
        detected_sprs = self.spr_manager.detect_sprs_with_confidence(query)
        
        # Step 2: Enhance with Zepto SPR searching
        # Decompress Zepto SPRs and search within their content
        query_lower = query.lower()
        query_keywords = set([w for w in query_lower.split() if len(w) > 2])
        
        zepto_enhanced_sprs = []
        for spr_id, spr_data in self.spr_manager.sprs.items():
            zepto_spr = spr_data.get('zepto_spr', '')
            symbol_codex = spr_data.get('symbol_codex', {})
            
            # Skip if no Zepto SPR or if already detected
            if not zepto_spr or zepto_spr.strip() == '' or zepto_spr == 'Ξ':
                continue
            
            # Skip pseudo-compressed SPRs (long text that's not actually Zepto-compressed)
            if not self._is_real_zepto_spr(zepto_spr):
                continue  # Only process real Zepto-compressed SPRs
            
            # Check if this SPR was already detected
            already_detected = any(s.get('spr_id') == spr_id for s in detected_sprs)
            if already_detected:
                continue  # Skip, already found via Guardian pointS/term matching
            
            # Try to decompress Zepto SPR
            try:
                decomp_result = self.zepto_processor.decompress_from_zepto(
                    zepto_spr=zepto_spr,
                    codex=symbol_codex
                )
                
                if decomp_result and not decomp_result.error and decomp_result.decompressed_text:
                    decompressed_lower = decomp_result.decompressed_text.lower()
                    
                    # Check if query keywords appear in decompressed content
                    matching_keywords = sum(1 for kw in query_keywords if kw in decompressed_lower)
                    
                    if matching_keywords > 0:
                        # Calculate confidence based on keyword matches
                        confidence = min(0.85, 0.4 + (matching_keywords * 0.1))
                        
                        # Boost confidence if query words appear multiple times
                        query_word_count = sum(decompressed_lower.count(kw) for kw in query_keywords)
                        if query_word_count > 3:
                            confidence = min(0.9, confidence + 0.1)
                        
                        zepto_enhanced_sprs.append({
                            'spr_id': spr_id,
                            'spr_data': spr_data,
                            'activation_level': confidence,
                            'confidence_score': confidence,
                            'guardian_point': spr_id,
                            'matched_via': 'zepto_spr',
                            'keyword_matches': matching_keywords,
                            'knowledge_network': {
                                'resonance_frequency': 0.7,
                                'activation_history': [],
                                'related_sprs': []
                            }
                        })
            except Exception as e:
                # Skip if decompression fails
                continue
        
        # Step 3: Filter out very short/low-quality matches
        # Remove SPRs with very short IDs that are likely false positives
        # Expanded list of common words that should be filtered aggressively
        # These are common English words that should NEVER be treated as meaningful SPRs
        common_words_blacklist = {
            # Very short (1-2 chars) - ALWAYS filter
            'an', 'in', 'on', 'at', 'to', 'of', 'is', 'it', 'as', 'or', 'be', 'we', 'if', 'my', 'up', 'so', 'no', 'go', 'do', 'by', 'me', 'he', 'us', 'am', 'id',
            # Short (3 chars) - ALWAYS filter
            'and', 'the', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use',
            # Medium (4 chars) - ALWAYS filter
            'that', 'with', 'have', 'this', 'will', 'your', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'what', 'when', 'which', 'will', 'with', 'would', 'year', 'your'
        }
        
        # Specific low-quality SPRs that should be completely excluded
        # These are known bad SPRs from agi.txt extraction that are just common words
        blacklisted_spr_ids = {
            'AnD', 'and',  # The specific "AnD" SPR that's causing issues
            'ExpandinG', 'expanding',
            'HandleD', 'handled',
            'UnderstandinG', 'understanding',
        }
        
        filtered_sprs = []
        for spr in detected_sprs + zepto_enhanced_sprs:
            spr_id = spr.get('spr_id', '')
            confidence = spr.get('confidence_score', spr.get('activation_level', 0.0))
            spr_data = spr.get('spr_data', {})
            
            # COMPLETE BLACKLIST: Exclude specific low-quality SPRs (no exceptions)
            if spr_id in blacklisted_spr_ids or spr_id.lower() in blacklisted_spr_ids:
                continue  # Never include these, regardless of confidence
            
            # COMPLETE BLACKLIST: Exclude common words (1-4 chars) - these are NEVER meaningful SPRs
            spr_id_lower = spr_id.lower()
            if len(spr_id) <= 4 and spr_id_lower in common_words_blacklist:
                continue  # Never include common words, regardless of confidence
            
            # Filter out very low confidence matches
            if confidence < 0.3:  # Raised from 0.25
                continue
            
            # Ensure SPR has meaningful data
            if not spr_data:
                continue
            
            # Check if SPR has at least a term or definition
            if not spr_data.get('term') and not spr_data.get('definition'):
                # Only keep if it has Zepto SPR with meaningful content
                zepto_spr = spr_data.get('zepto_spr', '')
                if not zepto_spr or zepto_spr.strip() == '' or zepto_spr == 'Ξ':
                    continue
                # Even with Zepto, require decent confidence
                if confidence < 0.5:
                    continue
            
            # Additional quality check: filter SPRs with very short or generic terms
            spr_term = spr_data.get('term', '').lower()
            if spr_term and len(spr_term) <= 2:
                if confidence < 0.8:
                    continue
            
            filtered_sprs.append(spr)
        
        # Step 4: Sort by confidence (highest first)
        filtered_sprs.sort(key=lambda x: x.get('confidence_score', x.get('activation_level', 0.0)), reverse=True)
        
        # Step 5: Deduplicate (keep highest confidence version)
        seen_spr_ids = set()
        unique_sprs = []
        for spr in filtered_sprs:
            spr_id = spr.get('spr_id')
            if spr_id not in seen_spr_ids:
                seen_spr_ids.add(spr_id)
                unique_sprs.append(spr)
        
        return unique_sprs
    
    def query_kg(self, query: str, min_confidence: float = 0.3) -> Optional[Dict[str, Any]]:
        """
        Query Knowledge Graph directly without LLM calls.
        If document_path is set, also searches within that document.
        Supports @ references for dynamic component access.
        
        Uses intent inference to translate natural language queries to SPRs,
        searching both Guardian pointS format and Zepto SPRs.
        
        Args:
            query: User question (may contain @ references like @PRIME_ARCHE_PROTOCOL.md)
            min_confidence: Minimum confidence threshold
            
        Returns:
            Dictionary with response and metadata, or None if no match
        """
        start_time = time.time()
        
        # Check for @ references in query
        ref_matches = re.findall(r'@(\S+)', query)
        referenced_components = []
        if ref_matches:
            for ref_match in ref_matches:
                component = self.self_ref_system.resolve_reference(ref_match)
                if component:
                    referenced_components.append(component)
                    # If it's a document, load it
                    if component.component_type in ['document', 'protocol']:
                        self.document_path = component.path
                        self._load_document(component.path)
        
        # Clean query: Remove @ references for SPR detection (they're already processed)
        clean_query = re.sub(r'@\S+\s*', '', query).strip()
        if not clean_query:
            clean_query = query  # Fallback if cleaning removed everything
        
        # If document mode, try document search first
        document_sections = []
        if self.document_path and self.document_content:
            document_sections = self._extract_document_sections(clean_query)
        
        # Step 1: Detect relevant SPRs using intent inference
        # This searches Guardian pointS format, terms, definitions, and Zepto SPRs
        detected_sprs = self._detect_sprs_with_intent_inference(clean_query)
        
        # If document mode and we found relevant sections, enhance the query context
        if document_sections and detected_sprs:
            # Boost confidence for SPRs that appear in document sections
            for spr in detected_sprs:
                spr_term = spr.get('spr_data', {}).get('term', '').lower()
                spr_id = spr.get('spr_id', '').lower()
                for section in document_sections:
                    section_text = (section["title"] + " " + section["content"]).lower()
                    # Check if SPR term or ID appears in section
                    if spr_term in section_text or spr_id in section_text:
                        # Boost confidence significantly for document matches
                        current_conf = spr.get('confidence_score', spr.get('activation_level', 0.0))
                        spr['confidence_score'] = min(1.0, current_conf + 0.3)
                        spr['document_boost'] = True  # Mark as document-enhanced
        
        # Prioritize document-based answers when document sections are highly relevant
        if document_sections:
            # Check if any document section has high relevance (contains key query terms)
            query_words = set([w.lower() for w in clean_query.split() if len(w) > 3])
            high_relevance_sections = []
            for section in document_sections:
                section_text = (section["title"] + " " + section["content"]).lower()
                section_words = set(section_text.split())
                matching_words = query_words & section_words
                if len(matching_words) >= 2:  # At least 2 key words match
                    high_relevance_sections.append(section)
            
            # If we have highly relevant document sections, prioritize SPRs that match them
            if high_relevance_sections and detected_sprs:
                for spr in detected_sprs:
                    spr_term = spr.get('spr_data', {}).get('term', '').lower()
                    for section in high_relevance_sections:
                        section_text = (section["title"] + " " + section["content"]).lower()
                        if spr_term in section_text:
                            # Extra boost for high-relevance document matches
                            current_conf = spr.get('confidence_score', spr.get('activation_level', 0.0))
                            spr['confidence_score'] = min(1.0, current_conf + 0.15)
        
        # PRIORITY CHECK: If document is loaded and has highly relevant sections, prioritize document answer
        # This handles cases like "What are the Mandates?" where the document directly answers
        if document_sections and len(document_sections) > 0:
            # Check if document sections are highly relevant (title matches key query terms)
            stop_words = {'what', 'is', 'are', 'the', 'a', 'an', 'this', 'that', 'these', 'those', 'how', 'does', 'do', 'tell', 'me', 'about', 'explain', 'define'}
            meaningful_query_words = [w.lower() for w in clean_query.split() if w.lower() not in stop_words and len(w) > 2]
            
            highly_relevant_document = False
            for section in document_sections[:3]:  # Check top 3 sections
                title_lower = section["title"].lower()
                # If key query words appear in section title, it's highly relevant
                title_matches = sum(1 for word in meaningful_query_words if word in title_lower)
                if title_matches >= len(meaningful_query_words) * 0.5 and len(meaningful_query_words) > 0:
                    highly_relevant_document = True
                    break
            
            # If document is highly relevant, use it even if SPRs are found (unless SPR has very high confidence)
            if highly_relevant_document:
                # Only use SPR if it has very high confidence AND document boost
                if detected_sprs:
                    best_spr = max(detected_sprs, 
                                 key=lambda s: s.get('confidence_score', s.get('activation_level', 0.0)))
                    spr_confidence = best_spr.get('confidence_score', best_spr.get('activation_level', 0.0))
                    # Only prefer SPR if it's document-boosted AND has very high confidence
                    if not (best_spr.get('document_boost', False) and spr_confidence > 0.85):
                        # Prefer document answer - construct response from document sections
                        response_text = self._construct_document_answer(document_sections, clean_query)
                        if response_text:
                            return {
                                "query": query,
                                "response": response_text,
                                "spr_id": None,
                                "spr_term": None,
                                "category": "document",
                                "confidence": 0.9,  # High confidence for document matches
                                "zepto_spr": None,
                                "blueprint": None,
                                "relationships": {},
                                "execution_time_ms": (time.time() - start_time) * 1000,
                                "source": f"document:{Path(self.document_path).name}",
                                "llm_bypassed": True,
                                "autonomous": True,
                                "document_sections": len(document_sections),
                                "referenced_components": [comp.ref_id for comp in referenced_components] if referenced_components else []
                            }
        
        if not detected_sprs and not document_sections:
            return None
        
        # Step 2: Find best match
        # Prioritize SPRs with document boost, then by confidence
        if detected_sprs:
            best_match = max(detected_sprs, 
                            key=lambda s: (
                                s.get('document_boost', False),  # Document matches first
                                s.get('confidence_score', s.get('activation_level', 0.0))
                            ))
            confidence = best_match.get('confidence_score', best_match.get('activation_level', 0.0))
            
            if confidence < min_confidence:
                return None
        else:
            # No SPRs found, but we have document sections - use document answer
            response_text = self._construct_document_answer(document_sections, clean_query)
            if response_text:
                return {
                    "query": query,
                    "response": response_text,
                    "spr_id": None,
                    "spr_term": None,
                    "category": "document",
                    "confidence": 0.8,
                    "zepto_spr": None,
                    "blueprint": None,
                    "relationships": {},
                    "execution_time_ms": (time.time() - start_time) * 1000,
                    "source": f"document:{Path(self.document_path).name}",
                    "llm_bypassed": True,
                    "autonomous": True,
                    "document_sections": len(document_sections),
                    "referenced_components": [comp.ref_id for comp in referenced_components] if referenced_components else []
                }
            return None
        
        # Step 3: Extract SPR data
        spr_data = best_match.get('spr_data', {})
        if not spr_data:
            return None
        
        spr_id = spr_data.get('spr_id', 'unknown')
        spr_term = spr_data.get('term', spr_id)
        category = spr_data.get('category', 'unknown')
        zepto_spr = spr_data.get('zepto_spr', '')
        symbol_codex = spr_data.get('symbol_codex', {})
        definition = spr_data.get('definition', '')
        blueprint = spr_data.get('blueprint_details', '')
        relationships = spr_data.get('relationships', {})
        
        # Step 4: Generate natural language explanation from SPR data (NO LLM)
        # This converts raw SPR data into readable explanations without LLM calls
        response_text = self.nlg_generator.generate_explanation(spr_data)
        
        # If NLG produces minimal output, fallback to definition
        if not response_text or len(response_text) < 50:
            response_text = definition if definition else ""
            
            # If still minimal, try Zepto decompression as last resort
            # Only attempt if it's a real Zepto-compressed SPR (not pseudo-compressed)
            if (not response_text or len(response_text) < 50) and zepto_spr and zepto_spr.strip() and zepto_spr != 'Ξ':
                if self._is_real_zepto_spr(zepto_spr):
                    try:
                        decomp_result = self.zepto_processor.decompress_from_zepto(
                            zepto_spr=zepto_spr,
                            codex=symbol_codex
                        )
                        
                        if decomp_result and not decomp_result.error and decomp_result.decompressed_text:
                            if len(decomp_result.decompressed_text) > len(response_text):
                                response_text = decomp_result.decompressed_text
                    except Exception as e:
                        pass  # Keep definition
                # If pseudo-compressed, don't try to decompress (it's already readable text)
        
        # Enhance with NLG if we have definition but want richer explanation
        if response_text and len(response_text) < 200:
            enhanced = self.nlg_generator.enhance_kg_response(response_text, spr_data)
            if len(enhanced) > len(response_text):
                response_text = enhanced
        
        # If document mode and we found relevant sections, append document context
        document_context = ""
        if document_sections:
            document_context = "\n\n📄 **From Document**:\n"
            for i, section in enumerate(document_sections[:3], 1):
                # Extract relevant excerpt (first 300 chars)
                excerpt = section["content"].strip()[:300]
                if len(section["content"]) > 300:
                    excerpt += "..."
                document_context += f"\n**{section['title']}**\n{excerpt}\n"
        
        if document_context:
            response_text += document_context
        
        # Add referenced components info
        if referenced_components:
            ref_info = "\n\n🔗 **Referenced Components**:\n"
            for comp in referenced_components:
                ref_info += f"  • {comp.ref_id} ({comp.component_type}): {comp.name}\n"
            response_text += ref_info
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        source = "knowledge_graph"
        if self.document_path:
            source = f"knowledge_graph+{Path(self.document_path).name}"
        if referenced_components:
            source += f"+refs:{len(referenced_components)}"
        
        return {
            "query": query,
            "response": response_text,
            "spr_id": spr_id,
            "spr_term": spr_term,
            "category": category,
            "confidence": confidence,
            "zepto_spr": zepto_spr,
            "blueprint": blueprint,
            "relationships": relationships,
            "execution_time_ms": execution_time,
            "source": source,
            "llm_bypassed": True,
            "autonomous": True,
            "document_sections": len(document_sections) if document_sections else 0,
            "referenced_components": [comp.ref_id for comp in referenced_components]
        }
    
    def get_real_world_answer(self, query: str, kg_answer: str) -> Optional[Dict[str, Any]]:
        """
        Get real-world answer using LLM or web search for comparison.
        
        Args:
            query: Original query
            kg_answer: Knowledge Graph answer
            
        Returns:
            Dictionary with real-world answer and metadata, or None if unavailable
        """
        start_time = time.time()
        
        # Try LLM first (more comprehensive)
        if LLM_TOOL_AVAILABLE:
            try:
                prompt = f"""Please provide a clear, concise explanation of: {query}

Focus on:
- Standard/accepted definition
- Key characteristics
- Real-world applications
- Current understanding in the field

Keep it factual and objective."""
                
                result = generate_text_llm({
                    "prompt": prompt,
                    "model": "gemini-2.0-flash-exp",
                    "temperature": 0.3,
                    "max_tokens": 500
                })
                
                if result and result.get("result"):
                    response_text = result["result"].get("response_text", "")
                    if response_text and response_text.strip():
                        return {
                            "answer": response_text.strip(),
                            "source": "llm",
                            "execution_time_ms": (time.time() - start_time) * 1000,
                            "method": "LLM (Gemini)"
                        }
                elif result and result.get("error"):
                    print(f"   ⚠️  LLM error: {result.get('error')}")
            except Exception as e:
                print(f"   ⚠️  LLM comparison failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to web search
        if WEB_SEARCH_AVAILABLE:
            try:
                search_result = search_web({
                    "query": query,
                    "num_results": 5
                })
                
                if search_result and search_result.get("result"):
                    results = search_result["result"].get("results", [])
                    if results:
                        # Synthesize top results into an answer
                        snippets = []
                        for r in results[:5]:
                            snippet = r.get("snippet", "") or r.get("description", "")
                            title = r.get("title", "")
                            if snippet:
                                if title:
                                    snippets.append(f"{title}: {snippet}")
                                else:
                                    snippets.append(snippet)
                        
                        if snippets:
                            # Combine snippets into coherent answer
                            synthesized = "\n\n".join(snippets[:3])  # Use top 3 snippets
                            
                            return {
                                "answer": synthesized,
                                "source": "web_search",
                                "execution_time_ms": (time.time() - start_time) * 1000,
                                "method": "Web Search",
                                "sources": [r.get("url", "") or r.get("link", "") for r in results[:5] if r.get("url") or r.get("link")]
                            }
            except Exception as e:
                print(f"   ⚠️  Web search comparison failed: {e}")
                import traceback
                traceback.print_exc()
        
        return None
    
    def compare_answers(self, kg_answer: str, real_world_answer: str) -> Dict[str, Any]:
        """
        Compare KG answer with real-world answer and identify differences/similarities.
        
        Args:
            kg_answer: Answer from Knowledge Graph
            real_world_answer: Answer from LLM/web search
            
        Returns:
            Comparison analysis with differences and similarities
        """
        # Extract key concepts from both answers
        kg_concepts = self._extract_concepts(kg_answer)
        rw_concepts = self._extract_concepts(real_world_answer)
        
        # Find common concepts
        common = set(kg_concepts) & set(rw_concepts)
        
        # Find KG-specific concepts
        kg_only = set(kg_concepts) - set(rw_concepts)
        
        # Find real-world-specific concepts
        rw_only = set(rw_concepts) - set(kg_concepts)
        
        # Calculate similarity score (simple word overlap)
        kg_words = set(kg_answer.lower().split())
        rw_words = set(real_world_answer.lower().split())
        word_overlap = len(kg_words & rw_words) / max(len(kg_words | rw_words), 1)
        
        return {
            "similarity_score": word_overlap,
            "common_concepts": list(common)[:10],
            "kg_only_concepts": list(kg_only)[:10],
            "rw_only_concepts": list(rw_only)[:10],
            "kg_length": len(kg_answer),
            "rw_length": len(real_world_answer)
        }
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts/terms from text."""
        # Simple extraction: capitalized words, technical terms
        concepts = []
        
        # Find capitalized words (likely concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        concepts.extend(capitalized)
        
        # Find technical terms (words with specific patterns)
        technical = re.findall(r'\b[a-z]+(?:ing|tion|ism|ology|ics)\b', text, re.IGNORECASE)
        concepts.extend(technical)
        
        # Remove duplicates and common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'this', 'that', 'these', 'those'}
        concepts = [c.lower() for c in concepts if c.lower() not in stop_words]
        
        return list(set(concepts))[:20]  # Return top 20 unique concepts
    
    def format_response(self, result: Dict[str, Any], show_details: bool = True, comparison: Optional[Dict[str, Any]] = None) -> str:
        """Format response for display, optionally with comparison."""
        lines = []
        
        if comparison and comparison.get("real_world_answer"):
            # Side-by-side comparison format
            lines.append("=" * 80)
            lines.append(f"📊 KNOWLEDGE COMPARISON: KG vs Real-World")
            lines.append("=" * 80)
            lines.append("")
            lines.append(f"Query: {result['query']}")
            lines.append("")
            
            # Show both answers in full (better for readability)
            lines.append("🔵 KNOWLEDGE GRAPH ANSWER:")
            lines.append("─" * 80)
            kg_text = result['response']
            # Wrap long lines for better display
            for line in kg_text.split('\n'):
                if len(line) > 78:
                    # Simple word wrap
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + word) > 78:
                            lines.append(current_line)
                            current_line = word + " "
                        else:
                            current_line += word + " "
                    if current_line:
                        lines.append(current_line)
                else:
                    lines.append(line)
            lines.append("─" * 80)
            lines.append("")
            
            lines.append("🌐 REAL-WORLD ANSWER:")
            lines.append("─" * 80)
            rw_text = comparison['real_world_answer']['answer']
            for line in rw_text.split('\n'):
                if len(line) > 78:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + word) > 78:
                            lines.append(current_line)
                            current_line = word + " "
                        else:
                            current_line += word + " "
                    if current_line:
                        lines.append(current_line)
                else:
                    lines.append(line)
            lines.append("─" * 80)
            lines.append("")
            
            # Comparison Analysis
            comp_analysis = comparison.get("comparison_analysis", {})
            similarity = comp_analysis.get("similarity_score", 0)
            
            lines.append("📊 COMPARISON ANALYSIS:")
            lines.append("-" * 80)
            lines.append(f"   Similarity Score: {similarity:.1%}")
            lines.append("")
            
            if comp_analysis.get("common_concepts"):
                lines.append(f"   ✅ Common Concepts ({len(comp_analysis['common_concepts'])}):")
                lines.append(f"      {', '.join(comp_analysis['common_concepts'][:8])}")
                lines.append("")
            
            if comp_analysis.get("kg_only_concepts"):
                lines.append(f"   🔵 KG-Only Concepts ({len(comp_analysis['kg_only_concepts'])}):")
                lines.append(f"      {', '.join(comp_analysis['kg_only_concepts'][:8])}")
                lines.append("")
            
            if comp_analysis.get("rw_only_concepts"):
                lines.append(f"   🌐 Real-World-Only Concepts ({len(comp_analysis['rw_only_concepts'])}):")
                lines.append(f"      {', '.join(comp_analysis['rw_only_concepts'][:8])}")
                lines.append("")
            
            # Metadata
            lines.append("📈 METADATA:")
            lines.append(f"   KG Answer: {result['execution_time_ms']:.2f}ms | {result['spr_id']}")
            lines.append(f"   Real-World: {comparison['real_world_answer']['execution_time_ms']:.2f}ms | {comparison['real_world_answer']['method']}")
            if comparison['real_world_answer'].get('sources'):
                lines.append(f"   Sources: {len(comparison['real_world_answer']['sources'])} URLs")
            lines.append("")
            
        else:
            # Standard format (no comparison)
            lines.append("=" * 80)
            lines.append(f"📚 KNOWLEDGE GRAPH RESPONSE")
            lines.append("=" * 80)
            lines.append("")
            lines.append(f"Query: {result['query']}")
            lines.append("")
            lines.append(f"✅ KG HIT: {result['spr_term']} ({result['spr_id']})")
            lines.append(f"   Confidence: {result['confidence']:.2f}")
            lines.append(f"   Category: {result['category']}")
            lines.append(f"   Execution Time: {result['execution_time_ms']:.2f}ms")
            lines.append(f"   Source: {result['source']} (NO LLM CALL)")
            lines.append("")
            
            if result.get('zepto_spr'):
                zepto_spr = result['zepto_spr']
                if self._is_real_zepto_spr(zepto_spr):
                    # Real Zepto-compressed SPR (short, symbolic)
                    lines.append(f"🔤 Zepto SPR: '{zepto_spr}'")
                else:
                    # Pseudo-compressed (long text) - indicate it's not actually compressed
                    if len(zepto_spr) > 100:
                        lines.append(f"⚠️  Zepto SPR (pseudo-compressed, {len(zepto_spr)} chars): '{zepto_spr[:100]}...'")
                    else:
                        lines.append(f"⚠️  Zepto SPR (pseudo-compressed): '{zepto_spr}'")
                    lines.append("   Note: This is not a true Zepto-compressed SPR (should be short symbolic form)")
                lines.append("")
            
            lines.append("📖 Response:")
            lines.append("-" * 80)
            lines.append(result['response'])
            lines.append("-" * 80)
            lines.append("")
        
        if show_details and not comparison:
            if result.get('blueprint'):
                lines.append("🔧 Blueprint Details:")
                lines.append(f"   {result['blueprint'][:200]}..." if len(result['blueprint']) > 200 else f"   {result['blueprint']}")
                lines.append("")
            
            if result.get('relationships'):
                lines.append("🔗 Relationships:")
                rel_keys = list(result['relationships'].keys())[:5]
                for key in rel_keys:
                    value = result['relationships'][key]
                    if isinstance(value, list):
                        lines.append(f"   {key}: {', '.join(str(v) for v in value[:3])}")
                    else:
                        lines.append(f"   {key}: {value}")
                lines.append("")
        
        if not comparison:
            lines.append("=" * 80)
            lines.append("✅ This answer came from ArchE's internal Knowledge Graph")
            lines.append("   • Zero LLM API costs")
            lines.append("   • <1ms latency")
            lines.append("   • Autonomous knowledge retrieval")
            lines.append("=" * 80)
        else:
            lines.append("=" * 80)
            lines.append("💡 Tip: Use --compare flag to compare with real-world understanding")
            lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """Main CLI loop."""
    parser = argparse.ArgumentParser(
        description="ArchE Knowledge Graph CLI - Query internal KG without LLM calls",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ask_kg_cli.py
  python3 ask_kg_cli.py --compare
  python3 ask_kg_cli.py --compare "What is Machine Learning?"
        """
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Enable real-world comparison (uses LLM/web search to compare with KG answer)'
    )
    parser.add_argument(
        '--document',
        '--doc',
        type=str,
        metavar='FILE',
        help='Query from a specific document (e.g., PRIME_ARCHE_PROTOCOL.md). Document content will be searched alongside Knowledge Graph.'
    )
    parser.add_argument(
        'query',
        nargs='?',
        help='Optional query to execute immediately (otherwise enters interactive mode)'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("ArchE Knowledge Graph CLI - Direct KG Queries")
    if args.compare:
        print("   Real-World Comparison: ENABLED")
    else:
        print("   (No LLM Calls - Pure KG Mode)")
    if args.document:
        print(f"   Document Mode: {args.document}")
    print("=" * 80)
    print()
    print("Ask questions about concepts from agi.txt (Mastermind_AI legacy knowledge)")
    if args.document:
        print(f"   Also querying from: {args.document}")
    print("Commands:")
    print("  'exit' or 'quit' - Exit the CLI")
    print("  'help' - Show example queries")
    if not args.compare:
        print("  Use --compare flag to enable real-world comparison")
    if not args.document:
        print("  Use --document FILE to query from a specific document")
    print()
    
    kg_cli = KGCli(enable_comparison=args.compare, document_path=args.document)
    
    # If query provided as argument, execute and exit
    if args.query:
        result = kg_cli.query_kg(args.query, min_confidence=0.3)
        if result:
            comparison = None
            if args.compare:
                print("🔍 Fetching real-world answer for comparison...")
                rw_answer = kg_cli.get_real_world_answer(args.query, result['response'])
                if rw_answer:
                    comp_analysis = kg_cli.compare_answers(result['response'], rw_answer['answer'])
                    comparison = {
                        "real_world_answer": rw_answer,
                        "comparison_analysis": comp_analysis
                    }
                else:
                    print("   ⚠️  Could not fetch real-world answer")
            
            print()
            print(kg_cli.format_response(result, comparison=comparison))
        else:
            print(f"\n❌ No match found in Knowledge Graph for: {args.query}")
        return
    
    # Interactive mode
    while True:
        try:
            query = input("\n🔍 Query: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'help':
                print("\n📚 Example queries:")
                print("   • What is System Architecture?")
                print("   • What is Machine Learning?")
                print("   • What is Cognitive Resonance?")
                print()
                print("🔗 Using @ References (like Cursor IDE):")
                print("   • @PRIME_ARCHE_PROTOCOL.md What are the 14 Mandates?")
                print("   • @SPRManager How does SPR detection work?")
                print("   • @CognitiveResonancE What is this concept?")
                print("   • @workflow_engine How does workflow execution work?")
                print()
                print("💡 Type '@' followed by a component name to reference it")
                print("   The system will automatically find and use the component")
                print()
                continue
            
            if query.lower().startswith('@list'):
                # List available components
                component_type = query.split()[1] if len(query.split()) > 1 else None
                if component_type:
                    components = kg_cli.self_ref_system.list_by_type(component_type)
                    print(f"\n📋 Components of type '{component_type}':")
                    for comp in components[:20]:
                        print(f"   {comp.ref_id} - {comp.name}")
                else:
                    stats = kg_cli.self_ref_system.get_statistics()
                    print(f"\n📊 Self-Reference System Statistics:")
                    print(f"   Total components: {stats['total_components']}")
                    print(f"   By type:")
                    for comp_type, count in stats['by_type'].items():
                        print(f"     • {comp_type}: {count}")
                print()
                continue
            
            if query.lower().startswith('@search'):
                # Search for components
                search_query = ' '.join(query.split()[1:]) if len(query.split()) > 1 else ""
                if search_query:
                    results = kg_cli.self_ref_system.search(search_query, limit=10)
                    print(f"\n🔍 Search results for '{search_query}':")
                    for comp in results:
                        print(f"   {comp.ref_id} ({comp.component_type}) - {comp.name}")
                        if comp.description:
                            print(f"      {comp.description[:100]}...")
                else:
                    print("\n❌ Please provide a search query: @search <query>")
                print()
                continue
            
            # Query Knowledge Graph
            result = kg_cli.query_kg(query, min_confidence=0.3)
            
            if not result:
                print("\n❌ No match found in Knowledge Graph")
                print("   (This concept is not in ArchE's internal knowledge base)")
                print("   Try asking about concepts from agi.txt or ResonantiA Protocol")
                continue
            
            # Get real-world comparison if enabled
            comparison = None
            if args.compare:
                print("🔍 Fetching real-world answer for comparison...")
                rw_answer = kg_cli.get_real_world_answer(query, result['response'])
                if rw_answer:
                    comp_analysis = kg_cli.compare_answers(result['response'], rw_answer['answer'])
                    comparison = {
                        "real_world_answer": rw_answer,
                        "comparison_analysis": comp_analysis
                    }
                else:
                    print("   ⚠️  Could not fetch real-world answer")
            
            # Display response
            print()
            print(kg_cli.format_response(result, comparison=comparison))
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

