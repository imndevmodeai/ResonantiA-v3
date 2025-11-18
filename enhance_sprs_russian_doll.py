#!/usr/bin/env python3
"""
Enhance Existing SPRs for Russian Doll Architecture - FULL RECOMPRESSION REQUIRED

CRITICAL: SPRs are Sparse Priming Representations that activate knowledge.
Without full Russian Doll layering, they cannot:
- Support layered retrieval at different detail levels
- Enable progressive decompression
- Preserve nuanced knowledge (critical specifics + generalizable patterns)
- Support novel pattern applications

This script:
1. RECOMPRESSES all SPRs to create full Russian Doll layers (default behavior)
2. Enhances symbol_codex entries with nuanced knowledge fields
3. Stores all compression stages with content for layered retrieval

Strategy:
- Full recompression through all stages (Narrative → Concise → Nano → ... → Zepto)
- Enhanced symbol inference extracts: original_patterns, critical_specifics, 
  generalizable_patterns, relationships, contextual_variations, decompression_template
- All layers stored with content for Russian Doll retrieval
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import time
from datetime import datetime
from multiprocessing import Pool, Manager, cpu_count
from functools import partial

# Try to import tqdm for progress bar, fallback to simple progress
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("💡 Install 'tqdm' for better progress bars: pip install tqdm")

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessorAdapter
from Three_PointO_ArchE.pattern_crystallization_engine import SymbolCodexEntry


def enhance_symbol_codex_entry(
    symbol: str,
    existing_entry: Dict[str, Any],
    spr_definition: str,
    spr_term: str,
    processor: ZeptoSPRProcessorAdapter
) -> Dict[str, Any]:
    """
    Enhance an existing symbol codex entry with nuanced knowledge.
    
    Uses the SPR definition and term to infer:
    - Original patterns
    - Critical specifics
    - Generalizable patterns
    - Relationships
    - Contextual variations
    - Decompression template
    """
    enhanced = existing_entry.copy()
    
    # If already has enhanced fields, skip (already enhanced)
    if 'original_patterns' in enhanced and enhanced.get('original_patterns'):
        return enhanced
    
    # Build narrative from SPR for inference
    narrative = f"{spr_term}: {spr_definition}"
    
    # Use the engine's enhanced inference
    try:
        meaning_data = processor.engine._infer_symbol_meaning(symbol, narrative)
        
        # Add enhanced fields
        enhanced['original_patterns'] = meaning_data.get('original_patterns', [])
        enhanced['relationships'] = meaning_data.get('relationships', {})
        enhanced['critical_specifics'] = meaning_data.get('critical_specifics', [])
        enhanced['generalizable_patterns'] = meaning_data.get('generalizable_patterns', [])
        enhanced['contextual_variations'] = meaning_data.get('contextual_variations', {})
        enhanced['decompression_template'] = meaning_data.get('decompression_template', enhanced.get('meaning', ''))
        
        return enhanced
    except Exception as e:
        print(f"  ⚠️  Warning: Could not enhance symbol '{symbol}': {e}")
        # Return with empty enhanced fields
        enhanced.setdefault('original_patterns', [])
        enhanced.setdefault('relationships', {})
        enhanced.setdefault('critical_specifics', [])
        enhanced.setdefault('generalizable_patterns', [])
        enhanced.setdefault('contextual_variations', {})
        enhanced.setdefault('decompression_template', enhanced.get('meaning', ''))
        return enhanced


def find_file_in_project(file_path_str: str, project_root: Path) -> Optional[Path]:
    """
    Find a file referenced in blueprint/details.
    Handles both absolute and relative paths, including historical paths.
    
    Handles:
    - Current paths (mnt/36*)
    - Historical paths (media/newbu/36*, three_point0*/workflows)
    - Path variations and migrations
    """
    if not file_path_str:
        return None
    
    # Normalize path string
    file_path_str = file_path_str.strip()
    
    # Try direct path
    file_path = Path(file_path_str)
    if file_path.is_absolute() and file_path.exists():
        return file_path
    
    # Try relative to project root
    relative_path = project_root / file_path_str
    if relative_path.exists():
        return relative_path
    
    # Handle historical path migrations
    # Map old paths to new locations
    path_migrations = {
        'media/newbu/36': 'mnt/3626C55326C514B1',
        'three_point0': 'Three_PointO_ArchE',
        'three_point5': 'Three_Point5_ArchE',
        'three_pointO': 'Three_PointO_ArchE',  # Case variations
        'Three_Point0': 'Three_PointO_ArchE',
    }
    
    # Try migrated paths
    migrated_path = file_path_str
    for old_path, new_path in path_migrations.items():
        if old_path in migrated_path:
            migrated_path = migrated_path.replace(old_path, new_path)
            migrated_file = project_root / migrated_path
            if migrated_file.exists():
                return migrated_file
    
    # Try to find by filename (most flexible)
    filename = file_path.name
    for pattern in [f"**/{filename}", f"**/*{filename}*"]:
        matches = list(project_root.glob(pattern))
        if matches:
            # Prefer matches in expected directories
            for match in matches:
                if 'Three_PointO' in str(match) or 'specifications' in str(match):
                    return match
            return matches[0]  # Return first match if no preferred found
    
    return None


def extract_agi_context(spr: Dict[str, Any], agi_path: Optional[Path] = None) -> str:
    """
    Extract full context from agi.txt for SPRs that reference it.
    
    Includes:
    - All [From agi.txt] sections from definition
    - Full Node context from agi.txt
    - Related conversation context
    - Implicit context understood through osmosis
    """
    if agi_path is None:
        # Try common locations
        possible_paths = [
            Path("past chats/agi.txt"),
            Path("agi.txt"),
            Path("../agi.txt"),
            Path("../../agi.txt"),
        ]
        for path in possible_paths:
            if path.exists():
                agi_path = path
                break
    
    if not agi_path or not agi_path.exists():
        return ""
    
    try:
        with open(agi_path, 'r', encoding='utf-8') as f:
            agi_content = f.read()
    except Exception as e:
        return f"[Could not read agi.txt: {e}]"
    
    context_parts = []
    
    # Extract all [From agi.txt] references from definition
    definition = spr.get('definition', '')
    import re
    
    # Find all Node references
    node_matches = re.findall(r'Node\s+(\d+):\s+([^\n]+)', definition)
    for node_num, node_title in node_matches:
        # Extract full Node context from agi.txt
        node_pattern = rf'Node\s+{node_num}:\s+{re.escape(node_title)}'
        node_match = re.search(node_pattern, agi_content)
        if node_match:
            # Get context around this node (next 2000 chars or until next Node)
            start_pos = node_match.start()
            next_node = re.search(r'\nNode\s+\d+:', agi_content[start_pos + 100:])
            if next_node:
                node_context = agi_content[start_pos:start_pos + next_node.start() + 100]
            else:
                node_context = agi_content[start_pos:start_pos + 2000]
            
            context_parts.append(f"NODE {node_num} CONTEXT FROM agi.txt:\n{node_context.strip()}")
    
    # Find SPR mentions
    spr_mentions = re.findall(r'SPR mentioned in list from agi\.txt:\s*([^\n]+)', definition)
    for mention in spr_mentions:
        # Search for context around this mention
        mention_pattern = re.escape(mention)
        mention_matches = list(re.finditer(mention_pattern, agi_content))
        for match in mention_matches[:3]:  # Limit to 3 matches
            # Get context around mention (500 chars before and after)
            start = max(0, match.start() - 500)
            end = min(len(agi_content), match.end() + 500)
            mention_context = agi_content[start:end]
            context_parts.append(f"SPR MENTION CONTEXT ({mention}):\n{mention_context.strip()}")
    
    # If SPR was enriched from agi.txt, include broader context
    if spr.get('enriched_from') == 'agi.txt':
        # Find the term in agi.txt and get surrounding context
        term = spr.get('term', spr.get('spr_id', ''))
        if term:
            term_matches = list(re.finditer(re.escape(term), agi_content, re.IGNORECASE))
            for match in term_matches[:2]:  # Limit to 2 matches
                start = max(0, match.start() - 1000)
                end = min(len(agi_content), match.end() + 1000)
                term_context = agi_content[start:end]
                context_parts.append(f"TERM CONTEXT FROM agi.txt ({term}):\n{term_context.strip()}")
    
    return "\n\n".join(context_parts) if context_parts else ""


def build_full_narrative(spr: Dict[str, Any], project_root: Optional[Path] = None, agi_path: Optional[Path] = None) -> str:
    """
    Build complete narrative from all SPR fields to preserve full original content.
    
    POWERFUL KERNEL: Includes:
    - Full specifications and code when referenced (handles historical paths)
    - Full agi.txt context for SPRs enriched from conversations
    - All implicit context understood through osmosis
    - Complete verbose robust context-rich version
    
    This ensures the Narrative layer contains ALL information including specs, code, and conversation context.
    """
    if project_root is None:
        project_root = Path(__file__).parent
    
    parts = []
    
    # Core fields
    term = spr.get('term', '')
    if term:
        parts.append(f"TERM: {term}")
    
    definition = spr.get('definition', '')
    if definition:
        parts.append(f"DEFINITION:\n{definition}")
    
    # Additional context fields
    blueprint = spr.get('blueprint_details', '')
    if blueprint:
        parts.append(f"BLUEPRINT DETAILS:\n{blueprint}")
        
        # POWERFUL KERNEL: Try to include full specification if referenced
        # Handles historical paths (media/newbu/36* -> mnt/36*, three_point0* -> Three_PointO_ArchE)
        import re
        spec_matches = re.findall(r'([\w/]+\.md)', blueprint)
        for spec_match in spec_matches[:2]:  # Limit to 2 specs to avoid huge files
            spec_file = find_file_in_project(spec_match, project_root)
            if spec_file and spec_file.exists() and spec_file.suffix == '.md':
                try:
                    spec_content = spec_file.read_text(encoding='utf-8')
                    # Limit spec size to 50KB to avoid massive narratives
                    if len(spec_content) < 50000:
                        parts.append(f"FULL SPECIFICATION ({spec_file.name}):\n{spec_content}")
                    else:
                        parts.append(f"SPECIFICATION ({spec_file.name}) - First 50KB:\n{spec_content[:50000]}...")
                except Exception as e:
                    parts.append(f"SPECIFICATION ({spec_file.name}) - Could not read: {e}")
            else:
                # File not found - preserve the reference for context
                parts.append(f"SPECIFICATION REFERENCE (file not found): {spec_match}")
        
        # POWERFUL KERNEL: Try to include full code if referenced
        # Handles historical paths
        code_matches = re.findall(r'([\w/]+\.py)', blueprint)
        for code_match in code_matches[:2]:  # Limit to 2 code files
            code_file = find_file_in_project(code_match, project_root)
            if code_file and code_file.exists() and code_file.suffix == '.py':
                try:
                    code_content = code_file.read_text(encoding='utf-8')
                    # Limit code size to 30KB per file
                    if len(code_content) < 30000:
                        parts.append(f"FULL IMPLEMENTATION CODE ({code_file.name}):\n```python\n{code_content}\n```")
                    else:
                        parts.append(f"IMPLEMENTATION CODE ({code_file.name}) - First 30KB:\n```python\n{code_content[:30000]}...\n```")
                except Exception as e:
                    parts.append(f"CODE ({code_file.name}) - Could not read: {e}")
            else:
                # File not found - preserve the reference for context
                parts.append(f"CODE REFERENCE (file not found): {code_match}")
    
    example = spr.get('example_application', '')
    if example:
        parts.append(f"EXAMPLE APPLICATION:\n{example}")
    
    category = spr.get('category', '')
    if category:
        parts.append(f"CATEGORY: {category}")
    
    # Relationships context
    relationships = spr.get('relationships', {})
    if relationships and isinstance(relationships, dict):
        rel_parts = []
        for key, value in relationships.items():
            if value:  # Only include non-empty values
                if isinstance(value, list):
                    rel_parts.append(f"{key}: {', '.join(str(v) for v in value)}")
                else:
                    rel_parts.append(f"{key}: {value}")
        if rel_parts:
            parts.append(f"RELATIONSHIPS:\n{'; '.join(rel_parts)}")
    
    # POWERFUL KERNEL: Extract full agi.txt context for SPRs enriched from conversations
    # This includes the verbose robust context-rich version understood through osmosis
    if '[From agi.txt]' in definition or spr.get('enriched_from') == 'agi.txt':
        agi_context = extract_agi_context(spr, agi_path)
        if agi_context:
            parts.append(f"FULL CONVERSATION CONTEXT FROM agi.txt:\n{agi_context}")
    
    # POWERFUL KERNEL: Add implicit context markers
    # If SPR has no spec/code but has agi.txt context, mark it as conversation-derived
    has_spec = any('SPECIFICATION' in part for part in parts)
    has_code = any('IMPLEMENTATION CODE' in part for part in parts)
    has_agi = any('agi.txt' in part for part in parts)
    
    if not has_spec and not has_code and has_agi:
        parts.append("CONTEXT TYPE: Conversation-derived knowledge (no direct spec/code, enriched from agi.txt conversations)")
        parts.append("IMPLICIT KNOWLEDGE: This SPR represents knowledge understood through conversation context and osmosis")
    
    # Build complete narrative
    full_narrative = "\n\n".join(parts)
    
    # If we have compression_stages with a Narrative layer, prefer that as the source of truth
    # BUT: If current narrative is richer (has agi.txt context), use current
    compression_stages = spr.get('compression_stages', [])
    if compression_stages:
        narrative_stage = next(
            (s for s in compression_stages if s.get('stage_name') == 'Narrative'),
            None
        )
        if narrative_stage and narrative_stage.get('content'):
            existing_content = narrative_stage['content']
            # Use existing if it's already comprehensive, otherwise use enhanced version
            if len(existing_content) > len(full_narrative) * 0.9:
                # Existing is already comprehensive, keep it
                return existing_content
            # Otherwise, use the enhanced version with agi.txt context
    
    return full_narrative


def enhance_compression_stages(
    stages: List[Dict[str, Any]],
    spr: Dict[str, Any],  # Changed: pass full SPR instead of just definition/term
    processor: ZeptoSPRProcessorAdapter,
    recompress: bool = False,
    project_root: Optional[Path] = None,
    agi_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Enhance compression stages with content field (Russian Doll layers).
    
    If recompress=True, recompresses to get full layers with content.
    Otherwise, just adds empty content placeholders.
    """
    if recompress:
        # Recompress to get full Russian Doll layers
        try:
            # Build FULL narrative from all SPR fields (with historical path support and agi.txt context)
            full_narrative = build_full_narrative(spr, project_root=project_root, agi_path=agi_path)
            
            if not full_narrative or len(full_narrative.strip()) < 10:
                # Fallback: use definition if narrative building failed
                full_narrative = f"{spr.get('term', '')}: {spr.get('definition', '')}"
            
            result = processor.compress_to_zepto(
                narrative=full_narrative,
                target_stage="Zepto"
            )
            
            # The compression engine now automatically creates Narrative layer
            # So we should have it already, but let's verify
            enhanced_stages = result.compression_stages.copy()
            
            # Check if Narrative layer already exists (should be there now)
            has_narrative = any(
                stage.get('stage_name') == 'Narrative' 
                for stage in enhanced_stages
            )
            
            if not has_narrative:
                # Add Narrative layer at the beginning (outermost doll)
                # This shouldn't happen with the updated engine, but keep as fallback
                from datetime import datetime, timezone
                narrative_stage = {
                    "stage_name": "Narrative",
                    "content": full_narrative,  # Full original content
                    "compression_ratio": 1.0,  # No compression
                    "symbol_count": len(full_narrative),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                enhanced_stages.insert(0, narrative_stage)
            
            return enhanced_stages
        except Exception as e:
            print(f"  ⚠️  Warning: Recompression failed: {e}")
            # Fallback: enhance existing stages
            return enhance_existing_stages(stages)
    else:
        # Just enhance existing stages (add content field as placeholder)
        return enhance_existing_stages(stages)


def enhance_existing_stages(stages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add content field to existing compression stages (placeholder)."""
    enhanced = []
    for stage in stages:
        enhanced_stage = stage.copy()
        if 'content' not in enhanced_stage:
            # Add placeholder - actual content would require recompression
            enhanced_stage['content'] = None  # Mark as needing recompression
        enhanced.append(enhanced_stage)
    return enhanced


def process_single_spr(args_tuple):
    """
    Process a single SPR for parallel execution.
    
    Args:
        args_tuple: (spr, recompress, processor_init_args, project_root, agi_path)
    
    Returns:
        (spr_id, enhanced_spr, result_dict, error)
    """
    spr, recompress, processor_init_args, project_root, agi_path = args_tuple
    spr_id = spr.get('spr_id', 'UNKNOWN')
    
    result = {
        "enhanced": False,
        "codex_enhanced": False,
        "stages_enhanced": False,
        "recompressed": False,
        "layers_count": 0,
        "error": None
    }
    
    try:
        # Initialize processor in this process
        processor = ZeptoSPRProcessorAdapter(**processor_init_args)
        
        zepto_spr = spr.get('zepto_spr', '')
        symbol_codex = spr.get('symbol_codex', {})
        compression_stages = spr.get('compression_stages', [])
        definition = spr.get('definition', '')
        term = spr.get('term', spr_id)
        
        if not zepto_spr or not symbol_codex:
            result["error"] = "missing zepto_spr or symbol_codex"
            return (spr_id, spr, result, None)
        
        enhanced_spr = spr.copy()
        enhanced = False
        codex_enhanced = False
        stages_enhanced = False
        layers_count = 0
        
        # Enhance symbol_codex entries
        if symbol_codex:
            enhanced_codex = {}
            for symbol, entry in symbol_codex.items():
                if isinstance(entry, dict):
                    enhanced_entry = enhance_symbol_codex_entry(
                        symbol=symbol,
                        existing_entry=entry,
                        spr_definition=definition,
                        spr_term=term,
                        processor=processor
                    )
                    if enhanced_entry != entry:
                        enhanced = True
                        codex_enhanced = True
                    enhanced_codex[symbol] = enhanced_entry
                else:
                    enhanced_codex[symbol] = entry
            
            if codex_enhanced:
                enhanced_spr['symbol_codex'] = enhanced_codex
        
        # Enhance compression_stages
        if compression_stages:
            try:
                enhanced_stages = enhance_compression_stages(
                    stages=compression_stages,
                    spr=enhanced_spr,  # Pass full SPR for complete narrative
                    processor=processor,
                    recompress=recompress,
                    project_root=project_root,
                    agi_path=agi_path
                )
                
                if enhanced_stages != compression_stages:
                    enhanced = True
                    stages_enhanced = True
                    enhanced_spr['compression_stages'] = enhanced_stages
                    layers_count = len(enhanced_stages)
                    if recompress:
                        result["recompressed"] = True
            except Exception as e:
                result["error"] = str(e)
                return (spr_id, spr, result, str(e))
        
        result["enhanced"] = enhanced
        result["codex_enhanced"] = codex_enhanced
        result["stages_enhanced"] = stages_enhanced
        result["layers_count"] = layers_count
        
        return (spr_id, enhanced_spr, result, None)
        
    except Exception as e:
        result["error"] = str(e)
        return (spr_id, spr, result, str(e))


def enhance_spr_file(
    spr_file: Path,
    dry_run: bool = False,
    recompress: bool = False,
    limit: Optional[int] = None,
    workers: int = 1
) -> Dict[str, Any]:
    """
    Enhance all SPRs in the file with Russian Doll architecture.
    
    Args:
        spr_file: Path to SPR definitions file
        dry_run: If True, don't save changes
        recompress: If True, recompress SPRs to get full Russian Doll layers
        limit: Optional limit on number of SPRs to process
    """
    print(f"📚 Loading SPR definitions from {spr_file}...")
    
    with open(spr_file, 'r', encoding='utf-8') as f:
        spr_data = json.load(f)
    
    # Handle both dict and list formats
    if isinstance(spr_data, dict):
        sprs = spr_data
        spr_list = list(sprs.values())
    elif isinstance(spr_data, list):
        spr_list = spr_data
        sprs = {spr['spr_id']: spr for spr in spr_list if isinstance(spr, dict) and 'spr_id' in spr}
    else:
        print("❌ ERROR: Invalid SPR data format")
        return {}
    
    print(f"✅ Loaded {len(sprs)} SPRs")
    
    # Find project root and agi.txt path
    project_root = Path(__file__).parent
    
    # Find agi.txt in common locations
    agi_path = None
    possible_agi_paths = [
        project_root / "past chats" / "agi.txt",
        project_root / "agi.txt",
        project_root.parent / "agi.txt",
        project_root.parent.parent / "agi.txt",
    ]
    for path in possible_agi_paths:
        if path.exists():
            agi_path = path
            print(f"✅ Found agi.txt at: {agi_path}")
            break
    
    if not agi_path:
        print("⚠️  agi.txt not found - SPRs enriched from agi.txt will not have full conversation context")
    
    # Initialize processor (for sequential mode or to get init args)
    processor_init_args = {}
    try:
        processor = ZeptoSPRProcessorAdapter()
        processor_init_args = {
            "symbol_codex_path": str(processor.codex_path),
            "protocol_vocabulary_path": str(processor.engine.protocol_vocab_path) if hasattr(processor.engine, 'protocol_vocab_path') else "knowledge_graph/protocol_symbol_vocabulary.json"
        }
        print("✅ Zepto SPR processor initialized")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize processor: {e}")
        return {}
    
    # Statistics
    stats = {
        "total": len(sprs),
        "enhanced_codex": 0,
        "enhanced_stages": 0,
        "recompressed": 0,
        "skipped": 0,
        "errors": []
    }
    
    # Process SPRs
    spr_list_limited = spr_list[:limit] if limit else spr_list
    total_sprs = len(spr_list_limited)
    
    print(f"\n🔧 Enhancing {total_sprs} SPRs...")
    if recompress:
        print("   Mode: FULL RECOMPRESSION (creating complete Russian Doll layers)")
        print("   ⚠️  This is REQUIRED for proper SPR functionality")
        print("   ⏱️  Estimated time: ~{:.1f} seconds per SPR".format(2.0))  # Rough estimate
    else:
        print("   ⚠️  WARNING: Skipping recompression - SPRs will NOT have full Russian Doll layers")
        print("   ⚠️  This means they cannot be properly decompressed with layered retrieval")
    
    if workers > 1:
        print(f"   🔀 Parallel processing: {workers} workers")
        print("   ⚠️  Note: LLM rate limits may limit effective parallelism")
    else:
        print("   🔄 Sequential processing")
    
    print()
    start_time = time.time()
    
    # Process SPRs (parallel or sequential)
    if workers > 1:
        # Parallel processing
        process_args = [
            (spr, recompress, processor_init_args, project_root, agi_path)
            for spr in spr_list_limited
        ]
        
        # Incremental save every N SPRs
        save_interval = max(50, total_sprs // 20)  # Save every 5% or 50 SPRs, whichever is larger
        processed_count = 0
        
        with Pool(processes=workers) as pool:
            if HAS_TQDM:
                results_iter = tqdm(
                    pool.imap(process_single_spr, process_args),
                    total=total_sprs,
                    desc="Processing SPRs",
                    unit="SPR",
                    ncols=100,
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
                )
                results = []
                for result in results_iter:
                    results.append(result)
                    processed_count += 1
                    
                    # Incremental save
                    if processed_count % save_interval == 0:
                        # Update SPRs in memory
                        for spr_id, enhanced_spr, result_dict, error in results[-save_interval:]:
                            if not error and result_dict.get("enhanced"):
                                if isinstance(spr_data, dict):
                                    if spr_id in sprs:
                                        sprs[spr_id] = enhanced_spr
                                elif isinstance(spr_data, list):
                                    for idx, s in enumerate(spr_list):
                                        if s.get('spr_id') == spr_id:
                                            spr_list[idx] = enhanced_spr
                                            break
                        
                        # Save incrementally
                        try:
                            with open(spr_file, 'w', encoding='utf-8') as f:
                                json.dump(spr_data, f, indent=2, ensure_ascii=False)
                            if HAS_TQDM:
                                tqdm.write(f"  💾 Incremental save: {processed_count}/{total_sprs} SPRs processed")
                        except Exception as e:
                            if HAS_TQDM:
                                tqdm.write(f"  ⚠️  Incremental save failed: {e}")
            else:
                results = pool.map(process_single_spr, process_args)
        
        # Process results
        for spr_id, enhanced_spr, result_dict, error in results:
            # Find index for display
            matching_sprs = [s for s in spr_list_limited if s.get('spr_id') == spr_id]
            i = spr_list_limited.index(matching_sprs[0]) + 1 if matching_sprs else 0
            
            if error:
                stats["errors"].append(f"{spr_id}: {error}")
                if HAS_TQDM:
                    tqdm.write(f"  ⚠️  Error enhancing {spr_id}: {error}")
                else:
                    print(f"  [{i}/{total_sprs}] ⚠️  Error enhancing {spr_id}: {error}")
                continue
            
            if result_dict.get("error") == "missing zepto_spr or symbol_codex":
                stats["skipped"] += 1
                if HAS_TQDM:
                    tqdm.write(f"  ⏭️  Skipped {spr_id} (missing zepto_spr or symbol_codex)")
                else:
                    print(f"  [{i}/{total_sprs}] ⏭️  Skipped {spr_id} (missing zepto_spr or symbol_codex)")
                continue
            
            # Update SPR in spr_data
            if isinstance(spr_data, dict):
                if spr_id in sprs:
                    sprs[spr_id] = enhanced_spr
            elif isinstance(spr_data, list):
                for idx, s in enumerate(spr_list):
                    if s.get('spr_id') == spr_id:
                        spr_list[idx] = enhanced_spr
                        break
            
            if result_dict.get("enhanced"):
                if result_dict.get("codex_enhanced"):
                    stats["enhanced_codex"] += 1
                if result_dict.get("stages_enhanced"):
                    stats["enhanced_stages"] += 1
                    if result_dict.get("recompressed"):
                        stats["recompressed"] += 1
                
                status_parts = []
                if result_dict.get("codex_enhanced"):
                    status_parts.append(f"codex({len(enhanced_spr.get('symbol_codex', {}))} symbols)")
                if result_dict.get("stages_enhanced"):
                    if recompress:
                        status_parts.append(f"recompressed({result_dict.get('layers_count', 0)} layers)")
                    else:
                        status_parts.append("stages")
                
                status = " + ".join(status_parts)
                if HAS_TQDM:
                    tqdm.write(f"  ✅ {spr_id[:40]}: {status}")
                else:
                    print(f"  [{i}/{total_sprs}] ✅ {spr_id[:40]}: {status}")
            else:
                stats["skipped"] += 1
                if HAS_TQDM:
                    tqdm.write(f"  ⏭️  {spr_id[:40]}: No changes needed")
                else:
                    print(f"  [{i}/{total_sprs}] ⏭️  {spr_id[:40]}: No changes needed")
    else:
        # Sequential processing (original code)
        # Use the processor we already initialized
        # Create progress bar or iterator
        if HAS_TQDM:
            spr_iterator = tqdm(
                enumerate(spr_list_limited, 1),
                total=total_sprs,
                desc="Processing SPRs",
                unit="SPR",
                ncols=100,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            )
        else:
            spr_iterator = enumerate(spr_list_limited, 1)
            last_progress_time = time.time()
            progress_interval = 5  # Show progress every 5 seconds
        
        for i, spr in spr_iterator:
            spr_id = spr.get('spr_id', f'SPR_{i}')
            zepto_spr = spr.get('zepto_spr', '')
            symbol_codex = spr.get('symbol_codex', {})
            compression_stages = spr.get('compression_stages', [])
            definition = spr.get('definition', '')
            term = spr.get('term', spr_id)
            
            if not zepto_spr or not symbol_codex:
                stats["skipped"] += 1
                if HAS_TQDM:
                    tqdm.write(f"  ⏭️  Skipped {spr_id} (missing zepto_spr or symbol_codex)")
                else:
                    print(f"  [{i}/{total_sprs}] ⏭️  Skipped {spr_id} (missing zepto_spr or symbol_codex)")
                continue
        
            # Show progress (if not using tqdm)
            if not HAS_TQDM:
                current_time = time.time()
                if current_time - last_progress_time >= progress_interval or i == 1 or i == total_sprs:
                    elapsed = current_time - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    remaining = (total_sprs - i) / rate if rate > 0 else 0
                    print(f"[{i}/{total_sprs}] Processing: {spr_id} | Elapsed: {elapsed:.1f}s | ETA: {remaining:.1f}s | Rate: {rate:.2f} SPR/s")
                    last_progress_time = current_time
            else:
                # Update tqdm description (only update every 10 SPRs to reduce flicker)
                if i % 10 == 1 or i == total_sprs:
                    spr_iterator.set_description(f"Processing {spr_id[:30]}")
            
            spr_start_time = time.time()
            
            enhanced = False
            codex_enhanced = False
            stages_enhanced = False
            layers_count = 0
            
            # Enhance symbol_codex entries
            codex_start = time.time()
            if symbol_codex:
                enhanced_codex = {}
                for symbol, entry in symbol_codex.items():
                    if isinstance(entry, dict):
                        enhanced_entry = enhance_symbol_codex_entry(
                            symbol=symbol,
                            existing_entry=entry,
                            spr_definition=definition,
                            spr_term=term,
                            processor=processor
                        )
                        if enhanced_entry != entry:
                            enhanced = True
                            codex_enhanced = True
                        enhanced_codex[symbol] = enhanced_entry
                    else:
                        enhanced_codex[symbol] = entry
                
                if codex_enhanced:
                    spr['symbol_codex'] = enhanced_codex
                    stats["enhanced_codex"] += 1
            codex_time = time.time() - codex_start
            
            # Enhance compression_stages
            stages_start = time.time()
            if compression_stages:
                try:
                    enhanced_stages = enhance_compression_stages(
                        stages=compression_stages,
                        spr=spr,  # Pass full SPR for complete narrative
                        processor=processor,
                        recompress=recompress,
                        project_root=project_root,
                        agi_path=agi_path
                    )
                    
                    if enhanced_stages != compression_stages:
                        enhanced = True
                        stages_enhanced = True
                        spr['compression_stages'] = enhanced_stages
                        stats["enhanced_stages"] += 1
                        layers_count = len(enhanced_stages)
                        if recompress:
                            stats["recompressed"] += 1
                except Exception as e:
                    stats["errors"].append(f"{spr_id}: {e}")
                    if HAS_TQDM:
                        tqdm.write(f"  ⚠️  Error enhancing {spr_id}: {e}")
                    else:
                        print(f"     ⚠️  Error enhancing {spr_id}: {e}")
            stages_time = time.time() - stages_start
            
            # Report results for this SPR
            total_spr_time = time.time() - spr_start_time
            if enhanced:
                status_parts = []
                if codex_enhanced:
                    status_parts.append(f"codex({len(enhanced_codex)} symbols)")
                if stages_enhanced:
                    if recompress:
                        status_parts.append(f"recompressed({layers_count} layers)")
                    else:
                        status_parts.append("stages")
                
                status = " + ".join(status_parts)
                if HAS_TQDM:
                    tqdm.write(f"  ✅ {spr_id[:40]}: {status} in {total_spr_time:.2f}s")
                else:
                    print(f"     ✅ {spr_id[:40]}: {status} in {total_spr_time:.2f}s")
            else:
                stats["skipped"] += 1
                if HAS_TQDM:
                    tqdm.write(f"  ⏭️  {spr_id[:40]}: No changes needed")
                else:
                    print(f"     ⏭️  {spr_id[:40]}: No changes needed")
            
            # Update progress info
            if HAS_TQDM:
                elapsed_total = time.time() - start_time
                rate = i / elapsed_total if elapsed_total > 0 else 0
                remaining = (total_sprs - i) / rate if rate > 0 else 0
                spr_iterator.set_postfix({
                    'Enhanced': stats["enhanced_codex"],
                    'Recompressed': stats["recompressed"],
                    'ETA': f"{remaining:.0f}s" if remaining < 3600 else f"{remaining/60:.1f}m"
                })
    
    total_time = time.time() - start_time
    
    # Save if not dry run
    if not dry_run:
        if HAS_TQDM:
            print()  # New line after progress bar
        print(f"\n💾 Saving enhanced SPRs...")
        spr_file_backup = spr_file.with_suffix('.json.backup')
        
        # Create backup
        import shutil
        backup_start = time.time()
        shutil.copy(spr_file, spr_file_backup)
        backup_time = time.time() - backup_start
        print(f"   📦 Backup created: {spr_file_backup} ({backup_time:.2f}s)")
        
        # Save enhanced SPRs
        save_start = time.time()
        with open(spr_file, 'w', encoding='utf-8') as f:
            json.dump(spr_data, f, indent=2, ensure_ascii=False)
        save_time = time.time() - save_start
        print(f"   ✅ Saved enhanced SPRs to {spr_file} ({save_time:.2f}s)")
    else:
        if HAS_TQDM:
            print()  # New line after progress bar
        print(f"\n🔍 Dry-run: No changes saved")
    
    print(f"\n⏱️  Total processing time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    if stats['enhanced_codex'] > 0:
        avg_time = total_time / stats['enhanced_codex']
        print(f"   Average time per SPR: {avg_time:.2f}s")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Enhance existing SPRs for Russian Doll architecture - FULL RECOMPRESSION REQUIRED"
    )
    parser.add_argument(
        '--spr-file',
        type=str,
        default='knowledge_graph/spr_definitions_tv.json',
        help='Path to SPR definitions file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Don\'t save changes, just report what would be done'
    )
    parser.add_argument(
        '--no-recompress',
        action='store_true',
        help='Skip recompression (NOT RECOMMENDED - SPRs need full Russian Doll layers)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of SPRs to process (for testing)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of parallel workers (default: 1 = sequential). '
             'Note: LLM rate limits (15 req/min) may limit effective parallelism. '
             'Recommended: 2-4 workers max.'
    )
    
    args = parser.parse_args()
    
    spr_file = Path(args.spr_file)
    if not spr_file.exists():
        print(f"❌ ERROR: SPR file not found: {spr_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("RUSSIAN DOLL ARCHITECTURE: SPR Enhancement")
    print("=" * 80)
    print()
    
    # Default to recompression (SPRs need full layers)
    recompress = not args.no_recompress
    
    if not recompress:
        print()
        print("⚠️  WARNING: You've disabled recompression.")
        print("⚠️  SPRs without full Russian Doll layers cannot properly support:")
        print("   - Layered retrieval at different detail levels")
        print("   - Progressive decompression")
        print("   - Complete nuanced knowledge reconstruction")
        print()
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    
    # Validate workers
    max_workers = min(cpu_count(), 8)  # Cap at 8 to avoid excessive parallelism
    workers = max(1, min(args.workers, max_workers))
    if args.workers > max_workers:
        print(f"⚠️  Warning: Requested {args.workers} workers, capping at {max_workers} (CPU count: {cpu_count()})")
    
    stats = enhance_spr_file(
        spr_file=spr_file,
        dry_run=args.dry_run,
        recompress=recompress,
        limit=args.limit,
        workers=workers
    )
    
    print()
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total SPRs: {stats['total']}")
    print(f"✅ Enhanced symbol_codex: {stats['enhanced_codex']}")
    print(f"✅ Enhanced compression_stages: {stats['enhanced_stages']}")
    if recompress:
        print(f"✅ Recompressed with full Russian Doll layers: {stats['recompressed']}")
    print(f"⏭️  Skipped: {stats['skipped']}")
    if stats['errors']:
        print(f"❌ Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"   - {error}")
    
    if args.dry_run:
        print()
        print("💡 Run without --dry-run to apply changes")


if __name__ == "__main__":
    main()

