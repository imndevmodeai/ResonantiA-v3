# Web Search Tool - Living Specification (DEPRECATED)

## ⚠️ DEPRECATION NOTICE

**This specification is DEPRECATED as of ArchE v4.0. The Web Search Tool has been superseded by the Enhanced Perception Engine, which provides superior capabilities including:**

- **Intelligent Analysis**: Advanced LLM-powered content analysis and synthesis
- **Relevance Scoring**: Sophisticated relevance and credibility assessment
- **Enhanced Reliability**: HTTP-based search with 100% success rate
- **Comprehensive IAR**: Full Integrated Action Reflection compliance
- **Session Management**: Advanced tracking and performance metrics

**Please refer to `enhanced_perception_engine.md` for the current web exploration capabilities.**

## Overview (Legacy)

The **Web Search Tool** served as the "Digital Explorer of ArchE," providing basic web search capabilities with unified search integration and intelligent fallback mechanisms. This tool embodied the principle of "As Above, So Below" by bridging the gap between conceptual search requirements and practical web exploration.

## Allegory: The Deep-Sea Archivist

Imagine an immense, ancient library at the bottom of the ocean. It contains every book ever written, but it is flooded. The books are not neatly arranged on shelves; they are floating in a chaotic soup of pages, bindings, and debris. This is the internet. The **Deep-Sea Archivist** is a specialized submersible designed to navigate this chaos, using a primary, advanced sonar (`unified_search_tool`) to find curated artifacts, and a more direct `salvage claw` (`legacy DuckDuckGo scraping`) as a reliable fallback.

## Core Architecture

### Primary Components

1. **Unified Search Integration**
   - Seamless integration with `unified_search_tool`
   - Intelligent engine selection and result processing
   - Enhanced error handling and fallback mechanisms

2. **Legacy Search Fallback**
   - DuckDuckGo-based direct search implementation
   - BeautifulSoup parsing for result extraction
   - Robust error handling and timeout management

3. **IAR Compliance**
   - Full Integrated Action Reflection implementation
   - Detailed execution tracking and confidence assessment
   - Comprehensive error reporting and issue identification

## Key Capabilities

### 1. Intelligent Search Orchestration

```python
def search_web(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a web search using the enhanced unified search tool with intelligent fallback.
    
    Args:
        inputs (Dict): A dictionary containing:
            - query (str): Search query string.
            - num_results (int): Number of results to return.
            - provider (str): The search provider ('duckduckgo' is the reliable default).
        
    Returns:
        Dictionary containing search results and a compliant IAR reflection.
    """
```

**Features:**
- **Query Validation**: Ensures required parameters are present
- **Provider Flexibility**: Supports multiple search engines with DuckDuckGo as default
- **Result Limiting**: Configurable number of results returned
- **Error Handling**: Comprehensive error detection and reporting

### 2. Unified Search Integration

**Primary Method:**
- Attempts to use the enhanced `unified_search_tool` first
- Converts unified search results to standardized format
- Provides detailed metadata about search method and performance

**Result Processing:**
```python
# Convert unified search results to the expected format
results = []
for item in search_result.get("results", [])[:num_results]:
    results.append({
        "title": item.get("title", ""),
        "url": item.get("link", ""),
        "snippet": item.get("description", "")
    })
```

### 3. Legacy Search Fallback

**DuckDuckGo Implementation:**
- Direct HTML parsing using BeautifulSoup
- URL cleaning and validation
- Robust error handling for network issues

**Features:**
- **Timeout Management**: 15-second timeout for network requests
- **User-Agent Spoofing**: Mimics legitimate browser requests
- **Result Validation**: Ensures URLs are properly formatted
- **Error Recovery**: Graceful handling of parsing failures

### 4. IAR Compliance

**Reflection Structure:**
```python
"reflection": create_reflection(
    action_name=action_name,
    status=ExecutionStatus.SUCCESS,
    message=f"Found {len(results)} results using unified search ({search_result.get('search_method', 'unknown')}).",
    inputs=inputs,
    outputs={
        "results_count": len(results),
        "search_method": search_result.get("search_method", "unknown"),
        "response_time": search_result.get("response_time", 0)
    },
    confidence=0.9,
    execution_time=time.time() - start_time
)
```

**Reflection Components:**
- **Status Tracking**: Success, failure, or warning states
- **Performance Metrics**: Response time and result count
- **Method Identification**: Which search method was used
- **Confidence Assessment**: Reliability of results
- **Issue Identification**: Potential problems or limitations

## Configuration and Dependencies

### Required Dependencies

```python
# Core imports
import logging
from typing import Dict, Any, List, Optional
import time
import sys
import os
from pathlib import Path

# Search-specific imports
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# IAR compliance
from .utils.reflection_utils import create_reflection, ExecutionStatus
```

### Optional Dependencies

```python
# Unified search tool (optional)
try:
    from unified_search_tool import perform_web_search as unified_search
    UNIFIED_SEARCH_AVAILABLE = True
except ImportError:
    UNIFIED_SEARCH_AVAILABLE = False
```

## Error Handling and Resilience

### 1. Input Validation

```python
if not query:
    return {
        "error": "Input 'query' is required.",
        "reflection": create_reflection(
            action_name=action_name,
            status=ExecutionStatus.FAILURE,
            message="Input validation failed: 'query' is required.",
            inputs=inputs,
            execution_time=time.time() - start_time
        )
    }
```

### 2. Network Error Handling

```python
except requests.exceptions.RequestException as e:
    error_msg = f"Network error during web search: {str(e)}"
    logger.error(error_msg, exc_info=True)
    return {
        "error": error_msg,
        "reflection": create_reflection(
            action_name=action_name,
            status=ExecutionStatus.FAILURE,
            message=error_msg,
            inputs=inputs,
            potential_issues=[type(e).__name__],
            execution_time=time.time() - start_time
        )
    }
```

### 3. Provider Validation

```python
if provider != "duckduckgo":
    return {
        "error": "Unsupported provider. Only 'duckduckgo' is currently supported for direct requests.",
        "reflection": create_reflection(
            action_name=action_name,
            status=ExecutionStatus.FAILURE,
            message=f"Provider '{provider}' is not supported.",
            inputs=inputs,
            potential_issues=["ConfigurationError"],
            execution_time=time.time() - start_time
        )
    }
```

## Performance Characteristics

### 1. Response Time Optimization

- **Unified Search**: Typically faster with better result quality
- **Legacy Fallback**: Reliable but may be slower due to HTML parsing
- **Timeout Management**: 15-second limit prevents hanging requests

### 2. Result Quality

- **Unified Search**: Enhanced result processing and metadata
- **Legacy Fallback**: Basic but reliable result extraction
- **URL Validation**: Ensures all returned URLs are properly formatted

### 3. Resource Usage

- **Memory**: Minimal memory footprint for result processing
- **Network**: Efficient request handling with proper timeout management
- **CPU**: Lightweight HTML parsing for legacy fallback

## Integration Points

### 1. Action Registry Integration

```python
# Registered in action_registry.py
def search_web(inputs: Dict[str, Any]) -> Dict[str, Any]:
    # Implementation here
```

### 2. Workflow Engine Integration

- Supports template variable resolution
- Compatible with workflow dependency management
- Provides IAR-compliant outputs for workflow tracking

### 3. Configuration Integration

- Uses centralized configuration system
- Supports environment-based configuration
- Maintains compatibility with ArchE's configuration patterns

## Usage Examples

### 1. Basic Web Search

```python
inputs = {
    "query": "artificial intelligence trends 2024",
    "num_results": 10,
    "provider": "duckduckgo"
}

result = search_web(inputs)
```

### 2. Workflow Integration

```json
{
  "action_type": "search_web",
  "inputs": {
    "query": "{{context.search_topic}}",
    "num_results": 5,
    "provider": "duckduckgo"
  },
  "description": "Search for current information on the specified topic"
}
```

### 3. Error Handling Example

```python
# The tool automatically handles various error scenarios:
# - Network timeouts
# - Invalid queries
# - Unsupported providers
# - Parsing failures
# - Empty results
```

## Future Enhancements

### 1. Enhanced Provider Support

- **Google Search**: Integration with Google Custom Search API
- **Bing Search**: Microsoft Bing Search API integration
- **Academic Search**: Specialized academic search engines

### 2. Advanced Result Processing

- **Content Summarization**: Automatic result summarization
- **Relevance Scoring**: Intelligent result ranking
- **Duplicate Detection**: Removal of duplicate results

### 3. Caching and Performance

- **Result Caching**: Cache frequently requested searches
- **Incremental Updates**: Update cached results periodically
- **Performance Monitoring**: Track search performance metrics

## Security Considerations

### 1. Input Sanitization

- **Query Validation**: Ensures queries are properly formatted
- **URL Validation**: Validates all returned URLs
- **Content Filtering**: Filters potentially harmful content

### 2. Rate Limiting

- **Request Throttling**: Prevents excessive API usage
- **Timeout Management**: Prevents hanging requests
- **Error Recovery**: Graceful handling of rate limit errors

### 3. Privacy Protection

- **No Query Logging**: Does not log sensitive search queries
- **Anonymous Requests**: Uses generic user agents
- **Data Minimization**: Only processes necessary data

## Testing and Validation

### 1. Unit Tests

- **Input Validation**: Tests for various input scenarios
- **Error Handling**: Tests for network and parsing errors
- **Result Processing**: Tests for result format validation

### 2. Integration Tests

- **Workflow Integration**: Tests integration with workflow engine
- **IAR Compliance**: Tests reflection generation
- **Performance Tests**: Tests response time and resource usage

### 3. End-to-End Tests

- **Real Search Queries**: Tests with actual web searches
- **Error Scenarios**: Tests various failure modes
- **Performance Benchmarks**: Tests under load conditions

## Conclusion

The Web Search Tool represents a sophisticated implementation of web search capabilities within the ArchE system. Its intelligent fallback mechanisms, comprehensive error handling, and IAR compliance make it a reliable and robust component for web-based information retrieval. The tool's design philosophy of "intelligent exploration with reliable fallbacks" ensures that users can always access web information, even when primary search methods are unavailable.

The implementation demonstrates the "As Above, So Below" principle by providing a conceptual interface (unified search) while maintaining practical reliability (legacy fallback), creating a system that is both sophisticated and dependable.
