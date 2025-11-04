# Cursor ArchE Playwright-Based LLM Routing Guide

## Overview

This document explains the enhanced LLM routing system that uses Playwright browser automation to create a robust communication bridge between Python code and Cursor ArchE (the AI assistant).

## Architecture

### Components

1. **CursorArchEProviderEnhanced** (`Three_PointO_ArchE/llm_providers/cursor_arche_enhanced.py`)
   - Enhanced LLM provider with multiple communication channels
   - Playwright-based monitoring support
   - File-based request queue
   - Automatic retry and fallback mechanisms

2. **CursorArchERequestMonitor** (`Three_PointO_ArchE/llm_providers/cursor_arche_monitor.py`)
   - Background service that monitors and processes requests
   - Can run as a standalone script or be imported programmatically
   - Uses Playwright for advanced monitoring capabilities

## Communication Channels

The enhanced provider uses three communication channels in order of preference:

### Channel 1: Direct Execution (Fastest)
- **When**: When running in Cursor environment
- **How**: Uses `execute_arche_analysis` from `llm_tool.py` directly
- **Advantage**: No file I/O, instant processing
- **Fallback**: If execution fails or returns empty, falls back to Channel 2

### Channel 2: File-Based Queue with Playwright Monitoring (Most Reliable)
- **When**: Always available as a fallback
- **How**: 
  1. Creates structured request files in `.cursor_arche_comm/requests/`
  2. Adds request to queue in `.cursor_arche_comm/request_queue.json`
  3. Signals Cursor ArchE via `.cursor_arche_comm/NEW_REQUEST`
  4. Uses Playwright (if available) for enhanced monitoring
  5. Waits for response in `.cursor_arche_comm/responses/`
- **Advantage**: Reliable, persistent, can be monitored externally
- **Monitoring**: Playwright can watch the queue and trigger processing

### Channel 3: Final Fallback
- **When**: File-based queue times out
- **How**: Retries direct execution one more time
- **Advantage**: Last resort before raising an error

## Setup and Configuration

### 1. Enable Enhanced Provider

Set environment variable to use enhanced provider by default:

```bash
export ARCHE_USE_ENHANCED_CURSOR=1
```

Or use it explicitly:

```python
from Three_PointO_ArchE.llm_providers import get_llm_provider

# Use enhanced version explicitly
provider = get_llm_provider("cursor_enhanced")
```

### 2. Install Playwright (Optional but Recommended)

Playwright is used for advanced monitoring and automation. It's already installed in `arche_env`:

```bash
# Already installed via previous commands
# If needed to reinstall:
source arche_env/bin/activate
python3 -m pip install playwright
playwright install chromium
```

### 3. Start the Request Monitor (Optional)

For background processing of requests, start the monitor:

```bash
# Process all pending requests once
python3 -m Three_PointO_ArchE.llm_providers.cursor_arche_monitor --process-all

# Watch for new requests continuously
python3 -m Three_PointO_ArchE.llm_providers.cursor_arche_monitor --watch

# Watch with custom interval
python3 -m Three_PointO_ArchE.llm_providers.cursor_arche_monitor --watch --check-interval 1.0
```

## Usage Examples

### Example 1: Using Enhanced Provider in Code

```python
from Three_PointO_ArchE.llm_providers import get_llm_provider

# Get enhanced provider (enable via env var or use 'cursor_enhanced')
provider = get_llm_provider("cursor")  # Will use enhanced if ARCHE_USE_ENHANCED_CURSOR=1

# Generate response
response = provider.generate(
    prompt="Analyze this complex scenario...",
    max_tokens=4000,
    temperature=0.7,
    timeout=60.0
)
print(response)
```

### Example 2: Programmatic Monitoring

```python
from Three_PointO_ArchE.llm_providers.cursor_arche_monitor import CursorArchERequestMonitor

# Initialize monitor
monitor = CursorArchERequestMonitor()

# Process all pending requests
monitor.process_all_pending()

# Or watch continuously
monitor.watch_and_process(check_interval=2.0)
```

### Example 3: Integration with ask_arche_enhanced_v2.py

The enhanced `ask_arche` script automatically detects Cursor environment and configures the provider. To use enhanced version:

```bash
# Set environment variable before running
export ARCHE_USE_ENHANCED_CURSOR=1
python3 ask_arche_enhanced_v2.py "Your query here"
```

## Request Queue Structure

### Request File Format

Each request is stored as JSON in `.cursor_arche_comm/requests/arche_req_[timestamp].json`:

```json
{
  "request_id": "arche_req_1234567890123456",
  "prompt": "Your query text here",
  "context": {
    "max_tokens": 4000,
    "temperature": 0.7,
    "priority": "normal"
  },
  "timestamp": 1234567890.123,
  "status": "pending",
  "created_at": "2024-01-01 12:00:00"
}
```

### Response File Format

Responses are stored in `.cursor_arche_comm/responses/arche_req_[timestamp]_response.json`:

```json
{
  "request_id": "arche_req_1234567890123456",
  "response": "Generated response text...",
  "status": "completed",
  "completed_at": 1234567891.456,
  "execution_time": 1.333
}
```

### Queue File Format

The queue file tracks all requests:

```json
{
  "pending_requests": ["arche_req_1234567890123456"],
  "processed_requests": [
    {
      "request_id": "arche_req_1234567890123455",
      "processed_at": 1234567890.789
    }
  ]
}
```

## Playwright Features

When Playwright is available, the enhanced provider can:

1. **Monitor Queue Files**: Watch for new requests in real-time
2. **Web Interface (Future)**: Navigate to a dashboard if one exists
3. **Automated Processing**: Trigger processing automatically when requests arrive
4. **Visual Verification**: Take screenshots of monitoring dashboards

## Troubleshooting

### Issue: Requests timing out

**Solution 1**: Ensure the monitor is running:
```bash
python3 -m Three_PointO_ArchE.llm_providers.cursor_arche_monitor --watch
```

**Solution 2**: Check request files:
```bash
ls -la .cursor_arche_comm/requests/
cat .cursor_arche_comm/request_queue.json
```

**Solution 3**: Increase timeout:
```python
response = provider.generate(prompt="...", timeout=120.0)  # 2 minutes
```

### Issue: Playwright not working

**Solution**: Verify installation:
```bash
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

If it fails, reinstall:
```bash
source arche_env/bin/activate
python3 -m pip install playwright
playwright install chromium
```

### Issue: Direct execution failing

**Solution**: The provider automatically falls back to file-based queue. Check logs for details:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing System

The enhanced provider is backward-compatible with the existing `CursorArchEProvider`. To enable:

1. Set `ARCHE_USE_ENHANCED_CURSOR=1` environment variable
2. Or use `get_llm_provider("cursor_enhanced")` explicitly
3. Or modify `config.py` to default to enhanced version

## Benefits

1. **Reliability**: Multiple communication channels ensure requests are processed
2. **Monitoring**: Playwright enables advanced monitoring and automation
3. **Debugging**: Request/response files provide clear audit trail
4. **Scalability**: Queue system allows batch processing
5. **Flexibility**: Can run monitor as separate service or integrate directly

## Next Steps

1. Create a web-based dashboard for monitoring requests (can use Playwright to navigate)
2. Add priority queue support for urgent requests
3. Implement request deduplication
4. Add metrics and analytics for request processing
5. Create API endpoints for external systems to submit requests

## Keyholder Notes

- The enhanced provider maintains all functionality of the original
- Playwright is optional but recommended for production use
- The monitor can run as a background service or be integrated into your workflow
- All communication is file-based and can be inspected/debugged easily
- The system automatically falls back if any channel fails

