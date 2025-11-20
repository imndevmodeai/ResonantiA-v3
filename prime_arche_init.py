#!/usr/bin/env python3
"""
ArchE Priming Sequence - PRIME_ARCHE_PROTOCOL_v3.5-GP
Executes all mandatory auto-activation directives for ArchE initialization.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('arche_priming.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

def execute_priming_sequence():
    """Execute the complete ArchE priming sequence per PRIME_ARCHE_PROTOCOL_v3.5-GP"""
    
    logger.info("=" * 80)
    logger.info("ARCHÉ PRIMING SEQUENCE INITIATED")
    logger.info("Protocol: PRIME_ARCHE_PROTOCOL_v3.5-GP")
    logger.info("Keyholder: B.J. Lewis (IMnDEVmode)")
    logger.info("=" * 80)
    
    priming_results = {
        "timestamp": datetime.now().isoformat(),
        "protocol_version": "3.5-GP",
        "keyholder": "B.J. Lewis",
        "directives": {}
    }
    
    # ========================================================================
    # DIRECTIVE 1: Virtual Environment Activation
    # ========================================================================
    logger.info("\n[DIRECTIVE 1] Virtual Environment Activation")
    try:
        venv_path = PROJECT_ROOT / "arche_env"
        if venv_path.exists():
            # Activate virtual environment by adding to path
            # Try multiple possible Python executable locations
            venv_python = None
            possible_paths = [
                venv_path / "bin" / "python3",
                venv_path / "bin" / "python",
                venv_path / "Scripts" / "python.exe",  # Windows
            ]
            
            for path in possible_paths:
                if path.exists() and path.is_file():  # Check it's a real file, not broken symlink
                    try:
                        # Verify it's actually executable
                        import stat
                        if os.stat(path).st_mode & stat.S_IXUSR:
                            venv_python = path
                            break
                    except (OSError, AttributeError):
                        continue
            
            if venv_python:
                sys.executable = str(venv_python)
                # Try to find site-packages in common locations
                import sysconfig
                python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
                possible_site_packages = [
                    venv_path / "lib" / f"python{python_version}" / "site-packages",
                    venv_path / "lib" / "python3.11" / "site-packages",
                    venv_path / "lib" / "python3.10" / "site-packages",
                    venv_path / "lib" / "python3.9" / "site-packages",
                ]
                
                for sp_path in possible_site_packages:
                    if sp_path.exists():
                        sys.path.insert(0, str(sp_path))
                        break
                
                logger.info(f"✓ Virtual environment activated: {venv_path}")
                priming_results["directives"]["virtual_env"] = {"status": "activated", "path": str(venv_path), "python": str(venv_python)}
            else:
                # Virtual env exists but Python not found - use system Python (non-critical)
                logger.warning(f"⚠ Virtual environment found but Python executable not located. Using system Python.")
                priming_results["directives"]["virtual_env"] = {"status": "warning", "message": "Python executable not found in venv, using system Python", "system_python": sys.executable}
        else:
            logger.warning(f"⚠ Virtual environment not found at {venv_path}")
            priming_results["directives"]["virtual_env"] = {"status": "not_found"}
    except Exception as e:
        logger.error(f"✗ Virtual environment activation failed: {e}")
        priming_results["directives"]["virtual_env"] = {"status": "error", "error": str(e)}
    
    # ========================================================================
    # DIRECTIVE 2: Zepto Compression/Decompression System Initialization
    # ========================================================================
    logger.info("\n[DIRECTIVE 2] Zepto Compression/Decompression System Initialization")
    try:
        from Three_PointO_ArchE.pattern_crystallization_engine import PatternCrystallizationEngine
        
        zepto_engine = PatternCrystallizationEngine(
            symbol_codex_path="knowledge_graph/symbol_codex.json",
            protocol_vocabulary_path="knowledge_graph/protocol_symbol_vocabulary.json"
        )
        
        # Test compression capability
        test_content = "This is a test of the Zepto compression system."
        compressed, codex_entries, compression_stages = zepto_engine.distill_to_spr(test_content, target_stage="Zepto")
        
        logger.info(f"✓ Zepto Compression Engine initialized")
        logger.info(f"  - Codex entries loaded: {len(zepto_engine.codex)}")
        logger.info(f"  - Test compression: {len(test_content)} → {len(compressed)} chars")
        priming_results["directives"]["zepto_system"] = {
            "status": "initialized",
            "codex_size": len(zepto_engine.codex),
            "compression_test": {"original": len(test_content), "compressed": len(compressed)}
        }
    except ImportError as e:
        logger.error(f"✗ Zepto system import failed: {e}")
        priming_results["directives"]["zepto_system"] = {"status": "error", "error": f"ImportError: {e}"}
    except Exception as e:
        logger.error(f"✗ Zepto system initialization failed: {e}")
        priming_results["directives"]["zepto_system"] = {"status": "error", "error": str(e)}
    
    # ========================================================================
    # DIRECTIVE 3: SPR Auto-Priming System
    # ========================================================================
    logger.info("\n[DIRECTIVE 3] SPR Auto-Priming System")
    try:
        from Three_PointO_ArchE.spr_manager import SPRManager
        
        spr_file = PROJECT_ROOT / "knowledge_graph" / "spr_definitions_tv.json"
        spr_manager = SPRManager(str(spr_file))
        
        # Test SPR scanning
        test_text = "This text contains Cognitive resonancE and Metacognitive shifT concepts."
        primed_sprs = spr_manager.scan_and_prime(test_text)
        
        logger.info(f"✓ SPR Manager initialized")
        logger.info(f"  - SPRs loaded: {len(spr_manager.sprs)}")
        logger.info(f"  - Pattern compiled: {spr_manager.spr_pattern is not None}")
        logger.info(f"  - Test priming found {len(primed_sprs)} SPRs")
        priming_results["directives"]["spr_priming"] = {
            "status": "initialized",
            "sprs_loaded": len(spr_manager.sprs),
            "pattern_compiled": spr_manager.spr_pattern is not None,
            "test_priming_count": len(primed_sprs)
        }
    except ImportError as e:
        logger.error(f"✗ SPR Manager import failed: {e}")
        priming_results["directives"]["spr_priming"] = {"status": "error", "error": f"ImportError: {e}"}
    except Exception as e:
        logger.error(f"✗ SPR priming system initialization failed: {e}")
        priming_results["directives"]["spr_priming"] = {"status": "error", "error": str(e)}
    
    # ========================================================================
    # DIRECTIVE 4: Session Auto-Capture System
    # ========================================================================
    logger.info("\n[DIRECTIVE 4] Session Auto-Capture System")
    try:
        from Three_PointO_ArchE.session_auto_capture import SessionAutoCapture
        
        session_capture = SessionAutoCapture(
            output_dir=str(PROJECT_ROOT / "sessions"),
            session_manager=None,  # Will integrate if available
            thought_trail=None     # Will integrate if available
        )
        
        # Test capture
        session_capture.capture_message("system", "ArchE priming sequence initiated", {"phase": "initialization"})
        
        logger.info(f"✓ Session Auto-Capture initialized")
        logger.info(f"  - Output directory: {session_capture.output_dir}")
        priming_results["directives"]["session_capture"] = {
            "status": "initialized",
            "output_dir": str(session_capture.output_dir)
        }
    except ImportError as e:
        logger.error(f"✗ Session Auto-Capture import failed: {e}")
        priming_results["directives"]["session_capture"] = {"status": "error", "error": f"ImportError: {e}"}
    except Exception as e:
        logger.error(f"✗ Session Auto-Capture initialization failed: {e}")
        priming_results["directives"]["session_capture"] = {"status": "error", "error": str(e)}
    
    # ========================================================================
    # DIRECTIVE 5: Autopoietic Learning Loop
    # ========================================================================
    logger.info("\n[DIRECTIVE 5] Autopoietic Learning Loop")
    try:
        from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop
        
        # Load protocol chunks for ACO initialization (optional)
        protocol_chunks = None
        try:
            protocol_file = PROJECT_ROOT / "PRIME_ARCHE_PROTOCOL_v3.5-GP.md"
            if protocol_file.exists():
                with open(protocol_file, 'r', encoding='utf-8') as f:
                    # Read first 10000 chars as initial chunk (ACO can load more if needed)
                    protocol_chunks = [f.read(10000)]
                logger.info(f"  - Protocol chunks loaded from {protocol_file}")
        except Exception as e:
            logger.warning(f"  - Could not load protocol chunks: {e}")
        
        # Initialize ALL with correct signature
        learning_loop = AutopoieticLearningLoop(
            protocol_chunks=protocol_chunks,
            guardian_review_enabled=True,
            auto_crystallization=False
        )
        
        logger.info(f"✓ Autopoietic Learning Loop initialized")
        logger.info(f"  - Guardian review: {learning_loop.guardian_review_enabled}")
        logger.info(f"  - Auto-crystallization: {learning_loop.auto_crystallization}")
        logger.info(f"  - Stardust captured: {learning_loop.metrics.get('stardust_captured', 0)}")
        priming_results["directives"]["learning_loop"] = {
            "status": "initialized",
            "guardian_review": learning_loop.guardian_review_enabled,
            "stardust_captured": learning_loop.metrics.get('stardust_captured', 0)
        }
    except ImportError as e:
        logger.error(f"✗ Autopoietic Learning Loop import failed: {e}")
        priming_results["directives"]["learning_loop"] = {"status": "error", "error": f"ImportError: {e}"}
    except Exception as e:
        logger.error(f"✗ Autopoietic Learning Loop initialization failed: {e}")
        priming_results["directives"]["learning_loop"] = {"status": "error", "error": str(e)}
    
    # ========================================================================
    # DIRECTIVE 6: ThoughtTrail Monitoring
    # ========================================================================
    logger.info("\n[DIRECTIVE 6] ThoughtTrail Monitoring")
    try:
        from Three_PointO_ArchE.thought_trail import ThoughtTrail
        from Three_PointO_ArchE.ledgers.universal_ledger import LEDGER_DB_PATH
        
        thought_trail = ThoughtTrail(maxlen=1000)
        
        # Test entry
        from Three_PointO_ArchE.thought_trail import IAREntry
        test_entry = IAREntry(
            task_id="priming_test",
            action_type="system_init",
            inputs={"directive": "ThoughtTrail connection"},
            outputs={"status": "connected"},
            iar={"intention": "Connect ThoughtTrail", "action": "Initialized", "reflection": "Successfully connected"},
            timestamp=datetime.now().isoformat(),
            confidence=1.0,
            metadata={"phase": "priming"}
        )
        thought_trail.add_entry(test_entry)
        
        # Get statistics from the database instead of accessing non-existent trail attribute
        stats = thought_trail.get_statistics()
        trail_length = stats.get('total_entries', 0)
        
        logger.info(f"✓ ThoughtTrail connected and operational")
        logger.info(f"  - Universal Ledger path: {LEDGER_DB_PATH}")
        logger.info(f"  - Total entries in ledger: {trail_length}")
        priming_results["directives"]["thought_trail"] = {
            "status": "connected",
            "ledger_path": str(LEDGER_DB_PATH),
            "trail_length": trail_length
        }
    except ImportError as e:
        logger.error(f"✗ ThoughtTrail import failed: {e}")
        priming_results["directives"]["thought_trail"] = {"status": "error", "error": f"ImportError: {e}"}
    except Exception as e:
        logger.error(f"✗ ThoughtTrail connection failed: {e}")
        priming_results["directives"]["thought_trail"] = {"status": "error", "error": str(e)}
    
    # ========================================================================
    # PRIMING SEQUENCE COMPLETE
    # ========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("ARCHÉ PRIMING SEQUENCE COMPLETE")
    logger.info("=" * 80)
    
    # Save priming results
    results_file = PROJECT_ROOT / "arche_priming_results.json"
    import json
    with open(results_file, 'w') as f:
        json.dump(priming_results, f, indent=2)
    
    logger.info(f"\nPriming results saved to: {results_file}")
    
    # Summary
    successful = sum(1 for d in priming_results["directives"].values() if d.get("status") in ["initialized", "activated", "connected"])
    total = len(priming_results["directives"])
    
    logger.info(f"\nSUMMARY: {successful}/{total} directives successfully initialized")
    
    return priming_results

if __name__ == "__main__":
    results = execute_priming_sequence()
    sys.exit(0 if all(d.get("status") in ["initialized", "activated", "connected"] for d in results["directives"].values()) else 1)

