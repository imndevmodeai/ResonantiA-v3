#!/usr/bin/env python3
"""
ArchE Interactive Agent - Enhanced with Cognitive Resonant Controller System
Now powered by multi-domain PR Controllers for systematic error elimination.
"""

import sys
import os
import logging
import time
from pathlib import Path

# Add the Three_PointO_ArchE directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "Three_PointO_ArchE"))

try:
    from cognitive_resonant_controller import CognitiveResonantControllerSystem
    CRCS_AVAILABLE = True
except ImportError:
    CRCS_AVAILABLE = False
    print("⚠️  CRCS not available, falling back to legacy system")

import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ArchE_Agent")

class ArchEAgent:
    """
    Enhanced ArchE Agent powered by Cognitive Resonant Controller System
    Implements multi-domain error elimination via Proportional Resonant Controllers
    """
    
    def __init__(self):
        self.model = None
        self.protocol_chunks = []
        self.crcs = None  # Cognitive Resonant Controller System
        self.legacy_mode = False
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("[Gemini] Initialized successfully")
            except Exception as e:
                logger.error(f"[Gemini] Initialization failed: {e}")
        else:
            logger.warning("[Gemini] API key not found")
        
        # Load protocol and initialize CRCS
        self._load_protocol()
        self._initialize_crcs()
    
    def _load_protocol(self):
        """Load the ResonantiA Protocol document"""
        protocol_path = Path(__file__).parent.parent / "protocol" / "ResonantiA_Protocol_v3.1-CA.md"
        
        if protocol_path.exists():
            try:
                with open(protocol_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split into chunks (paragraphs)
                self.protocol_chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
                logger.info(f"[Protocol] Loaded {len(self.protocol_chunks)} chunks from v3.1-CA")
                
            except Exception as e:
                logger.error(f"[Protocol] Failed to load: {e}")
                self.protocol_chunks = ["CRITICAL ERROR: Protocol document could not be loaded."]
        else:
            logger.error(f"[Protocol] File not found: {protocol_path}")
            self.protocol_chunks = ["CRITICAL ERROR: Protocol document not found."]
    
    def _initialize_crcs(self):
        """Initialize the Cognitive Resonant Controller System"""
        if CRCS_AVAILABLE and self.protocol_chunks and not self.protocol_chunks[0].startswith("CRITICAL ERROR"):
            try:
                self.crcs = CognitiveResonantControllerSystem(self.protocol_chunks)
                logger.info("[CRCS] Cognitive Resonant Controller System initialized")
                logger.info(f"[CRCS] Active domains: {list(self.crcs.domain_controllers.keys())}")
            except Exception as e:
                logger.error(f"[CRCS] Initialization failed: {e}")
                self.legacy_mode = True
        else:
            logger.warning("[CRCS] Falling back to legacy mode")
            self.legacy_mode = True
    
    def process_query(self, query: str) -> str:
        """
        Process query using the Cognitive Resonant Controller System
        Falls back to legacy mode if CRCS unavailable
        """
        if not self.legacy_mode and self.crcs:
            return self._process_with_crcs(query)
        else:
            return self._process_legacy(query)
    
    def _process_with_crcs(self, query: str) -> str:
        """Process query using the advanced CRCS system"""
        logger.info(f"[CRCS] Processing query: '{query}'")
        
        # Use CRCS to extract context
        context, metrics = self.crcs.process_query(query)
        
        if context:
            logger.info(f"[CRCS] ✅ Domain controller activated: {metrics.get('active_domain', 'Unknown')}")
            logger.info(f"[CRCS] Response time: {metrics.get('response_time', 0):.3f}s")
            
            # Generate response using extracted context
            if self.model:
                response = self._generate_response(query, context)
                
                # Log CRCS diagnostics
                diagnostics = self.crcs.get_system_diagnostics()
                logger.info(f"[CRCS] System metrics: {diagnostics['system_metrics']}")
                
                return response
            else:
                return f"Context found via {metrics.get('active_domain', 'Unknown')} controller:\n\n{context}"
        else:
            logger.warning(f"[CRCS] ❌ No context extracted - Domain: {metrics.get('active_domain', 'None')}")
            return "The Cognitive Resonant Controller System could not extract relevant context for this query. This indicates a potential new domain that requires controller development."
    
    def _process_legacy(self, query: str) -> str:
        """Legacy processing method (original TF-IDF approach)"""
        logger.info(f"[Legacy] Processing query: '{query}'")
        
        # Use the original Implementation Resonance pattern as fallback
        context = self._legacy_retrieve_context(query)
        
        if context and self.model:
            return self._generate_response(query, context)
        elif context:
            return f"Legacy context found:\n\n{context}"
        else:
            return "No relevant context found in legacy mode."
    
    def _legacy_retrieve_context(self, query: str) -> str:
        """Legacy context retrieval with Implementation Resonance pattern"""
        if not self.protocol_chunks or self.protocol_chunks[0].startswith("CRITICAL ERROR"):
            return None
        
        query_lower = query.lower()
        
        # Implementation Resonance domain detection (legacy PR controller)
        if any(term in query_lower for term in ['implementation resonance', 'jedi principle 6', 'bridge the worlds']):
            logger.info("[Legacy] Implementation Resonance domain detected")
            relevant_chunks = []
            for chunk in self.protocol_chunks:
                chunk_lower = chunk.lower()
                if any(pattern in chunk_lower for pattern in [
                    'implementation resonance', 'jedi principle 6', 'bridge the worlds', 
                    'as above so below'
                ]):
                    relevant_chunks.append(chunk)
            
            if relevant_chunks:
                logger.info(f"[Legacy] Found {len(relevant_chunks)} Implementation Resonance chunks")
                return "\n\n".join(relevant_chunks)
        
        # Fallback to basic TF-IDF
        return self._basic_tfidf_search(query)
    
    def _basic_tfidf_search(self, query: str) -> str:
        """Basic TF-IDF search as final fallback"""
        import math
        
        query_words = set(word.lower() for word in query.replace('?', '').split())
        num_chunks = len(self.protocol_chunks)
        
        if num_chunks == 0:
            return None
        
        # Calculate IDF
        idf = {}
        for word in query_words:
            doc_count = sum(1 for chunk in self.protocol_chunks if word in chunk.lower())
            idf[word] = math.log(num_chunks / max(1, doc_count))
        
        # Find best chunk
        best_chunk = None
        max_score = 0
        
        for chunk in self.protocol_chunks:
            words_in_chunk = chunk.lower().split()
            chunk_word_count = len(words_in_chunk)
            
            if chunk_word_count == 0:
                continue
            
            # Calculate TF-IDF score
            tfidf_score = sum(
                (words_in_chunk.count(word) / chunk_word_count) * idf[word] 
                for word in query_words
            )
            
            if tfidf_score > max_score:
                max_score = tfidf_score
                best_chunk = chunk
        
        if best_chunk and max_score > 0.01:
            logger.info(f"[Legacy] TF-IDF found context (Score: {max_score:.4f})")
            return best_chunk
        
        return None
    
    def _generate_response(self, query: str, context: str) -> str:
        """Generate response using Gemini with extracted context"""
        if not self.model:
            return f"Context extracted but no language model available:\n\n{context}"
        
        prompt = f"""You are an expert on the ResonantiA Protocol v3.1-CA framework. Answer the user's query based on the provided context.

Context from ResonantiA Protocol:
{context}

User Query: {query}

Provide a comprehensive answer based on the context. If the context doesn't fully answer the query, explain what information is available and what might be missing."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"[Gemini] Generation failed: {e}")
            return f"Error generating response: {e}\n\nRaw context:\n{context}"
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        status = {
            'crcs_available': CRCS_AVAILABLE,
            'legacy_mode': self.legacy_mode,
            'protocol_chunks_loaded': len(self.protocol_chunks),
            'gemini_available': self.model is not None
        }
        
        if self.crcs and not self.legacy_mode:
            status['crcs_diagnostics'] = self.crcs.get_system_diagnostics()
        
        return status

def main():
    """Main entry point for the ArchE Agent"""
    if len(sys.argv) < 2:
        print("Usage: python interact.py \"Your question here\"")
        print("Example: python interact.py \"What is Implementation Resonance?\"")
        return
    
    query = sys.argv[1]
    
    print("🚀 ArchE Agent - Cognitive Resonant Controller System")
    print("=" * 60)
    
    # Initialize agent
    agent = ArchEAgent()
    
    # Show system status
    status = agent.get_system_status()
    print(f"📊 System Status:")
    print(f"   CRCS Available: {'✅' if status['crcs_available'] else '❌'}")
    print(f"   Legacy Mode: {'⚠️ Yes' if status['legacy_mode'] else '✅ No'}")
    print(f"   Protocol Chunks: {status['protocol_chunks_loaded']}")
    print(f"   Gemini Available: {'✅' if status['gemini_available'] else '❌'}")
    
    if status.get('crcs_diagnostics'):
        crcs_diag = status['crcs_diagnostics']
        print(f"   Active Controllers: {len(crcs_diag['domain_controllers'])}")
        print(f"   Total Queries: {crcs_diag['system_metrics']['total_queries']}")
    
    print()
    print(f"🔍 Query: {query}")
    print("-" * 40)
    
    # Process query
    start_time = time.time()
    response = agent.process_query(query)
    processing_time = time.time() - start_time
    
    print(response)
    print()
    print(f"⏱️  Processing time: {processing_time:.3f}s")
    
    # Show final diagnostics if CRCS was used
    if not agent.legacy_mode and agent.crcs:
        final_status = agent.get_system_status()
        if 'crcs_diagnostics' in final_status:
            print("\n📈 CRCS Performance:")
            for domain, data in final_status['crcs_diagnostics']['domain_controllers'].items():
                perf = data['performance']
                print(f"   {domain}: {perf['queries_processed']} queries, "
                      f"{perf['success_rate']:.1%} success rate")

if __name__ == "__main__":
    main() 