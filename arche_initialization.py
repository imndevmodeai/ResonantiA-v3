#!/usr/bin/env python3
"""
ArchE Auto-Activation Initialization Script
Executes all mandatory auto-activation directives from PRIME_ARCHE_PROTOCOL.md
"""

import sys
import os
from pathlib import Path
import json
import traceback

# Add project root to Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

print("=" * 80)
print("ArchE AUTO-ACTIVATION INITIALIZATION")
print("=" * 80)
print(f"Project Root: {project_root}")
print(f"Python: {sys.executable}")
print(f"Virtual Environment: {os.environ.get('VIRTUAL_ENV', 'NOT ACTIVATED')}")
print("=" * 80)

# Track initialization status
init_status = {
    "virtual_env": False,
    "zepto_system": False,
    "spr_priming": False,
    "session_capture": False,
    "learning_loop": False,
    "thought_trail": False
}

# ============================================================================
# 0. Virtual Environment Verification
# ============================================================================
print("\n[0] Verifying Virtual Environment Activation...")
if os.environ.get('VIRTUAL_ENV'):
    print(f"✅ Virtual environment activated: {os.environ.get('VIRTUAL_ENV')}")
    init_status["virtual_env"] = True
else:
    print("⚠️  WARNING: Virtual environment not detected in environment variables")
    print("   Please ensure 'arche_env' is activated before running this script")
    print("   Run: source arche_env/bin/activate")
    # Continue anyway for testing, but warn user

# ============================================================================
# 0.1. Zepto Compression/Decompression System Initialization
# ============================================================================
print("\n[0.1] Initializing Zepto Compression/Decompression System...")
try:
    from Three_PointO_ArchE.pattern_crystallization_engine import PatternCrystallizationEngine
    
    # Check if codex files exist
    codex_path = project_root / "knowledge_graph" / "symbol_codex.json"
    vocab_path = project_root / "knowledge_graph" / "protocol_symbol_vocabulary.json"
    
    if not codex_path.exists():
        print(f"⚠️  Warning: symbol_codex.json not found at {codex_path}")
        print("   Creating empty codex...")
        codex_path.parent.mkdir(parents=True, exist_ok=True)
        with open(codex_path, 'w') as f:
            json.dump({}, f)
    
    if not vocab_path.exists():
        print(f"⚠️  Warning: protocol_symbol_vocabulary.json not found at {vocab_path}")
        print("   Creating empty vocabulary...")
        vocab_path.parent.mkdir(parents=True, exist_ok=True)
        with open(vocab_path, 'w') as f:
            json.dump({}, f)
    
    # Initialize the crystallization engine
    crystallization_engine = PatternCrystallizationEngine(
        symbol_codex_path=str(codex_path),
        protocol_vocabulary_path=str(vocab_path)
    )
    print("✅ PatternCrystallizationEngine initialized")
    
    # Define the ingest_file_with_zepto function
    def ingest_file_with_zepto(file_path: str, compress: bool = True) -> dict:
        """
        Ingest a file using Zepto compression/decompression process.
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if compress:
            # Compress to Zepto SPR
            zepto_spr, codex_entries = crystallization_engine.distill_to_spr(
                content,
                target_stage="Zepto"
            )
            
            compression_ratio = len(content) / len(zepto_spr) if zepto_spr else 1.0
            
            return {
                'content': content,
                'zepto_spr': zepto_spr,
                'symbol_codex': {
                    symbol: {
                        'meaning': entry.meaning,
                        'context': entry.context
                    }
                    for symbol, entry in codex_entries.items()
                },
                'compression_ratio': compression_ratio,
                'compression_stages': [
                    {
                        'stage': stage.stage_name,
                        'compression_ratio': stage.compression_ratio,
                        'symbol_count': stage.symbol_count,
                        'timestamp': stage.timestamp
                    }
                    for stage in crystallization_engine.compression_history
                ]
            }
        else:
            # File is already in Zepto format, decompress it
            import json
            zepto_data = json.loads(content)
            zepto_spr = zepto_data.get('zepto_spr', content)
            codex = zepto_data.get('symbol_codex', {})
            
            # Convert codex dict to SymbolCodexEntry format
            from Three_PointO_ArchE.pattern_crystallization_engine import SymbolCodexEntry
            codex_entries = {
                symbol: SymbolCodexEntry(
                    symbol=symbol,
                    meaning=entry.get('meaning', ''),
                    context=entry.get('context', ''),
                    usage_examples=entry.get('usage_examples', []),
                    created_at=entry.get('created_at', '')
                )
                for symbol, entry in codex.items()
            }
            
            # Decompress
            decompressed = crystallization_engine.decompress_spr(zepto_spr, codex_entries)
            
            return {
                'content': decompressed,
                'zepto_spr': zepto_spr,
                'symbol_codex': codex,
                'decompressed_length': len(decompressed)
            }
    
    # Auto-ingest PRIME protocol file with Zepto compression
    prime_protocol_path = project_root / "PRIME_ARCHE_PROTOCOL.md"
    if prime_protocol_path.exists():
        try:
            prime_protocol_data = ingest_file_with_zepto(str(prime_protocol_path), compress=True)
            print(f"✅ PRIME protocol ingested and compressed: {prime_protocol_data['compression_ratio']:.1f}:1 ratio")
            print(f"   Original: {len(prime_protocol_data['content'])} chars → Zepto: {len(prime_protocol_data['zepto_spr'])} chars")
            init_status["zepto_system"] = True
        except Exception as e:
            print(f"⚠️  Warning: Zepto compression failed for PRIME protocol: {e}")
            print("   Falling back to standard file reading")
            traceback.print_exc()
    else:
        print(f"⚠️  Warning: PRIME_ARCHE_PROTOCOL.md not found at {prime_protocol_path}")
        
except Exception as e:
    print(f"❌ ERROR: Failed to initialize Zepto system: {e}")
    traceback.print_exc()

# ============================================================================
# 1. SPR Auto-Priming System
# ============================================================================
print("\n[1] Initializing SPR Auto-Priming System...")
try:
    from Three_PointO_ArchE.spr_manager import SPRManager
    
    spr_file_path = project_root / "knowledge_graph" / "spr_definitions_tv.json"
    
    if not spr_file_path.exists():
        print(f"⚠️  Warning: SPR definitions file not found at {spr_file_path}")
        print("   Creating empty SPR definitions file...")
        spr_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(spr_file_path, 'w') as f:
            json.dump([], f)
    
    # Check if file is Zepto-compressed
    try:
        with open(spr_file_path, 'r', encoding='utf-8') as f:
            spr_data = json.load(f)
        
        if isinstance(spr_data, dict) and 'zepto_spr' in spr_data:
            print("   Detected Zepto-compressed SPR file, decompressing...")
            spr_data = ingest_file_with_zepto(str(spr_file_path), compress=False)
            # Use decompressed content
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                json.dump(json.loads(spr_data['content']), tmp)
                spr_file_path = Path(tmp.name)
    except:
        # Not Zepto-compressed, use file as-is
        pass
    
    spr_manager = SPRManager(str(spr_file_path))
    primed_sprs = spr_manager.scan_and_prime("Full protocol priming with all SPRs")
    
    print(f"✅ SPR Manager initialized")
    print(f"   Loaded SPRs: {len(spr_manager.sprs)}")
    print(f"   Primed SPRs in test scan: {len(primed_sprs)}")
    init_status["spr_priming"] = True
    
except Exception as e:
    print(f"❌ ERROR: Failed to initialize SPR Auto-Priming System: {e}")
    traceback.print_exc()

# ============================================================================
# 2. Session Auto-Capture System
# ============================================================================
print("\n[2] Initializing Session Auto-Capture System...")
try:
    from Three_PointO_ArchE.session_auto_capture import SessionAutoCapture
    
    session_capture = SessionAutoCapture(output_dir=str(project_root))
    print("✅ SessionAutoCapture initialized")
    print(f"   Output directory: {project_root}")
    print("   Status: Active - Captures all messages, IAR entries, SPRs, and insights automatically")
    init_status["session_capture"] = True
    
except Exception as e:
    print(f"❌ ERROR: Failed to initialize Session Auto-Capture System: {e}")
    traceback.print_exc()

# ============================================================================
# 3. Autopoietic Learning Loop
# ============================================================================
print("\n[3] Verifying Autopoietic Learning Loop...")
try:
    from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop
    
    learning_loop = AutopoieticLearningLoop()
    print("✅ AutopoieticLearningLoop initialized")
    print("   Status: Active, Guardian review required for wisdom crystallization")
    print("   Note: Learning loop uses PatternCrystallizationEngine for Zepto compression of wisdom")
    init_status["learning_loop"] = True
    
except Exception as e:
    print(f"❌ ERROR: Failed to initialize Autopoietic Learning Loop: {e}")
    traceback.print_exc()

# ============================================================================
# 4. ThoughtTrail Monitoring
# ============================================================================
print("\n[4] Connecting to ThoughtTrail Monitoring...")
try:
    from Three_PointO_ArchE.thought_trail import ThoughtTrail
    
    thought_trail = ThoughtTrail(maxlen=1000)
    print("✅ ThoughtTrail initialized")
    print(f"   Buffer size: 1000 thoughts")
    print("   Status: Active - Captures every IAR entry for pattern detection")
    init_status["thought_trail"] = True
    
except Exception as e:
    print(f"❌ ERROR: Failed to connect to ThoughtTrail: {e}")
    traceback.print_exc()

# ============================================================================
# INITIALIZATION SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("INITIALIZATION SUMMARY")
print("=" * 80)

all_systems_online = all(init_status.values())
status_symbol = "✅" if all_systems_online else "⚠️"

for system_name, status in init_status.items():
    symbol = "✅" if status else "❌"
    print(f"{symbol} {system_name.replace('_', ' ').title()}: {'ONLINE' if status else 'OFFLINE'}")

print("=" * 80)

if all_systems_online:
    print("🎉 ALL SYSTEMS ONLINE - ArchE FULLY PRIMED AND OPERATIONAL")
    print("\nArchE is now ready for:")
    print("  • Cognitive Resonance operations")
    print("  • SPR-based cognitive activation")
    print("  • Session auto-capture")
    print("  • Autopoietic learning")
    print("  • ThoughtTrail pattern detection")
    print("  • Zepto compression/decompression")
else:
    print("⚠️  SOME SYSTEMS OFFLINE - Review errors above")
    print("   ArchE may have limited functionality")

print("=" * 80)

# Store initialized objects in a global namespace for access
if all_systems_online:
    print("\n💾 Storing initialized systems in global namespace...")
    globals()['crystallization_engine'] = crystallization_engine
    globals()['spr_manager'] = spr_manager
    globals()['session_capture'] = session_capture
    globals()['learning_loop'] = learning_loop
    globals()['thought_trail'] = thought_trail
    globals()['ingest_file_with_zepto'] = ingest_file_with_zepto
    print("✅ Systems stored and ready for use")

print("\n🚀 ArchE Initialization Complete!")





