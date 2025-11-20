# ArchE Interface & Extension Guide

**Version:** 3.5-GP  
**Date:** 2025-11-20  
**Status:** ✅ COMPREHENSIVE GUIDE

---

## 🎯 Part 1: Best Interface to Interact with ArchE

### Overview of Available Interfaces

ArchE provides multiple interfaces for different use cases. Here's a comprehensive comparison:

---

### 🏆 **RECOMMENDED: ArchE Dashboard** (Best Overall)

**Location:** `arche_dashboard/`  
**Type:** Web-based interface  
**Status:** ✅ Production Ready

**Why it's the best:**
- ✅ **Most comprehensive** - All features in one place
- ✅ **Real-time updates** - WebSocket-based live communication
- ✅ **Visual interface** - Thought Trail visualization, statistics, SPR browsing
- ✅ **Conversation mode** - Multi-turn conversations with context retention
- ✅ **No installation needed** - Pure HTML/CSS/JS frontend
- ✅ **Full ArchE capabilities** - Access to all cognitive functions

**Quick Start:**
```bash
cd /mnt/3626C55326C514B1/Happier
./arche_dashboard/start_dashboard.sh
# Then open: file:///mnt/3626C55326C514B1/Happier/arche_dashboard/frontend/index.html
```

**Features:**
1. **Query Interface** - Submit queries with provider/model selection
2. **Thought Trail Visualization** - Timeline view of all cognitive processes
3. **Conversation Mode** - Chat with ArchE with full context
4. **Statistics Dashboard** - Performance metrics and insights
5. **SPR Knowledge Base** - Browse and search SPR definitions

**API Endpoints:**
- `POST /api/query/submit` - Submit queries
- `GET /api/thought-trail/recent` - Get recent entries
- `GET /api/sprs/list` - List all SPRs
- `WS /ws/live` - WebSocket for real-time updates

---

### 🤖 **Natural Language Interface** (Best for CLI)

**Location:** `natural_language_interface.py`  
**Type:** Command-line interface  
**Status:** ✅ Production Ready

**Why use it:**
- ✅ **Simple to use** - Just ask questions in natural language
- ✅ **Automatic parsing** - Converts questions to structured ArchE inputs
- ✅ **Interactive mode** - Supports both one-off and interactive sessions
- ✅ **No server required** - Direct execution

**Usage:**
```bash
# Single question
python natural_language_interface.py "How does ArchE work?"

# Interactive mode
python natural_language_interface.py

# Parse only (see how it's structured)
python natural_language_interface.py "Your question" --parse-only
```

**Simple Wrapper:**
```bash
python ask_arche.py "What are SPRs?"
```

**Features:**
- Parses natural language into structured goals, constraints, and outputs
- Generates ArchE commands automatically
- Supports question classification (implementation, analytical, comparative, etc.)
- Finds relevant specifications automatically

---

### 🔌 **Programmatic Interface** (Best for Integration)

**Location:** `arche_interface.py`  
**Type:** Python async client  
**Status:** ✅ Production Ready

**Why use it:**
- ✅ **Async support** - Non-blocking operations
- ✅ **WebSocket client** - Real-time communication
- ✅ **Easy integration** - Import and use in your code
- ✅ **Status checking** - Get server status programmatically

**Usage:**
```python
import asyncio
from arche_interface import send_query_to_server, get_server_status

# Send a query
async def ask_arche():
    response = await send_query_to_server("Your question here")
    print(response)

# Get server status
async def check_status():
    status = await get_server_status()
    print(status)

asyncio.run(ask_arche())
```

**CLI Usage:**
```bash
python arche_interface.py "Your query here"
python arche_interface.py --status  # Get server status
echo "Your query" | python arche_interface.py --server-mode
```

---

### 📊 **Other Available Interfaces**

1. **Nexus Interface** (`specifications/nexus_interface.md`)
   - FastAPI backend + React frontend
   - More structured API approach
   - WebSocket for real-time streaming

2. **CLI Tools:**
   - `arche_cli.py` - General CLI interface
   - `ask_kg_cli.py` - Knowledge graph queries
   - `guardian_cli.py` - Guardian system interface
   - `keyholder_client.py` - Keyholder-specific client

3. **Direct Processing:**
   - `ask_arche_unified.py` - Unified processor with all features
   - `UnifiedArchEProcessor` class - Programmatic access

---

## 🎯 Part 2: How to Add New Initialization Procedures

### Overview

The `arche_unified_init.py` script provides a clear pattern for adding new initialization directives. This guide shows you how to extend it.

---

### 📋 Understanding the Pattern

The unified initialization system follows this structure:

1. **Individual Initialization Functions** - Each component has its own function
2. **Result Dictionary Pattern** - All functions return structured dictionaries
3. **Main Orchestrator** - `prime_arche_system()` coordinates everything
4. **Error Handling** - Comprehensive error handling and logging
5. **Status Reporting** - Clear status messages and results

---

### 🔧 Step-by-Step: Adding a New Directive

#### Step 1: Create the Initialization Function

Create a function that follows this pattern:

```python
def initialize_your_component(project_root: Path, dependencies: Optional[Any] = None) -> Dict[str, Any]:
    """
    Initialize Your Component System.
    
    Args:
        project_root: Project root directory
        dependencies: Optional dependencies from previous directives
        
    Returns:
        Dictionary with initialization status and component instance
    """
    result = {
        "status": "error",
        "component": None,
        "metric1": 0,
        "metric2": None,
        "error": None
    }
    
    try:
        # Import your component
        from YourModule import YourComponent
        
        # Initialize the component
        component = YourComponent(
            config_path=str(project_root / "path" / "to" / "config.json"),
            # ... other parameters
        )
        
        # Test the component
        test_result = component.test_functionality()
        
        # Log success
        print_and_log("✅ YourComponent initialized", "info", "✅")
        print_and_log(f"   Status: {test_result}", "info")
        print_and_log(f"   Metric: {component.get_metric()}", "info")
        
        # Update result
        result["status"] = "initialized"
        result["component"] = component
        result["metric1"] = component.get_metric()
        result["metric2"] = test_result
        
    except ImportError as e:
        error_msg = f"YourComponent import failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        result["error"] = f"ImportError: {e}"
    except Exception as e:
        error_msg = f"YourComponent initialization failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        traceback.print_exc()
        result["error"] = str(e)
    
    return result
```

#### Step 2: Add to Main Orchestrator

In `prime_arche_system()`, add your directive:

```python
def prime_arche_system(
    project_root: Optional[Path] = None,
    store_globals: bool = False,
    save_results: bool = True
) -> Dict[str, Any]:
    # ... existing code ...
    
    # ========================================================================
    # DIRECTIVE X: Your New Component
    # ========================================================================
    print("\n[DIRECTIVE X] Your New Component System")
    logger.info("\n[DIRECTIVE X] Your New Component System")
    
    # Get dependencies from previous directives if needed
    dependency = previous_result.get("dependency_object")
    
    your_result = initialize_your_component(project_root, dependency)
    priming_results["directives"]["your_component"] = {
        "status": your_result["status"],
        "metric1": your_result["metric1"],
        "metric2": your_result["metric2"],
        "error": your_result.get("error")
    }
    
    your_component = your_result.get("component")
    
    # ... rest of existing code ...
```

#### Step 3: Add Global Storage (Optional)

If you want to store the component in global namespace:

```python
    # In the store_globals section
    if store_globals:
        # ... existing storage code ...
        
        if your_component:
            globals()['your_component'] = your_component
            priming_results["initialized_objects"]["your_component"] = "stored"
```

#### Step 4: Update References

Add to the references dictionary:

```python
    priming_results["initialized_objects"]["references"] = {
        # ... existing references ...
        "your_component": your_component is not None
    }
```

---

### 📝 Complete Example: Adding a New Monitoring System

Here's a complete example of adding a new "Performance Monitor" directive:

```python
def initialize_performance_monitor(project_root: Path) -> Dict[str, Any]:
    """
    Initialize Performance Monitoring System.
    
    Returns:
        Dictionary with initialization status and monitor instance
    """
    result = {
        "status": "error",
        "monitor": None,
        "metrics_tracked": 0,
        "sampling_rate": None,
        "error": None
    }
    
    try:
        from Three_PointO_ArchE.performance_monitor import PerformanceMonitor
        
        # Create config file if missing
        config_path = project_root / "monitoring" / "performance_config.json"
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({
                    "sampling_rate": 1.0,
                    "metrics": ["cpu", "memory", "response_time"]
                }, f)
        
        # Initialize monitor
        monitor = PerformanceMonitor(
            config_path=str(config_path),
            sampling_rate=1.0
        )
        
        # Start monitoring
        monitor.start()
        
        print_and_log("✅ PerformanceMonitor initialized", "info", "✅")
        print_and_log(f"   Metrics tracked: {len(monitor.metrics)}", "info")
        print_and_log(f"   Sampling rate: {monitor.sampling_rate}Hz", "info")
        print_and_log("   Status: Active - Monitoring system performance", "info")
        
        result["status"] = "initialized"
        result["monitor"] = monitor
        result["metrics_tracked"] = len(monitor.metrics)
        result["sampling_rate"] = monitor.sampling_rate
        
    except ImportError as e:
        error_msg = f"PerformanceMonitor import failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        result["error"] = f"ImportError: {e}"
    except Exception as e:
        error_msg = f"PerformanceMonitor initialization failed: {e}"
        print_and_log(f"❌ ERROR: {error_msg}", "error", "❌")
        traceback.print_exc()
        result["error"] = str(e)
    
    return result
```

Then add to `prime_arche_system()`:

```python
    # ========================================================================
    # DIRECTIVE 5: Performance Monitoring System
    # ========================================================================
    print("\n[DIRECTIVE 5] Performance Monitoring System")
    logger.info("\n[DIRECTIVE 5] Performance Monitoring System")
    monitor_result = initialize_performance_monitor(project_root)
    priming_results["directives"]["performance_monitor"] = {
        "status": monitor_result["status"],
        "metrics_tracked": monitor_result["metrics_tracked"],
        "sampling_rate": monitor_result["sampling_rate"],
        "error": monitor_result.get("error")
    }
    
    performance_monitor = monitor_result.get("monitor")
```

---

### 🎨 Best Practices

1. **Follow the Result Dictionary Pattern**
   - Always return a dictionary with `status`, `error`, and component-specific fields
   - Use consistent status values: `"initialized"`, `"error"`, `"connected"`, etc.

2. **Error Handling**
   - Catch `ImportError` separately (indicates missing dependency)
   - Catch general `Exception` for runtime errors
   - Always log errors with `print_and_log()`
   - Use `traceback.print_exc()` for debugging

3. **Logging**
   - Use `print_and_log()` for all messages
   - Include emojis for visual feedback (✅, ❌, ⚠️, 🔄)
   - Log both to console and file

4. **Dependencies**
   - If your component needs something from a previous directive, pass it as a parameter
   - Check for `None` before using dependencies

5. **Testing**
   - Always test your component after initialization
   - Report test results in the status message
   - Include metrics or statistics in the result dictionary

6. **File Creation**
   - Create missing config files automatically
   - Use `mkdir(parents=True, exist_ok=True)` for directories
   - Provide sensible defaults

---

### 📊 Current Directives Reference

The current `arche_unified_init.py` includes:

- **DIRECTIVE 0:** Virtual Environment Activation (MANDATORY)
- **DIRECTIVE 0.1:** Zepto Compression/Decompression System
- **DIRECTIVE 1:** SPR Auto-Priming System
- **DIRECTIVE 2:** Session Auto-Capture System
- **DIRECTIVE 3:** Autopoietic Learning Loop
- **DIRECTIVE 4:** ThoughtTrail Monitoring

**Your new directive should be numbered sequentially (e.g., DIRECTIVE 5, 6, etc.)**

---

### 🔍 Testing Your New Directive

1. **Test the function directly:**
   ```python
   from arche_unified_init import initialize_your_component
   from pathlib import Path
   
   result = initialize_your_component(Path("/mnt/3626C55326C514B1/Happier"))
   print(result)
   ```

2. **Test in the full sequence:**
   ```bash
   python3 arche_unified_init.py
   ```

3. **Check the results file:**
   ```bash
   cat arche_unified_priming_results.json | jq '.directives.your_component'
   ```

---

### 📚 Integration with Other Systems

If your new component needs to integrate with existing systems:

1. **SPR Manager:** Access via `spr_manager` from DIRECTIVE 1
2. **Session Capture:** Access via `session_capture` from DIRECTIVE 2
3. **Learning Loop:** Access via `learning_loop` from DIRECTIVE 3
4. **ThoughtTrail:** Access via `thought_trail` from DIRECTIVE 4
5. **Zepto Engine:** Access via `crystallization_engine` from DIRECTIVE 0.1

Example:
```python
def initialize_your_component(project_root: Path, spr_manager=None, thought_trail=None):
    # Use spr_manager if provided
    if spr_manager:
        spr_manager.scan_and_prime("Your component initialization")
    
    # Use thought_trail if provided
    if thought_trail:
        thought_trail.add_entry(IAREntry(...))
```

---

## 🎯 Summary

### Best Interface Choice:

- **For most users:** Use **ArchE Dashboard** - it's the most comprehensive
- **For CLI users:** Use **Natural Language Interface** - simple and direct
- **For developers:** Use **Programmatic Interface** - easy integration

### Adding New Initialization:

1. Create an initialization function following the pattern
2. Add it to `prime_arche_system()` as a new directive
3. Follow error handling and logging best practices
4. Test thoroughly before committing

---

## 📞 Next Steps

1. **Try the Dashboard:**
   ```bash
   ./arche_dashboard/start_dashboard.sh
   ```

2. **Add Your Component:**
   - Follow the pattern in this guide
   - Test your initialization function
   - Integrate into `prime_arche_system()`

3. **Document Your Component:**
   - Add comments explaining what it does
   - Document any dependencies
   - Include usage examples

---

**Status:** ✅ GUIDE COMPLETE  
**Last Updated:** 2025-11-20  
**Protocol:** PRIME_ARCHE_PROTOCOL_v3.5-GP

