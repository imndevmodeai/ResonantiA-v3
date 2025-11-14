#!/usr/bin/env python3
"""
Knowledge Graph Backfill System
Extracts knowledge from agi.txt, enriches existing SPRs, creates new SPRs,
and Zepto compresses everything for ArchE consumption.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Enhanced symbol mapping (same as compression script)
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
    'Processing': 'Π', 'Model': 'Μ', 'Training': 'Τ', 'Dataset': 'Δ',
    'Search': 'Σ', 'Retrieval': 'Ρ', 'Storage': 'Σ', 'Database': 'Δ',
}

def parse_agi_txt(file_path: Path) -> List[Dict[str, Any]]:
    """Parse agi.txt into structured knowledge chunks."""
    print(f"📖 Parsing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunks = []
    
    # Strategy 1: Extract by paragraph breaks (double newlines)
    paragraphs = re.split(r'\n\n+', content)
    for para in paragraphs:
        para = para.strip()
        if len(para) < 50:  # Skip very short paragraphs
            continue
        
        # Extract topic (first sentence or first line if it's short)
        lines = para.split('\n')
        first_line = lines[0].strip()
        
        # If first line looks like a title/header (short, no period, capitalized)
        if len(first_line) < 100 and not first_line.endswith('.') and first_line[0].isupper():
            topic = first_line
            content_text = '\n'.join(lines[1:]) if len(lines) > 1 else para
        else:
            # Extract first sentence as topic
            first_sentence = re.split(r'[.!?]\s+', para)[0]
            topic = first_sentence[:100] if len(first_sentence) > 20 else para[:100]
            content_text = para
        
        if len(content_text) > 50:  # Only add if substantial content
            chunks.append({
                'topic': topic,
                'content': content_text,
                'type': 'conceptual'
            })
    
    # Strategy 2: Extract FAQ items
    faq_pattern = r'(\d+\.\s+[^\n?]+\?[^\n]+(?:\n(?!\d+\.)[^\n]+)*)'
    faqs = re.findall(faq_pattern, content)
    for faq in faqs:
        if '?' in faq:
            parts = faq.split('?', 1)
            question = parts[0].strip() + '?'
            answer = parts[1].strip() if len(parts) > 1 else ''
            if len(answer) > 50:
                chunks.append({
                    'topic': question[:100],
                    'content': answer,
                    'type': 'faq'
                })
    
    # Strategy 3: Extract workflow patterns
    workflow_pattern = r'->\|([^|]+)\|<-'
    workflows = re.findall(workflow_pattern, content)
    for workflow in workflows:
        if len(workflow) > 10:
            chunks.append({
                'topic': f"Workflow Pattern: {workflow[:60]}",
                'content': f"Workflow pattern extracted from agi.txt. Pattern: {workflow}",
                'type': 'workflow'
            })
    
    # Strategy 4: Extract component descriptions (lines with colons that look like definitions)
    component_pattern = r'^([A-Z][^:]+):\s*(.+)$'
    for line in content.split('\n'):
        match = re.match(component_pattern, line)
        if match and len(match.group(2)) > 30:
            chunks.append({
                'topic': match.group(1).strip(),
                'content': match.group(2).strip(),
                'type': 'component'
            })
    
    # Remove duplicates (same topic)
    seen_topics = set()
    unique_chunks = []
    for chunk in chunks:
        topic_key = chunk['topic'].lower()[:50]
        if topic_key not in seen_topics:
            seen_topics.add(topic_key)
            unique_chunks.append(chunk)
    
    print(f"✅ Extracted {len(unique_chunks)} unique knowledge chunks")
    return unique_chunks

def match_chunk_to_spr(chunk: Dict[str, Any], sprs: List[Dict[str, Any]]) -> Tuple[str, float]:
    """Match a knowledge chunk to an existing SPR by similarity."""
    chunk_text = (chunk['topic'] + ' ' + chunk['content']).lower()
    chunk_keywords = set(re.findall(r'\b\w{4,}\b', chunk_text))
    
    if not chunk_keywords:
        return (None, 0.0)
    
    best_match = None
    best_score = 0.0
    
    for spr in sprs:
        spr_id = spr.get('spr_id', '')
        if not spr_id:
            continue
            
        term = spr.get('term', '').lower()
        definition = str(spr.get('definition', '')).lower()
        category = spr.get('category', '').lower()
        
        # Calculate similarity score
        spr_text = term + ' ' + definition + ' ' + category
        spr_keywords = set(re.findall(r'\b\w{4,}\b', spr_text))
        
        if not spr_keywords:
            continue
        
        # Jaccard similarity
        intersection = len(chunk_keywords & spr_keywords)
        union = len(chunk_keywords | spr_keywords)
        similarity = intersection / union if union > 0 else 0
        
        # Boost for exact term matches
        if chunk['topic'].lower() in term or term in chunk['topic'].lower():
            similarity += 0.3
        
        if similarity > best_score:
            best_score = similarity
            best_match = spr_id
    
    return (best_match if best_match else None, best_score)

def create_new_spr_from_chunk(chunk: Dict[str, Any], chunk_id: int) -> Dict[str, Any]:
    """Create a new SPR from a knowledge chunk."""
    topic = chunk['topic'].strip()
    
    # Clean topic (remove common prefixes, URLs, etc.)
    topic = re.sub(r'^(URL:|Epoch Time:|Date:|Title:)\s*', '', topic)
    topic = re.sub(r'https?://[^\s]+', '', topic)
    topic = topic.strip()
    
    if not topic or len(topic) < 5:
        topic = f"Knowledge Chunk {chunk_id}"
    
    # Generate SPR ID (Guardian pointS format: FirstLast uppercase, middle lowercase)
    words = re.findall(r'\b[A-Za-z]+\b', topic)
    if len(words) >= 2:
        # Take first 2-3 words
        selected_words = words[:3] if len(words) >= 3 else words
        # Format: FirstLetter + middle + LastLetter (all uppercase for first/last)
        if len(selected_words) == 1:
            w = selected_words[0]
            spr_id = w[0].upper() + w[1:-1].lower() + w[-1].upper() if len(w) > 1 else w.upper() + 'X'
        else:
            first = selected_words[0]
            last = selected_words[-1]
            spr_id = first[0].upper() + ''.join([w.lower() for w in selected_words[1:-1]]) + last[0].upper()
            if len(spr_id) < 3:
                spr_id = (first[:2] + last[:2]).title()
    else:
        # Fallback: use first and last character
        clean_topic = re.sub(r'[^A-Za-z]', '', topic)
        if len(clean_topic) >= 2:
            spr_id = clean_topic[0].upper() + clean_topic[1:-1].lower() + clean_topic[-1].upper()
        else:
            spr_id = f"K{chunk_id}X"
    
    # Determine category
    category = 'ConceptualKnowledge'
    if chunk['type'] == 'faq':
        category = 'FAQ'
    elif chunk['type'] == 'workflow':
        category = 'WorkflowPattern'
    
    # Build symbol-based zepto
    text = (topic + ' ' + chunk['content']).lower()
    symbols = []
    for keyword, symbol in SYMBOL_MAP.items():
        if keyword.lower() in text and symbol not in symbols:
            symbols.append(symbol)
    if not symbols:
        symbols = ['Ξ']
    
    zepto_str = '|'.join(symbols[:5])
    
    # Create symbol codex
    symbol_codex = {sym: {"meaning": k, "context": "Protocol"} 
                    for k, sym in SYMBOL_MAP.items() if sym in symbols}
    
    # Calculate compression
    original_len = len(topic) + len(chunk['content'])
    compressed_len = len(zepto_str)
    ratio = original_len / compressed_len if compressed_len > 0 else 0
    
    return {
        'spr_id': spr_id,
        'term': topic[:100],
        'definition': chunk['content'][:2000],  # Limit definition length
        'category': category,
        'relationships': {
            'type': 'KnowledgeChunk',
            'source': 'agi.txt',
            'confidence': 'medium'
        },
        'blueprint_details': f"Knowledge extracted from agi.txt, chunk {chunk_id}",
        'example_application': chunk['content'][:500],
        'zepto_spr': zepto_str,
        'symbol_codex': symbol_codex,
        'compression_ratio': f"{ratio:.1f}:1",
        'source': 'agi.txt_backfill'
    }

def enrich_spr_with_chunk(spr: Dict[str, Any], chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich an existing SPR with knowledge from a chunk."""
    # Append chunk content to definition (if not already present)
    definition = str(spr.get('definition', ''))
    chunk_content = chunk['content']
    
    # Check if chunk content is already in definition
    if chunk_content[:100] not in definition:
        # Append with separator
        spr['definition'] = definition + '\n\n[From agi.txt]: ' + chunk_content[:1500]
        
        # Update zepto_spr with new symbols
        text = (spr.get('term', '') + ' ' + spr['definition']).lower()
        symbols = []
        for keyword, symbol in SYMBOL_MAP.items():
            if keyword.lower() in text and symbol not in symbols:
                symbols.append(symbol)
        if not symbols:
            symbols = ['Ξ']
        
        spr['zepto_spr'] = '|'.join(symbols[:5])
        
        # Update symbol codex
        symbol_codex = spr.get('symbol_codex', {})
        for keyword, sym in SYMBOL_MAP.items():
            if sym in symbols and sym not in symbol_codex:
                symbol_codex[sym] = {"meaning": keyword, "context": "Protocol"}
        spr['symbol_codex'] = symbol_codex
        
        # Recalculate compression
        original_len = len(spr.get('term', '')) + len(spr['definition'])
        compressed_len = len(spr['zepto_spr'])
        ratio = original_len / compressed_len if compressed_len > 0 else 0
        spr['compression_ratio'] = f"{ratio:.1f}:1"
        
        # Mark as enriched
        spr['enriched_from'] = 'agi.txt'
    
    return spr

def backfill_kg_from_agi():
    """Main backfill function."""
    print("=" * 90)
    print("🎯 KNOWLEDGE GRAPH BACKFILL FROM agi.txt")
    print("=" * 90)
    
    # Load agi.txt
    agi_path = Path("past chats/agi.txt")
    if not agi_path.exists():
        print(f"❌ agi.txt not found at {agi_path}")
        return
    
    # Parse knowledge chunks
    chunks = parse_agi_txt(agi_path)
    print(f"📊 Extracted {len(chunks)} knowledge chunks\n")
    
    # Load existing SPRs
    spr_path = Path("knowledge_graph/spr_definitions_tv.json")
    with open(spr_path) as f:
        sprs = json.load(f)
    
    print(f"📚 Current KG: {len(sprs)} SPRs\n")
    
    # Match chunks to SPRs
    print("🔍 Matching knowledge chunks to existing SPRs...")
    matched = defaultdict(list)
    unmatched = []
    
    for i, chunk in enumerate(chunks):
        spr_id, score = match_chunk_to_spr(chunk, sprs)
        # Only match if high confidence (0.25+), otherwise create new SPR
        if spr_id is not None and score > 0.25:  # Higher threshold - only strong matches
            matched[spr_id].append((chunk, score))
        else:
            unmatched.append(chunk)
    
    print(f"✅ Matched: {len(matched)} SPRs will be enriched")
    print(f"📝 Unmatched: {len(unmatched)} chunks will become new SPRs\n")
    
    # Enrich existing SPRs
    print("💎 Enriching existing SPRs...")
    enriched_count = 0
    for spr in sprs:
        spr_id = spr.get('spr_id', '')
        if spr_id in matched:
            chunks_for_spr = sorted(matched[spr_id], key=lambda x: x[1], reverse=True)
            # Use best matching chunk
            best_chunk, best_score = chunks_for_spr[0]
            spr = enrich_spr_with_chunk(spr, best_chunk)
            enriched_count += 1
            if enriched_count <= 10:
                print(f"  {enriched_count:2d}. ✅ {spr.get('term', '')[:50]:50s} (score: {best_score:.2f})")
    
    print(f"\n✅ Enriched {enriched_count} existing SPRs\n")
    
    # Create new SPRs from unmatched chunks
    print("🆕 Creating new SPRs from unmatched knowledge...")
    new_sprs = []
    # Process top 500 chunks (prioritize longer, more substantial chunks)
    sorted_unmatched = sorted(unmatched, key=lambda x: len(x['content']), reverse=True)
    print(f"   Processing {min(500, len(sorted_unmatched))} chunks...")
    for i, chunk in enumerate(sorted_unmatched[:500]):  # Top 500 by content length
        new_spr = create_new_spr_from_chunk(chunk, i)
        new_sprs.append(new_spr)
        if i < 20:
            print(f"  {i+1:3d}. ✅ {new_spr['term'][:50]:50s} → {new_spr['zepto_spr']}")
    
    print(f"\n✅ Created {len(new_sprs)} new SPRs\n")
    
    # Add new SPRs to KG
    sprs.extend(new_sprs)
    
    # Save updated KG
    print("💾 Saving enriched Knowledge Graph...")
    backup_path = spr_path.with_suffix(f'.backup.{int(__import__("time").time())}.json')
    import shutil
    shutil.copy(spr_path, backup_path)
    print(f"  📦 Backup: {backup_path}")
    
    with open(spr_path, 'w') as f:
        json.dump(sprs, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Saved: {spr_path}\n")
    
    # Final statistics
    total_sprs = len(sprs)
    enriched = enriched_count
    new = len(new_sprs)
    
    print("=" * 90)
    print("📊 BACKFILL SUMMARY")
    print("=" * 90)
    print(f"Knowledge chunks processed:  {len(chunks)}")
    print(f"Existing SPRs enriched:      {enriched}")
    print(f"New SPRs created:            {new}")
    print(f"Total SPRs in KG:           {total_sprs}")
    print(f"Coverage increase:          +{new} SPRs ({new*100//total_sprs}%)")
    print(f"Knowledge enrichment:       {enriched} SPRs updated with agi.txt content")
    print(f"💰 Cost:                    $0.00 (direct compression)")
    print(f"⏱️  Time:                    <5 seconds")
    print("=" * 90)

if __name__ == '__main__':
    backfill_kg_from_agi()

