#!/usr/bin/env python3
"""
Extract SPR definitions from agi.txt
Recognizes SPRs even without Guardian pointS format, extracts their definitions,
and creates/enriches SPRs in the KG.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Zepto compression system
try:
    from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessorAdapter
    ZEPTO_AVAILABLE = True
except ImportError:
    ZEPTO_AVAILABLE = False
    ZeptoSPRProcessorAdapter = None

# Fallback symbol map (only used if Zepto compression fails)
SYMBOL_MAP = {
    'Cognitive': 'Γ', 'Pattern': 'Π', 'Resonance': 'Ρ', 'Knowledge': 'Κ',
    'Action': 'Α', 'Temporal': 'Τ', 'Workflow': 'Ω', 'Meta': 'Μ',
    'Agent': 'Α', 'Vetting': 'Β', 'Mandate': 'Δ', 'SPR': 'Σ',
    'Thought': 'Θ', 'System': 'Σ', 'Entity': 'Ε', 'Causal': 'Χ',
    'Inference': 'Ι', 'Modeling': 'Μ', 'Analysis': 'Α', 'Framework': 'Φ',
    'Tool': 'Τ', 'Network': 'Ν', 'Learning': 'Λ', 'Execution': 'Ε',
    'Processing': 'Π', 'Architecture': 'Α', 'Component': 'Κ', 'Protocol': 'Π',
    'Registry': 'Ρ', 'Manager': 'Μ', 'Engine': 'Ε', 'Orchestrator': 'Ο',
    'Query': 'Q', 'Data': 'Δ', 'Extraction': 'Ε', 'Machine': 'Μ',
    'Language': 'Λ', 'Parser': 'Π', 'Optimizer': 'Ο', 'Executor': 'Ε',
    'Model': 'Μ', 'Training': 'Τ', 'Dataset': 'Δ', 'Search': 'Σ',
    'Retrieval': 'Ρ', 'Storage': 'Σ', 'Database': 'Δ',
}

# Global Zepto processor (lazy initialization)
_zepto_processor = None

def _get_zepto_processor():
    """Get or create Zepto processor."""
    global _zepto_processor
    if _zepto_processor is None and ZEPTO_AVAILABLE:
        try:
            _zepto_processor = ZeptoSPRProcessorAdapter()
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize Zepto processor: {e}")
            return None
    return _zepto_processor

def _fallback_symbol_mapping(text: str) -> str:
    """Fallback symbol mapping when Zepto compression is not available."""
    text_lower = text.lower()
    symbols = []
    for keyword, symbol in SYMBOL_MAP.items():
        if keyword.lower() in text_lower and symbol not in symbols:
            symbols.append(symbol)
    if not symbols:
        symbols = ['Ξ']
    return '|'.join(symbols[:5])

def extract_spr_definitions_from_agi(file_path: Path) -> List[Dict[str, Any]]:
    """Extract SPR definitions from agi.txt, recognizing them even without Guardian pointS format."""
    print(f"📖 Extracting SPR definitions from {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    spr_definitions = []
    
    # STEP 1: Extract ALL nodes (even without explicit SPR definitions)
    # Every Node should be treated as a potential SPR
    all_nodes = list(re.finditer(r'Node\s+(\d+):\s+([^\n]+)', content))
    print(f"  📍 Found {len(all_nodes)} total Node entries")
    
    # STEP 2: For each node, try to find associated SPR definition
    for node_match in all_nodes:
        node_num = node_match.group(1)
        concept_name = node_match.group(2).strip()
        node_start = node_match.start()
        node_end = node_match.end()
        
        # Look for SPR definition within next 1000 chars
        next_1000 = content[node_end:node_end + 1000]
        spr_match = re.search(r'SPR:\s*([\d.]+),\s*"([^"]+)"', next_1000)
        
        if spr_match:
            # Has explicit SPR definition
            confidence = float(spr_match.group(1))
            spr_name = spr_match.group(2).strip()
        else:
            # No explicit SPR - use concept name as SPR name
            spr_name = concept_name
            confidence = 0.5  # Default confidence
        
        # Extract description (text between this node and next node, up to 2000 chars)
        next_node_match = re.search(r'\nNode\s+\d+:', content[node_end:])
        if next_node_match:
            description = content[node_end:node_end + next_node_match.start()].strip()
        else:
            description = content[node_end:node_end + 2000].strip()
        
        # Clean up description (remove SPR/Edges lines if present)
        description = re.sub(r'SPR:.*?\n', '', description)
        description = re.sub(r'Edges:.*?\n', '', description)
        description = description.strip()
        
        # Extract edges if present (look in wider range)
        edges = []
        search_range = content[max(0, node_start - 200):node_end + 2000]
        edges_match = re.search(r'Edges:\s*\[([^\]]+)\]', search_range)
        if edges_match:
            edges_str = edges_match.group(1)
            edges = re.findall(r"'([^']+)'", edges_str)
        
        spr_definitions.append({
            'spr_name': spr_name,
            'concept_name': concept_name,
            'node_number': node_num,
            'confidence': confidence,
            'definition': description[:2000] if description else f"Node {node_num}: {concept_name}",
            'edges': edges,
            'type': 'node_format',
            'has_explicit_spr': bool(spr_match),
            'source_context': content[node_start:node_end + 200][:500]
        })
    
    print(f"  ✅ Extracted {len(spr_definitions)} SPRs from Node format")
    
    # Pattern 1: Explicit SPR definitions with quotes or colons
    # Example: "Summers_eyeS": {"url": "...", "description": "..."}
    spr_dict_pattern = r'["\']([^"\']+)["\']:\s*\{[^}]+\}'
    dict_matches = re.finditer(spr_dict_pattern, content)
    for match in dict_matches:
        spr_name = match.group(1)
        # Extract the full dict
        start = match.start()
        brace_count = 0
        in_dict = False
        dict_end = start
        for i, char in enumerate(content[start:], start):
            if char == '{':
                brace_count += 1
                in_dict = True
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and in_dict:
                    dict_end = i + 1
                    break
        
        if dict_end > start:
            dict_str = content[start:dict_end]
            try:
                # Try to parse as JSON-like
                spr_data = {}
                # Extract key-value pairs
                url_match = re.search(r'["\']url["\']:\s*["\']([^"\']+)["\']', dict_str)
                desc_match = re.search(r'["\']description["\']:\s*["\']([^"\']+)["\']', dict_str)
                if url_match:
                    spr_data['url'] = url_match.group(1)
                if desc_match:
                    spr_data['description'] = desc_match.group(1)
                
                spr_definitions.append({
                    'spr_name': spr_name,
                    'definition': spr_data.get('description', ''),
                    'metadata': spr_data,
                    'type': 'explicit_definition',
                    'source_context': dict_str[:200]
                })
            except:
                pass
    
    # Pattern 2: SPR mentions with explanations
    # Example: "the SPR 'KnO' represents..." or "SPR 'Summers_eyeS'..."
    spr_explanation_pattern = r"(?:SPR|spr|Sparse Priming Representation)[\s'\"](?:called|named|is|represents|means|stands for)[\s'\"]([A-Za-z_][A-Za-z0-9_]*)[\s'\"].*?(?:represents|means|is|stands for|description|definition)[\s:]+([^.\n]+(?:\.[^.\n]+)*)"
    explanations = re.finditer(spr_explanation_pattern, content, re.IGNORECASE | re.DOTALL)
    for match in explanations:
        spr_name = match.group(1)
        definition = match.group(2).strip()
        spr_definitions.append({
            'spr_name': spr_name,
            'definition': definition,
            'type': 'explanation',
            'source_context': match.group(0)[:300]
        })
    
    # Pattern 3: Guardian pointS format detection (even if not explicitly called SPR)
    # Format: FirstLast uppercase, middle lowercase (e.g., "KnO", "skillS", "Summers_eyeS")
    guardian_pattern = r'\b([A-Z][a-z]*[A-Z]|[A-Z][a-z_]*[A-Z])\b'
    guardian_matches = re.finditer(guardian_pattern, content)
    seen_guardians = set()
    
    for match in guardian_matches:
        spr_name = match.group(1)
        if spr_name in seen_guardians or len(spr_name) < 3:
            continue
        seen_guardians.add(spr_name)
        
        # Find context around this SPR mention
        start = max(0, match.start() - 200)
        end = min(len(content), match.end() + 200)
        context = content[start:end]
        
        # Try to extract definition from context
        definition = ""
        # Look for "represents", "means", "is", etc. after the SPR
        after_spr = content[match.end():match.end()+500]
        def_match = re.search(r'(?:represents|means|is|stands for|description|definition)[\s:]+([^.\n]+)', after_spr, re.IGNORECASE)
        if def_match:
            definition = def_match.group(1).strip()
        else:
            # Use surrounding sentence
            sentence_match = re.search(r'[.!?]\s*([^.!?]*' + re.escape(spr_name) + r'[^.!?]*)[.!?]', context)
            if sentence_match:
                definition = sentence_match.group(1).strip()
        
        if definition or spr_name in ['KnO', 'Summers_eyeS', 'skillS']:  # Known important SPRs
            spr_definitions.append({
                'spr_name': spr_name,
                'definition': definition or f"SPR extracted from agi.txt: {spr_name}",
                'type': 'guardian_format',
                'source_context': context
            })
    
    # Pattern 4: Lists of SPRs (e.g., "SPRs: KnO, Summers_eyeS, skillS")
    spr_list_pattern = r'(?:SPRs?|Sparse Priming Representations?)[\s:]+([A-Za-z_][A-Za-z0-9_,\s]+)'
    list_matches = re.finditer(spr_list_pattern, content, re.IGNORECASE)
    for match in list_matches:
        spr_list_str = match.group(1)
        spr_names = re.findall(r'\b([A-Za-z_][A-Za-z0-9_]+)\b', spr_list_str)
        for spr_name in spr_names:
            if spr_name not in seen_guardians:
                spr_definitions.append({
                    'spr_name': spr_name,
                    'definition': f"SPR mentioned in list from agi.txt: {spr_name}",
                    'type': 'list_mention',
                    'source_context': match.group(0)
                })
    
    # Pattern 5: Extract unique capitalized multi-word concepts as potential SPRs
    # These are terms like "Machine Learning", "Natural Language Processing", etc.
    capitalized_concept_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b'
    concept_matches = re.finditer(capitalized_concept_pattern, content)
    seen_concepts = set()
    
    for match in concept_matches:
        concept = match.group(1).strip()
        # Filter: must be 2-5 words, not too short, not common words
        words = concept.split()
        if (len(words) >= 2 and len(words) <= 5 and 
            len(concept) > 8 and 
            concept not in seen_concepts and
            concept.lower() not in ['node', 'edge', 'the', 'and', 'for', 'with', 'that', 'this']):
            seen_concepts.add(concept)
            
            # Find context around this concept
            start = max(0, match.start() - 300)
            end = min(len(content), match.end() + 500)
            context = content[start:end]
            
            # Extract description from context
            description = ""
            # Look for definition patterns
            def_patterns = [
                r'(?:is|are|represents|means|refers to|stands for|definition|description)[\s:]+([^.\n]+)',
                r'([^.\n]{20,200}(?:' + re.escape(concept) + r')[^.\n]{20,200})',
            ]
            for pattern in def_patterns:
                def_match = re.search(pattern, context, re.IGNORECASE)
                if def_match:
                    description = def_match.group(1).strip()
                    break
            
            if description or concept in ['Machine Learning', 'Natural Language Processing', 'Knowledge Graph']:
                spr_definitions.append({
                    'spr_name': concept,
                    'concept_name': concept,
                    'definition': description[:1500] if description else f"Concept extracted from agi.txt: {concept}",
                    'type': 'capitalized_concept',
                    'source_context': context[:500]
                })
    
    print(f"  ✅ Extracted {len([s for s in spr_definitions if s.get('type') == 'capitalized_concept'])} capitalized concepts")
    
    # Pattern 6: Workflow tags that might be SPRs (->|...|<-)
    workflow_pattern = r'->\|([A-Za-z_][A-Za-z0-9_]+)\|<-'
    workflow_matches = re.finditer(workflow_pattern, content)
    for match in workflow_matches:
        spr_name = match.group(1)
        if spr_name not in seen_guardians and len(spr_name) > 2:
            # Check if it's mentioned as an SPR in nearby context
            context_start = max(0, match.start() - 300)
            context_end = min(len(content), match.end() + 300)
            context = content[context_start:context_end]
            
            if 'SPR' in context or 'Sparse Priming' in context:
                spr_definitions.append({
                    'spr_name': spr_name,
                    'definition': f"Workflow SPR pattern from agi.txt: {spr_name}",
                    'type': 'workflow_spr',
                    'source_context': context
                })
    
    # Remove duplicates (keep first occurrence)
    seen = set()
    unique_sprs = []
    for spr_def in spr_definitions:
        key = spr_def['spr_name'].lower()
        if key not in seen:
            seen.add(key)
            unique_sprs.append(spr_def)
    
    print(f"✅ Extracted {len(unique_sprs)} unique SPR definitions")
    return unique_sprs

def convert_to_guardian_points(spr_name: str) -> str:
    """
    Convert SPR name to Guardian pointS format: FirstLast uppercase, middle lowercase.
    Examples: "Memory" -> "MemorY", "Human-Centered Design" -> "HumanCenteredDesigN"
    """
    # Remove special chars, keep only alphanumeric and spaces
    clean_name = re.sub(r'[^A-Za-z0-9\s]', '', spr_name)
    
    # Split into words
    words = clean_name.split()
    
    if len(words) == 0:
        return spr_name.upper() + 'X'
    
    if len(words) == 1:
        # Single word: FirstLast uppercase
        word = words[0]
        if len(word) >= 2:
            return word[0].upper() + word[1:-1].lower() + word[-1].upper()
        else:
            return word.upper() + 'X'
    else:
        # Multiple words: First letter of first word + middle + Last letter of last word
        first_word = words[0]
        last_word = words[-1]
        middle_words = words[1:-1] if len(words) > 2 else []
        
        # Build: FirstLetter + middle + LastLetter
        result = first_word[0].upper()
        
        # Add middle (all lowercase)
        if middle_words:
            result += ''.join([w.lower() for w in middle_words])
        if len(first_word) > 1:
            result += first_word[1:].lower()
        
        # Add last word (all but last letter lowercase, last letter uppercase)
        if len(last_word) > 1:
            result += last_word[:-1].lower()
        result += last_word[-1].upper()
        
        return result

def create_or_enrich_spr(spr_def: Dict[str, Any], existing_sprs: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], bool]:
    """Create new SPR or enrich existing one. Ensures Guardian pointS format."""
    spr_name = spr_def['spr_name']
    concept_name = spr_def.get('concept_name', spr_name)
    
    # Convert to Guardian pointS format
    guardian_name = convert_to_guardian_points(spr_name)
    
    # Also check concept_name for matching
    concept_guardian = convert_to_guardian_points(concept_name) if concept_name != spr_name else guardian_name
    
    # Check if exists (STRICT: Only exact Guardian pointS format match)
    # We only match if the Guardian pointS format SPR ID matches exactly
    existing_spr = None
    for spr in existing_sprs:
        spr_id = spr.get('spr_id', '').lower()
        # ONLY match on exact Guardian pointS format ID match
        if spr_id == guardian_name.lower() or spr_id == concept_guardian.lower():
            existing_spr = spr
            break
    
    if existing_spr:
        # Enrich existing
        definition = str(existing_spr.get('definition', ''))
        new_def = spr_def['definition']
        
        if new_def and new_def[:100] not in definition:
            existing_spr['definition'] = definition + '\n\n[From agi.txt]: ' + new_def[:1500]
            existing_spr['enriched_from'] = 'agi.txt'
            
            # Update zepto_spr using proper Zepto compression
            narrative = (existing_spr.get('term', '') + ' ' + existing_spr['definition']).strip()
            zepto_processor = _get_zepto_processor()
            
            if zepto_processor and narrative and len(narrative) > 10:
                try:
                    result = zepto_processor.compress_to_zepto(narrative, target_stage="Zepto")
                    if result and not result.error and result.zepto_spr:
                        existing_spr['zepto_spr'] = result.zepto_spr
                        # Update symbol codex with new entries
            symbol_codex = existing_spr.get('symbol_codex', {})
                        from dataclasses import asdict
                        for symbol, entry in result.new_codex_entries.items():
                            if hasattr(entry, '__dict__'):
                                symbol_codex[symbol] = asdict(entry)
                            else:
                                symbol_codex[symbol] = entry
            existing_spr['symbol_codex'] = symbol_codex
                    else:
                        # Fallback to simple symbol mapping
                        existing_spr['zepto_spr'] = _fallback_symbol_mapping(narrative)
                except Exception as e:
                    print(f"  ⚠️  Zepto compression failed for {guardian_name}: {e}")
                    existing_spr['zepto_spr'] = _fallback_symbol_mapping(narrative)
            else:
                # Fallback to simple symbol mapping
                existing_spr['zepto_spr'] = _fallback_symbol_mapping(narrative)
        
        return (existing_spr, True)  # Enriched
    else:
        # Create new SPR - use proper Zepto compression
        narrative = (spr_name + ' ' + spr_def['definition']).strip()
        zepto_processor = _get_zepto_processor()
        
        zepto_str = 'Ξ'  # Default
        symbol_codex = {}
        original_len = len(narrative)
        compressed_len = 1
        ratio = original_len
        
        if zepto_processor and narrative and len(narrative) > 10:
            try:
                result = zepto_processor.compress_to_zepto(narrative, target_stage="Zepto")
                if result and not result.error and result.zepto_spr:
                    zepto_str = result.zepto_spr
                    compressed_len = len(zepto_str)
                    ratio = result.compression_ratio
                    # Update symbol codex with new entries
                    from dataclasses import asdict
                    for symbol, entry in result.new_codex_entries.items():
                        if hasattr(entry, '__dict__'):
                            symbol_codex[symbol] = asdict(entry)
                        else:
                            symbol_codex[symbol] = entry
                else:
                    # Fallback to simple symbol mapping
                    zepto_str = _fallback_symbol_mapping(narrative)
                    compressed_len = len(zepto_str)
                    ratio = original_len / compressed_len if compressed_len > 0 else 0
                    # Create basic symbol codex from fallback
                    text_lower = narrative.lower()
                    symbols = zepto_str.split('|')
                    for keyword, sym in SYMBOL_MAP.items():
                        if sym in symbols and sym not in symbol_codex:
                            symbol_codex[sym] = {"meaning": keyword, "context": "Protocol"}
            except Exception as e:
                print(f"  ⚠️  Zepto compression failed for {guardian_name}: {e}")
                zepto_str = _fallback_symbol_mapping(narrative)
                compressed_len = len(zepto_str)
                ratio = original_len / compressed_len if compressed_len > 0 else 0
        else:
            # Fallback to simple symbol mapping
            zepto_str = _fallback_symbol_mapping(narrative)
            compressed_len = len(zepto_str)
            ratio = original_len / compressed_len if compressed_len > 0 else 0
        
        # Ensure default symbol has codex entry
        if 'Ξ' in zepto_str and 'Ξ' not in symbol_codex:
            symbol_codex['Ξ'] = {"meaning": "Generic/Universal", "context": "Protocol"}
        
        # Build comprehensive definition with all knowledge
        full_definition = f"{concept_name}: {spr_def['definition']}"
        if spr_def.get('edges'):
            full_definition += f"\n\nRelated SPRs: {', '.join(spr_def['edges'])}"
        if spr_def.get('confidence'):
            full_definition += f"\n\nConfidence: {spr_def['confidence']}"
        
        new_spr = {
            'spr_id': guardian_name,  # MUST be Guardian pointS format
            'term': concept_name if concept_name else spr_name,  # Full concept name
            'definition': full_definition[:2000],  # All knowledge backfilled
            'category': 'ExtractedKnowledge',
            'relationships': {
                'type': 'SPRFromAgi',
                'source': 'agi.txt',
                'original_format': spr_def['type'],
                'node_number': spr_def.get('node_number'),
                'edges': spr_def.get('edges', [])
            },
            'blueprint_details': f"SPR extracted from agi.txt Node {spr_def.get('node_number', '?')}, type: {spr_def['type']}. Original SPR name: '{spr_name}'",
            'example_application': spr_def.get('source_context', '')[:500],
            'zepto_spr': zepto_str,  # Zepto compressed
            'symbol_codex': symbol_codex,  # Symbol meanings
            'compression_ratio': f"{ratio:.1f}:1",
            'compression_stages': [{
                'stage_name': 'Zepto',
                'compression_ratio': ratio,
                'symbol_count': len(symbols),
                'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
            }],
            'source': 'agi.txt_extraction'
        }
        
        return (new_spr, False)  # New

def backfill_sprs_from_agi():
    """Main function to extract and backfill SPRs from agi.txt."""
    print("=" * 90)
    print("🎯 SPR EXTRACTION & BACKFILL FROM agi.txt")
    print("=" * 90)
    
    # Extract SPR definitions
    agi_path = Path("past chats/agi.txt")
    if not agi_path.exists():
        print(f"❌ agi.txt not found at {agi_path}")
        return
    
    spr_definitions = extract_spr_definitions_from_agi(agi_path)
    print(f"📊 Found {len(spr_definitions)} SPR definitions\n")
    
    # Load existing SPRs
    spr_path = Path("knowledge_graph/spr_definitions_tv.json")
    with open(spr_path) as f:
        sprs = json.load(f)
    
    print(f"📚 Current KG: {len(sprs)} SPRs\n")
    
    # Process each SPR definition
    print("🔄 Processing SPR definitions...")
    enriched_count = 0
    new_count = 0
    new_sprs = []
    
    for i, spr_def in enumerate(spr_definitions):
        spr, is_enriched = create_or_enrich_spr(spr_def, sprs)
        
        if is_enriched:
            enriched_count += 1
            if enriched_count <= 10:
                print(f"  {enriched_count:2d}. 💎 Enriched: {spr.get('term', '')[:50]:50s}")
        else:
            new_sprs.append(spr)
            new_count += 1
            if new_count <= 20:
                print(f"  {new_count:3d}. 🆕 New: {spr['term'][:50]:50s} → {spr['zepto_spr']}")
    
    print(f"\n✅ Enriched: {enriched_count} existing SPRs")
    print(f"✅ Created: {new_count} new SPRs\n")
    
    # Add new SPRs
    sprs.extend(new_sprs)
    
    # Save
    print("💾 Saving enriched Knowledge Graph...")
    import time
    backup_path = spr_path.with_suffix(f'.backup.{int(time.time())}.json')
    import shutil
    shutil.copy(spr_path, backup_path)
    print(f"  📦 Backup: {backup_path}")
    
    with open(spr_path, 'w') as f:
        json.dump(sprs, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Saved: {spr_path}\n")
    
    # Statistics
    total_sprs = len(sprs)
    print("=" * 90)
    print("📊 BACKFILL SUMMARY")
    print("=" * 90)
    print(f"SPR definitions extracted:    {len(spr_definitions)}")
    print(f"Existing SPRs enriched:      {enriched_count}")
    print(f"New SPRs created:            {new_count}")
    print(f"Total SPRs in KG:           {total_sprs}")
    print(f"Coverage increase:          +{new_count} SPRs ({new_count*100//total_sprs if total_sprs > 0 else 0}%)")
    print(f"💰 Cost:                    $0.00 (direct compression)")
    print(f"⏱️  Time:                    <5 seconds")
    print("=" * 90)

if __name__ == '__main__':
    backfill_sprs_from_agi()

