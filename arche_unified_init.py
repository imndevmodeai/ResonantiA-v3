#!/usr/bin/env python3
"""
ArchE Unified Initialization Script - PRIME_ARCHE_PROTOCOL_v3.5-GP
The superior, unified initialization system combining the best of both approaches.

This script:
- Activates virtual environment (MANDATORY)
- Initializes Zepto compression/decompression with full file ingestion
- Auto-ingests PRIME protocol with Zepto compression
- Handles Zepto-compressed SPR files automatically
- Loads protocol chunks for ACO initialization
- Provides structured logging with immediate feedback
- Returns comprehensive results dictionary
- Optionally stores objects in global namespace
- Saves priming results to JSON

Usage:
    python3 arche_unified_init.py
    # Or import and call:
    from arche_unified_init import prime_arche_system
    results = prime_arche_system(store_globals=True)
"""

import sys
import os
import logging
import json
import traceback
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging with both console and file output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('arche_unified_init.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Protocol version constant
PROTOCOL_VERSION = "3.5-GP"
PRIME_PROTOCOL_FILE = f"PRIME_ARCHE_PROTOCOL_{PROTOCOL_VERSION}.md"


def print_and_log(message: str, level: str = "info", emoji: str = ""):
    """Print with emoji for immediate feedback and log for persistence."""
    full_message = f"{emoji} {message}" if emoji else message
    print(full_message)
    getattr(logger, level)(message)


def activate_virtual_environment(project_root: Path) -> Dict[str, Any]:
    """
    Activate arche_env virtual environment (MANDATORY per PRIME protocol).
    
    Returns:
        Dictionary with activation status and details
    """
    result = {
        "status": "not_found",
        "path": None,
        "python": None,
        "error": None
    }
    
    venv_path = project_root / "arche_env"
    
    if not venv_path.exists():
        error_msg = f"arche_env virtual environment not found at {venv_path}"
        print_and_log(f"❌ ERROR: {error_msg}", "error")
        print_and_log("   Please create it with: python3 -m venv arche_env", "error")
        result["error"] = error_msg
        return result
    
    # Check if already activated
    virtual_env_path = os.environ.get('VIRTUAL_ENV')
    python_executable = sys.executable
    venv_detected = False
    
    if virtual_env_path:
        if 'arche_env' in virtual_env_path or Path(virtual_env_path).samefile(venv_path):
            print_and_log(f"✅ Virtual environment already activated: {virtual_env_path}", "info", "✅")
            venv_detected = True
            result["status"] = "already_activated"
            result["path"] = virtual_env_path
            result["python"] = python_executable
            return result
        else:
            print_and_log(f"⚠️  Different venv activated: {virtual_env_path}", "warning", "⚠️")
            print_and_log("   Switching to arche_env...", "info")
    
    elif 'arche_env' in python_executable:
        print_and_log(f"✅ Virtual environment detected via Python path: {venv_path}", "info", "✅")
        print_and_log(f"   Python executable: {python_executable}", "info")
        venv_detected = True
        result["status"] = "detected"
        result["path"] = str(venv_path)
        result["python"] = python_executable
        return result
    
    # Activate if not already active
    if not venv_detected:
        print_and_log("🔄 Activating arche_env virtual environment...", "info", "🔄")
        
        # Try multiple possible Python executable locations
        venv_python = None
        possible_paths = [
            venv_path / "bin" / "python3",
            venv_path / "bin" / "python",
            venv_path / "Scripts" / "python.exe",  # Windows
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                try:
                    import stat
                    if os.stat(path).st_mode & stat.S_IXUSR:
                        venv_python = path
                        break
                except (OSError, AttributeError):
                    continue
        
        if venv_python:
            sys.executable = str(venv_python)
            
            # Add venv site-packages to path
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
            
            # Set environment variables
            os.environ['VIRTUAL_ENV'] = str(venv_path)
            os.environ['PATH'] = str(venv_path / "bin") + os.pathsep + os.environ.get('PATH', '')
            
            print_and_log(f"✅ Activated arche_env: {venv_path}", "info", "✅")
            print_and_log(f"   Using Python: {sys.executable}", "info")
            
            result["status"] = "activated"
            result["path"] = str(venv_path)
            result["python"] = str(venv_python)
        else:
            error_msg = f"Python executable not found in arche_env at {venv_path}"
            print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
            print_and_log("   Please ensure arche_env is properly created", "error")
            result["error"] = error_msg
    
    return result


def initialize_zepto_system(project_root: Path) -> Dict[str, Any]:
    """
    Initialize Zepto compression/decompression system with full file ingestion.
    
    Returns:
        Dictionary with initialization status, engine, and ingest function
    """
    result = {
        "status": "error",
        "engine": None,
        "ingest_function": None,
        "prime_protocol_ingested": False,
        "compression_ratio": None,
        "error": None
    }
    
    try:
        from Three_PointO_ArchE.pattern_crystallization_engine import PatternCrystallizationEngine
        
        # Check if codex files exist, create if missing
        codex_path = project_root / "knowledge_graph" / "symbol_codex.json"
        vocab_path = project_root / "knowledge_graph" / "protocol_symbol_vocabulary.json"
        
        if not codex_path.exists():
            print_and_log(f"⚠️  Warning: symbol_codex.json not found at {codex_path}", "warning", "⚠️")
            print_and_log("   Creating empty codex...", "info")
            codex_path.parent.mkdir(parents=True, exist_ok=True)
            with open(codex_path, 'w') as f:
                json.dump({}, f)
        
        if not vocab_path.exists():
            print_and_log(f"⚠️  Warning: protocol_symbol_vocabulary.json not found at {vocab_path}", "warning", "⚠️")
            print_and_log("   Creating empty vocabulary...", "info")
            vocab_path.parent.mkdir(parents=True, exist_ok=True)
            with open(vocab_path, 'w') as f:
                json.dump({}, f)
        
        # Initialize the crystallization engine
        crystallization_engine = PatternCrystallizationEngine(
            symbol_codex_path=str(codex_path),
            protocol_vocabulary_path=str(vocab_path)
        )
        print_and_log("✅ PatternCrystallizationEngine initialized", "info", "✅")
        
        # Define the ingest_file_with_zepto function
        def ingest_file_with_zepto(file_path: str, compress: bool = True) -> dict:
            """
            Ingest a file using Zepto compression/decompression process.
            
            Args:
                file_path: Path to the file to ingest
                compress: If True, compress to Zepto SPR; if False, decompress from Zepto SPR
                
            Returns:
                Dictionary containing content, zepto_spr, symbol_codex, compression_ratio
            """
            file = Path(file_path)
            if not file.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file content
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if compress:
                # Compress to Zepto SPR
                zepto_spr, codex_entries, compression_stages_list = crystallization_engine.distill_to_spr(
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
                        for stage in compression_stages_list
                    ]
                }
            else:
                # File is already in Zepto format, decompress it
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
        prime_protocol_path = project_root / PRIME_PROTOCOL_FILE
        if prime_protocol_path.exists():
            try:
                prime_protocol_data = ingest_file_with_zepto(str(prime_protocol_path), compress=True)
                ratio = prime_protocol_data['compression_ratio']
                original_len = len(prime_protocol_data['content'])
                zepto_len = len(prime_protocol_data['zepto_spr'])
                
                print_and_log(
                    f"✅ PRIME protocol ingested and compressed: {ratio:.1f}:1 ratio",
                    "info", "✅"
                )
                print_and_log(
                    f"   Original: {original_len} chars → Zepto: {zepto_len} chars",
                    "info"
                )
                
                result["prime_protocol_ingested"] = True
                result["compression_ratio"] = ratio
            except Exception as e:
                print_and_log(
                    f"⚠️  Warning: Zepto compression failed for PRIME protocol: {e}",
                    "warning", "⚠️"
                )
                print_and_log("   Falling back to standard file reading", "info")
                traceback.print_exc()
        else:
            print_and_log(
                f"⚠️  Warning: {PRIME_PROTOCOL_FILE} not found at {prime_protocol_path}",
                "warning", "⚠️"
            )
        
        result["status"] = "initialized"
        result["engine"] = crystallization_engine
        result["ingest_function"] = ingest_file_with_zepto
        
    except ImportError as e:
        error_msg = f"Zepto system import failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        result["error"] = f"ImportError: {e}"
    except Exception as e:
        error_msg = f"Zepto system initialization failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        traceback.print_exc()
        result["error"] = str(e)
    
    return result


def initialize_spr_system(project_root: Path, ingest_file_with_zepto: Optional[callable] = None) -> Dict[str, Any]:
    """
    Initialize SPR Auto-Priming System with Zepto decompression support.
    
    Args:
        project_root: Project root directory
        ingest_file_with_zepto: Optional function for Zepto decompression
        
    Returns:
        Dictionary with initialization status and SPR manager
    """
    result = {
        "status": "error",
        "spr_manager": None,
        "sprs_loaded": 0,
        "test_priming_count": 0,
        "error": None
    }
    
    try:
        from Three_PointO_ArchE.spr_manager import SPRManager
        
        spr_file_path = project_root / "knowledge_graph" / "spr_definitions_tv.json"
        
        if not spr_file_path.exists():
            print_and_log(
                f"⚠️  Warning: SPR definitions file not found at {spr_file_path}",
                "warning", "⚠️"
            )
            print_and_log("   Creating empty SPR definitions file...", "info")
            spr_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(spr_file_path, 'w') as f:
                json.dump([], f)
        
        # Check if file is Zepto-compressed
        if ingest_file_with_zepto:
            try:
                with open(spr_file_path, 'r', encoding='utf-8') as f:
                    spr_data = json.load(f)
                
                if isinstance(spr_data, dict) and 'zepto_spr' in spr_data:
                    print_and_log("   Detected Zepto-compressed SPR file, decompressing...", "info")
                    spr_data = ingest_file_with_zepto(str(spr_file_path), compress=False)
                    # Use decompressed content
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                        json.dump(json.loads(spr_data['content']), tmp)
                        spr_file_path = Path(tmp.name)
            except:
                # Not Zepto-compressed, use file as-is
                pass
        
        spr_manager = SPRManager(str(spr_file_path))
        primed_sprs = spr_manager.scan_and_prime("Full protocol priming with all SPRs")
        
        print_and_log("✅ SPR Manager initialized", "info", "✅")
        print_and_log(f"   Loaded SPRs: {len(spr_manager.sprs)}", "info")
        print_and_log(f"   Primed SPRs in test scan: {len(primed_sprs)}", "info")
        
        result["status"] = "initialized"
        result["spr_manager"] = spr_manager
        result["sprs_loaded"] = len(spr_manager.sprs)
        result["test_priming_count"] = len(primed_sprs)
        
    except ImportError as e:
        error_msg = f"SPR Manager import failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        result["error"] = f"ImportError: {e}"
    except Exception as e:
        error_msg = f"SPR priming system initialization failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        traceback.print_exc()
        result["error"] = str(e)
    
    return result


def initialize_session_capture(project_root: Path) -> Dict[str, Any]:
    """
    Initialize Session Auto-Capture System.
    
    Returns:
        Dictionary with initialization status and session capture instance
    """
    result = {
        "status": "error",
        "session_capture": None,
        "output_dir": None,
        "error": None
    }
    
    try:
        from Three_PointO_ArchE.session_auto_capture import SessionAutoCapture
        
        output_dir = str(project_root)
        session_capture = SessionAutoCapture(output_dir=output_dir)
        
        # Test capture
        session_capture.capture_message(
            "system",
            "ArchE unified initialization sequence initiated",
            {"phase": "initialization", "protocol_version": PROTOCOL_VERSION}
        )
        
        print_and_log("✅ SessionAutoCapture initialized", "info", "✅")
        print_and_log(f"   Output directory: {output_dir}", "info")
        print_and_log(
            "   Status: Active - Captures all messages, IAR entries, SPRs, and insights automatically",
            "info"
        )
        
        result["status"] = "initialized"
        result["session_capture"] = session_capture
        result["output_dir"] = output_dir
        
    except ImportError as e:
        error_msg = f"Session Auto-Capture import failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        result["error"] = f"ImportError: {e}"
    except Exception as e:
        error_msg = f"Session Auto-Capture initialization failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        traceback.print_exc()
        result["error"] = str(e)
    
    return result


def initialize_learning_loop(project_root: Path) -> Dict[str, Any]:
    """
    Initialize Autopoietic Learning Loop with protocol chunks for ACO.
    
    Returns:
        Dictionary with initialization status and learning loop instance
    """
    result = {
        "status": "error",
        "learning_loop": None,
        "guardian_review": None,
        "stardust_captured": 0,
        "error": None
    }
    
    try:
        from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop
        
        # Load protocol chunks for ACO initialization (optional)
        protocol_chunks = None
        try:
            protocol_file = project_root / PRIME_PROTOCOL_FILE
            if protocol_file.exists():
                with open(protocol_file, 'r', encoding='utf-8') as f:
                    # Read first 10000 chars as initial chunk (ACO can load more if needed)
                    protocol_chunks = [f.read(10000)]
                print_and_log(f"  - Protocol chunks loaded from {protocol_file}", "info")
        except Exception as e:
            print_and_log(f"  - Could not load protocol chunks: {e}", "warning", "⚠️")
        
        # Initialize ALL with correct signature
        learning_loop = AutopoieticLearningLoop(
            protocol_chunks=protocol_chunks,
            guardian_review_enabled=True,
            auto_crystallization=False
        )
        
        print_and_log("✅ AutopoieticLearningLoop initialized", "info", "✅")
        print_and_log("   Status: Active, Guardian review required for wisdom crystallization", "info")
        print_and_log(
            "   Note: Learning loop uses PatternCrystallizationEngine for Zepto compression of wisdom",
            "info"
        )
        print_and_log(f"  - Guardian review: {learning_loop.guardian_review_enabled}", "info")
        print_and_log(f"  - Auto-crystallization: {learning_loop.auto_crystallization}", "info")
        print_and_log(
            f"  - Stardust captured: {learning_loop.metrics.get('stardust_captured', 0)}",
            "info"
        )
        
        result["status"] = "initialized"
        result["learning_loop"] = learning_loop
        result["guardian_review"] = learning_loop.guardian_review_enabled
        result["stardust_captured"] = learning_loop.metrics.get('stardust_captured', 0)
        
    except ImportError as e:
        error_msg = f"Autopoietic Learning Loop import failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        result["error"] = f"ImportError: {e}"
    except Exception as e:
        error_msg = f"Autopoietic Learning Loop initialization failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        traceback.print_exc()
        result["error"] = str(e)
    
    return result


def initialize_thought_trail(project_root: Path) -> Dict[str, Any]:
    """
    Initialize ThoughtTrail Monitoring.
    
    Returns:
        Dictionary with initialization status and thought trail instance
    """
    result = {
        "status": "error",
        "thought_trail": None,
        "trail_length": 0,
        "ledger_path": None,
        "error": None
    }
    
    try:
        from Three_PointO_ArchE.thought_trail import ThoughtTrail, IAREntry
        from Three_PointO_ArchE.ledgers.universal_ledger import LEDGER_DB_PATH
        
        thought_trail = ThoughtTrail(maxlen=1000)
        
        # Test entry
        test_entry = IAREntry(
            task_id="unified_init_test",
            action_type="system_init",
            inputs={"directive": "ThoughtTrail connection"},
            outputs={"status": "connected"},
            iar={
                "intention": "Connect ThoughtTrail",
                "action": "Initialized",
                "reflection": "Successfully connected"
            },
            timestamp=datetime.now().isoformat(),
            confidence=1.0,
            metadata={"phase": "unified_initialization"}
        )
        thought_trail.add_entry(test_entry)
        
        # Get statistics from the database
        stats = thought_trail.get_statistics()
        trail_length = stats.get('total_entries', 0)
        
        print_and_log("✅ ThoughtTrail initialized", "info", "✅")
        print_and_log(f"   Buffer size: 1000 thoughts", "info")
        print_and_log("   Status: Active - Captures every IAR entry for pattern detection", "info")
        print_and_log(f"  - Universal Ledger path: {LEDGER_DB_PATH}", "info")
        print_and_log(f"  - Total entries in ledger: {trail_length}", "info")
        
        result["status"] = "connected"
        result["thought_trail"] = thought_trail
        result["trail_length"] = trail_length
        result["ledger_path"] = str(LEDGER_DB_PATH)
        
    except ImportError as e:
        error_msg = f"ThoughtTrail import failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        result["error"] = f"ImportError: {e}"
    except Exception as e:
        error_msg = f"ThoughtTrail connection failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        traceback.print_exc()
        result["error"] = str(e)
    
    return result


def prime_arche_system(
    project_root: Optional[Path] = None,
    store_globals: bool = False,
    save_results: bool = True
) -> Dict[str, Any]:
    """
    Execute the complete ArchE unified priming sequence per PRIME_ARCHE_PROTOCOL_v3.5-GP.
    
    This is the superior, unified initialization that combines:
    - Full Zepto compression/decompression with file ingestion
    - Auto-ingestion of PRIME protocol
    - Zepto-compressed SPR file handling
    - Protocol chunk loading for ACO
    - Structured logging with immediate feedback
    - Comprehensive results dictionary
    - Optional global namespace storage
    
    Args:
        project_root: Project root directory (defaults to script location)
        store_globals: If True, store initialized objects in global namespace
        save_results: If True, save priming results to JSON file
        
    Returns:
        Dictionary with complete priming results and initialized objects
    """
    if project_root is None:
        project_root = PROJECT_ROOT
    
    print("=" * 80)
    print("ARCHÉ UNIFIED PRIMING SEQUENCE INITIATED")
    print("=" * 80)
    logger.info("=" * 80)
    logger.info("ARCHÉ UNIFIED PRIMING SEQUENCE INITIATED")
    logger.info(f"Protocol: PRIME_ARCHE_PROTOCOL_{PROTOCOL_VERSION}")
    logger.info("Keyholder: B.J. Lewis (IMnDEVmode)")
    logger.info(f"Project Root: {project_root}")
    logger.info(f"Python: {sys.executable}")
    logger.info(f"Virtual Environment: {os.environ.get('VIRTUAL_ENV', 'NOT ACTIVATED')}")
    logger.info("=" * 80)
    
    priming_results = {
        "timestamp": datetime.now().isoformat(),
        "protocol_version": PROTOCOL_VERSION,
        "keyholder": "B.J. Lewis",
        "project_root": str(project_root),
        "python_executable": sys.executable,
        "virtual_env": os.environ.get('VIRTUAL_ENV', None),
        "directives": {},
        "initialized_objects": {}
    }
    
    # ========================================================================
    # DIRECTIVE 0: Virtual Environment Activation (MANDATORY)
    # ========================================================================
    print("\n[DIRECTIVE 0] Virtual Environment Activation (MANDATORY)")
    logger.info("\n[DIRECTIVE 0] Virtual Environment Activation (MANDATORY)")
    venv_result = activate_virtual_environment(project_root)
    priming_results["directives"]["virtual_env"] = venv_result
    
    if venv_result["status"] not in ["activated", "already_activated", "detected"]:
        print_and_log(
            "⚠️  WARNING: Virtual environment activation failed or not found",
            "warning", "⚠️"
        )
        print_and_log("   Continuing with system Python (may cause import errors)", "warning")
    
    # ========================================================================
    # DIRECTIVE 0.1: Zepto Compression/Decompression System
    # ========================================================================
    print("\n[DIRECTIVE 0.1] Zepto Compression/Decompression System Initialization")
    logger.info("\n[DIRECTIVE 0.1] Zepto Compression/Decompression System Initialization")
    zepto_result = initialize_zepto_system(project_root)
    priming_results["directives"]["zepto_system"] = {
        "status": zepto_result["status"],
        "prime_protocol_ingested": zepto_result["prime_protocol_ingested"],
        "compression_ratio": zepto_result["compression_ratio"],
        "error": zepto_result.get("error")
    }
    
    ingest_function = zepto_result.get("ingest_function")
    crystallization_engine = zepto_result.get("engine")
    
    # ========================================================================
    # DIRECTIVE 1: SPR Auto-Priming System
    # ========================================================================
    print("\n[DIRECTIVE 1] SPR Auto-Priming System")
    logger.info("\n[DIRECTIVE 1] SPR Auto-Priming System")
    spr_result = initialize_spr_system(project_root, ingest_function)
    priming_results["directives"]["spr_priming"] = {
        "status": spr_result["status"],
        "sprs_loaded": spr_result["sprs_loaded"],
        "test_priming_count": spr_result["test_priming_count"],
        "error": spr_result.get("error")
    }
    
    spr_manager = spr_result.get("spr_manager")
    
    # ========================================================================
    # DIRECTIVE 2: Session Auto-Capture System
    # ========================================================================
    print("\n[DIRECTIVE 2] Session Auto-Capture System")
    logger.info("\n[DIRECTIVE 2] Session Auto-Capture System")
    session_result = initialize_session_capture(project_root)
    priming_results["directives"]["session_capture"] = {
        "status": session_result["status"],
        "output_dir": session_result["output_dir"],
        "error": session_result.get("error")
    }
    
    session_capture = session_result.get("session_capture")
    
    # ========================================================================
    # DIRECTIVE 3: Autopoietic Learning Loop
    # ========================================================================
    print("\n[DIRECTIVE 3] Autopoietic Learning Loop")
    logger.info("\n[DIRECTIVE 3] Autopoietic Learning Loop")
    learning_result = initialize_learning_loop(project_root)
    priming_results["directives"]["learning_loop"] = {
        "status": learning_result["status"],
        "guardian_review": learning_result["guardian_review"],
        "stardust_captured": learning_result["stardust_captured"],
        "error": learning_result.get("error")
    }
    
    learning_loop = learning_result.get("learning_loop")
    
    # ========================================================================
    # DIRECTIVE 4: ThoughtTrail Monitoring
    # ========================================================================
    print("\n[DIRECTIVE 4] ThoughtTrail Monitoring")
    logger.info("\n[DIRECTIVE 4] ThoughtTrail Monitoring")
    thought_trail_result = initialize_thought_trail(project_root)
    priming_results["directives"]["thought_trail"] = {
        "status": thought_trail_result["status"],
        "trail_length": thought_trail_result["trail_length"],
        "ledger_path": thought_trail_result["ledger_path"],
        "error": thought_trail_result.get("error")
    }
    
    thought_trail = thought_trail_result.get("thought_trail")
    
    # ========================================================================
    # Store initialized objects (if requested)
    # ========================================================================
    if store_globals:
        print("\n💾 Storing initialized systems in global namespace...")
        logger.info("Storing initialized systems in global namespace...")
        
        if crystallization_engine:
            globals()['crystallization_engine'] = crystallization_engine
            priming_results["initialized_objects"]["crystallization_engine"] = "stored"
        
        if spr_manager:
            globals()['spr_manager'] = spr_manager
            priming_results["initialized_objects"]["spr_manager"] = "stored"
        
        if session_capture:
            globals()['session_capture'] = session_capture
            priming_results["initialized_objects"]["session_capture"] = "stored"
        
        if learning_loop:
            globals()['learning_loop'] = learning_loop
            priming_results["initialized_objects"]["learning_loop"] = "stored"
        
        if thought_trail:
            globals()['thought_trail'] = thought_trail
            priming_results["initialized_objects"]["thought_trail"] = "stored"
        
        if ingest_function:
            globals()['ingest_file_with_zepto'] = ingest_function
            priming_results["initialized_objects"]["ingest_file_with_zepto"] = "stored"
        
        print_and_log("✅ Systems stored and ready for use", "info", "✅")
    
    # Store references in results (for programmatic access)
    priming_results["initialized_objects"]["references"] = {
        "crystallization_engine": crystallization_engine is not None,
        "spr_manager": spr_manager is not None,
        "session_capture": session_capture is not None,
        "learning_loop": learning_loop is not None,
        "thought_trail": thought_trail is not None,
        "ingest_file_with_zepto": ingest_function is not None
    }
    
    # ========================================================================
    # PRIMING SEQUENCE COMPLETE
    # ========================================================================
    print("\n" + "=" * 80)
    print("ARCHÉ UNIFIED PRIMING SEQUENCE COMPLETE")
    print("=" * 80)
    logger.info("\n" + "=" * 80)
    logger.info("ARCHÉ UNIFIED PRIMING SEQUENCE COMPLETE")
    logger.info("=" * 80)
    
    # Calculate success summary
    successful = sum(
        1 for d in priming_results["directives"].values()
        if isinstance(d, dict) and d.get("status") in ["initialized", "activated", "connected", "already_activated", "detected"]
    )
    total = len(priming_results["directives"])
    
    print_and_log(f"\nSUMMARY: {successful}/{total} directives successfully initialized", "info")
    
    if successful == total:
        print_and_log("🎉 ALL SYSTEMS ONLINE - ArchE FULLY PRIMED AND OPERATIONAL", "info", "🎉")
        print("\nArchE is now ready for:")
        print("  • Cognitive Resonance operations")
        print("  • SPR-based cognitive activation")
        print("  • Session auto-capture")
        print("  • Autopoietic learning")
        print("  • ThoughtTrail pattern detection")
        print("  • Zepto compression/decompression")
    else:
        print_and_log("⚠️  SOME SYSTEMS OFFLINE - Review errors above", "warning", "⚠️")
        print_and_log("   ArchE may have limited functionality", "warning")
    
    # Save priming results
    if save_results:
        results_file = project_root / "arche_unified_priming_results.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(priming_results, f, indent=2, default=str)
            print_and_log(f"\nPriming results saved to: {results_file}", "info")
        except Exception as e:
            print_and_log(f"⚠️  Warning: Could not save results file: {e}", "warning", "⚠️")
    
    print("\n🚀 ArchE Unified Initialization Complete!")
    logger.info("ArchE Unified Initialization Complete!")
    
    return priming_results


if __name__ == "__main__":
    results = prime_arche_system(store_globals=True, save_results=True)
    
    # Exit with appropriate status code
    all_successful = all(
        isinstance(d, dict) and d.get("status") in ["initialized", "activated", "connected", "already_activated", "detected"]
        for d in results["directives"].values()
    )
    
    sys.exit(0 if all_successful else 1)


