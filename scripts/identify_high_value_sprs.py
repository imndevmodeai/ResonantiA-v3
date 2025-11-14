#!/usr/bin/env python3
"""
Identify high-value SPRs for priority recompression to symbols.
"""

import json
from pathlib import Path

def identify_high_value_sprs():
    """Identify top 80 high-value SPRs for recompression."""
    
    # Load SPR definitions
    spr_path = Path("knowledge_graph/spr_definitions_tv.json")
    with open(spr_path, 'r') as f:
        spr_data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(spr_data, list):
        sprs = spr_data
    else:
        sprs = spr_data.get('sprs', [])
    
    # High-value keywords
    core_protocol = [
        'Cognitive', 'Pattern', 'Resonance', 'IAR', 'SPR', 'Thought',
        'Knowledge', 'Temporal', 'Mandate', 'Keyholder', 'ArchE', 'ResonantiA',
        'Metacognitive', 'Vetting', 'Workflow', 'Action', 'Entity'
    ]
    
    high_value_sprs = []
    
    print(f"📊 Total SPRs in KG: {len(sprs)}\n")
    
    for spr in sprs:
        spr_id = spr.get('spr_id', '')
        term = spr.get('term', '')
        category = spr.get('category', '')
        
        # Skip empty entries
        if not spr_id or not term:
            continue
        
        # Score each SPR
        score = 0
        reasons = []
        
        # Mandate SPRs (highest value)
        if 'Mandate' in term:
            score += 100
            reasons.append("Mandate")
        
        # Core protocol SPRs
        for keyword in core_protocol:
            if keyword in term:
                score += 40
                reasons.append("Core")
                break
        
        # Category-based scoring
        category_scores = {
            'Protocol Core': 40,
            'Meta-Cognition': 35,
            'Cognitive Framework': 35,
            'Analytical Technique': 30,
            'Knowledge Management': 30,
            'System Architecture': 25,
            'Workflow': 20,
            'Tool': 15,
        }
        
        for cat, cat_score in category_scores.items():
            if cat.lower() in category.lower():
                score += cat_score
                reasons.append(f"Cat")
                break
        
        # Blueprint details (indicates well-defined)
        if spr.get('blueprint_details'):
            score += 10
            reasons.append("BP")
        
        # Already has symbols (deprioritize)
        zepto = spr.get('zepto_spr', '')
        symbol_chars = ['Ω', 'Δ', 'Φ', 'Θ', 'Λ', 'Σ', 'Π', 'Æ', '‖Ψ⟩', '⊗', '⊕']
        has_symbols = any(sym in zepto for sym in symbol_chars)
        
        if has_symbols:
            score -= 100  # Already symbolized
            reasons.append("✓Sym")
        elif zepto and len(zepto) > 30:
            score -= 20  # Partial compression
            reasons.append("Part")
        else:
            reasons.append("→Need")
        
        if score > 0:
            high_value_sprs.append({
                'spr_id': spr_id,
                'term': term,
                'category': category,
                'score': score,
                'reasons': reasons,
                'has_symbols': has_symbols
            })
    
    # Sort by score (descending)
    high_value_sprs.sort(key=lambda x: x['score'], reverse=True)
    
    # Take top 80
    top_80 = high_value_sprs[:80]
    
    print(f"🎯 Top 80 High-Value SPRs for Priority Recompression:")
    print("=" * 110)
    
    for i, spr in enumerate(top_80, 1):
        status = "✓" if spr['has_symbols'] else "→"
        print(f"{i:2d}. [{status}] {spr['term']:50s} ({spr['category']:25s}) Sc:{spr['score']:3d}")
    
    # Save to file for batch processing
    output_file = Path("knowledge_graph/high_value_80_sprs.json")
    with open(output_file, 'w') as f:
        json.dump({
            'total_high_value': len(high_value_sprs),
            'top_80_selected': len(top_80),
            'sprs': [{'spr_id': s['spr_id'], 'term': s['term'], 'score': s['score']} for s in top_80]
        }, f, indent=2)
    
    print(f"\n✅ Saved top 80 SPRs to: knowledge_graph/high_value_80_sprs.json")
    
    # Statistics
    with_symbols = sum(1 for s in top_80 if s['has_symbols'])
    without_symbols = len(top_80) - with_symbols
    
    print(f"\n📊 Recompression Statistics:")
    print(f"  ✓ Already symbolized: {with_symbols:2d}/80")
    print(f"  → Need recompression: {without_symbols:2d}/80")
    print(f"  💰 Estimated cost:    ${without_symbols * 0.12:.2f}")
    print(f"  ⏱️  Expected time:     ~{without_symbols * 2}s (rate-limited by Groq)")
    print(f"  📈 Cost savings/year: ${without_symbols * 1200 / 100:.2f}")

if __name__ == '__main__':
    identify_high_value_sprs()
