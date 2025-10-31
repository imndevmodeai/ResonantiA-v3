# 🚀 Unified Search Engine - Mastermind.interact Integration

## 📋 Overview

The Unified Search Engine combines the best features from all analyzed Puppeteer scripts into a single, powerful search solution with seamless integration into mastermind.interact. It features advanced anti-detection, human CAPTCHA handoff, multi-engine support, and comprehensive error handling.

## ✨ Key Features

### 🔍 **Multi-Engine Support**
- **Google Search** - With advanced CAPTCHA detection and consent handling
- **DuckDuckGo** - Fast and reliable alternative
- **Bing** - Additional search engine option
- **Parallel Execution** - Search multiple engines simultaneously

### 🛡️ **Advanced Anti-Detection**
- **Stealth Plugins** - Uses `puppeteer-extra-plugin-stealth` and `puppeteer-extra-plugin-anonymize-ua`
- **Browser Fingerprinting** - Removes automation indicators
- **Realistic User Agents** - Configurable user agent strings
- **Session Management** - Unique user data directories per session

### 🤝 **Human CAPTCHA Handoff**
- **Automatic Detection** - Detects reCAPTCHA, unusual traffic, and blocking
- **Interactive Mode** - Switches to non-headless mode for human solving
- **Automatic Resumption** - Continues search after CAPTCHA is solved
- **Timeout Management** - Configurable handoff timeouts

### 🧠 **Learning Mode**
- **Click Detection** - Captures user clicks for selector learning
- **Selector Discovery** - Helps identify new page elements
- **Debug Information** - Detailed logging for troubleshooting

### 📊 **Result Analysis**
- **Duplicate Removal** - Removes duplicate results across engines
- **Result Comparison** - Compares results from different engines
- **Statistics** - Provides search statistics and success rates
- **Caching** - Caches results for improved performance

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Mastermind.interact                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Python Wrapper Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Search Handler  │  │ Cache Manager   │  │ Result       │ │
│  │                 │  │                 │  │ Formatter    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              JavaScript Engine Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Unified Search  │  │ CAPTCHA Handler │  │ Result       │ │
│  │ Engine          │  │                 │  │ Extractor    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Browser Automation Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Puppeteer Core  │  │ Stealth Plugins │  │ Chrome       │ │
│  │                 │  │                 │  │ Browser      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. **Installation**

```bash
# Install Node.js dependencies
npm install puppeteer-core puppeteer-extra puppeteer-extra-plugin-stealth puppeteer-extra-plugin-anonymize-ua

# Install Python dependencies
pip install asyncio
```

### 2. **Basic Usage**

```python
from unified_search_python import mastermind_search_sync

# Simple search
results = mastermind_search_sync(
    query="quantum computing applications",
    engines=['duckduckgo', 'google'],
    use_handoff=True
)

print(f"Found {len(results['results'])} results")
```

### 3. **Advanced Usage**

```python
from unified_search_python import MastermindSearchIntegration

# Create integration with custom config
integration = MastermindSearchIntegration({
    'debug': True,
    'enable_human_handoff': True,
    'headless': False,
    'timeout': 300,
    'max_results': 10
})

# Perform search
results = await integration.search(
    query="AI trends 2024",
    engines=['google', 'duckduckgo', 'bing'],
    use_handoff=True
)
```

## 🔧 Configuration Options

### **JavaScript Engine Options**

```javascript
const options = {
    headless: false,                    // Run browser in headless mode
    debug: true,                        // Enable debug logging
    timeout: 30000,                     // Search timeout in milliseconds
    maxResults: 10,                     // Maximum results per engine
    userAgent: 'Custom User Agent',     // Custom user agent string
    viewport: { width: 1920, height: 1080 }, // Browser viewport
    chromePath: '/usr/bin/google-chrome-stable', // Chrome executable path
    enableStealth: true,                // Enable stealth plugins
    enableHumanHandoff: true,           // Enable CAPTCHA handoff
    handoffTimeout: 300000,             // Handoff timeout (5 minutes)
    resultsDir: './search_results'      // Results directory
};
```

### **Python Wrapper Options**

```python
config = {
    'debug': True,                      # Enable debug mode
    'enable_human_handoff': True,       # Enable CAPTCHA handoff
    'headless': False,                  # Run in headless mode
    'timeout': 300,                     # Timeout in seconds
    'max_results': 10                   # Maximum results per engine
}
```

## 🔄 CAPTCHA Handoff Process

### **Automatic Detection**
1. **reCAPTCHA Detection** - Identifies reCAPTCHA iframes and elements
2. **Unusual Traffic Detection** - Detects "About this page" blocks
3. **Blocking Detection** - Identifies various blocking mechanisms

### **Human Handoff**
1. **Mode Switch** - Switches to non-headless mode
2. **User Notification** - Informs user about CAPTCHA challenge
3. **Wait Period** - Waits for human to solve CAPTCHA
4. **Automatic Resumption** - Continues search after solution

### **Example Handoff Flow**

```python
# Search with automatic handoff
results = await integration.search(
    query="sensitive search term",
    engines=['google'],
    use_handoff=True  # Will automatically handle CAPTCHAs
)

# If CAPTCHA is detected:
# 1. Browser window opens
# 2. User solves CAPTCHA
# 3. Search automatically resumes
# 4. Results are returned
```

## 📊 Result Format

### **Success Response**

```json
{
    "success": true,
    "query": "quantum computing",
    "results": [
        {
            "title": "Quantum Computing Applications",
            "link": "https://example.com/quantum",
            "description": "Overview of quantum computing applications...",
            "source_engine": "google"
        }
    ],
    "statistics": {
        "total_results": 15,
        "engine_stats": {
            "google": {"count": 10, "status": "success"},
            "duckduckgo": {"count": 5, "status": "success"}
        },
        "engines_used": ["google", "duckduckgo"]
    },
    "metadata": {
        "timestamp": 1640995200,
        "use_handoff": true,
        "config": {...}
    },
    "suggestions": [
        "Try searching for \"quantum\"",
        "Try searching for \"computing\""
    ]
}
```

### **Error Response**

```json
{
    "success": false,
    "error": "CAPTCHA detected but human handoff is disabled",
    "query": "blocked search term",
    "results": [],
    "suggestions": [
        "Try a different search query",
        "Enable human handoff",
        "Use DuckDuckGo instead of Google"
    ]
}
```

## 🔌 Mastermind.interact Integration

### **Direct Integration**

```python
# In your mastermind.interact process
from unified_search_python import mastermind_search_sync

def handle_search_request(user_query: str):
    """Handle search requests from mastermind.interact"""
    
    # Determine search parameters based on query
    if 'google' in user_query.lower():
        engines = ['google']
        use_handoff = True
    else:
        engines = ['duckduckgo', 'google']
        use_handoff = False
    
    # Perform search
    results = mastermind_search_sync(
        query=user_query,
        engines=engines,
        use_handoff=use_handoff,
        config={
            'debug': False,
            'enable_human_handoff': True,
            'headless': not use_handoff,
            'timeout': 120,
            'max_results': 5
        }
    )
    
    return results
```

### **Async Integration**

```python
# For async mastermind.interact processes
from unified_search_python import mastermind_search

async def handle_async_search_request(user_query: str):
    """Handle async search requests"""
    
    results = await mastermind_search(
        query=user_query,
        engines=['duckduckgo', 'google'],
        use_handoff=True,
        config={
            'debug': True,
            'enable_human_handoff': True,
            'headless': False
        }
    )
    
    return results
```

## 🛠️ Advanced Features

### **Learning Mode**

```python
# Enable learning mode for new selectors
integration = MastermindSearchIntegration({'debug': True})

# Enable learning mode
await integration.search_wrapper.enable_learning_mode()

# Perform search - clicks will be logged
results = await integration.search("test query")

# Disable learning mode
await integration.search_wrapper.disable_learning_mode()
```

### **Result Comparison**

```python
# Compare results from multiple engines
results = await integration.search(
    query="AI trends",
    engines=['google', 'duckduckgo', 'bing']
)

# Get comparison analysis
comparison = await integration.search_wrapper.compareResults(results)
print(f"Common results: {len(comparison['common_results'])}")
```

### **Caching**

```python
# Results are automatically cached
handler = MastermindSearchHandler()

# First search
results1 = await handler.handle_search_request("quantum computing")

# Second search (returns cached results)
results2 = await handler.handle_search_request("quantum computing")

# Clear cache
handler.clear_cache()
```

## 📈 Monitoring and Statistics

### **Search Statistics**

```python
integration = MastermindSearchIntegration()

# Perform some searches
await integration.search("query 1")
await integration.search("query 2")

# Get statistics
stats = integration.get_statistics()
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Total searches: {stats['total_searches']}")
```

### **Search History**

```python
# Get search history
history = integration.get_search_history()

for search in history:
    print(f"Query: {search['metadata']['query']}")
    print(f"Timestamp: {search['metadata']['timestamp']}")
    print(f"Engines: {search['metadata']['engines']}")
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Chrome Not Found**
   ```bash
   # Install Chrome
   sudo apt-get install google-chrome-stable
   
   # Or specify custom path
   config = {'chromePath': '/path/to/chrome'}
   ```

2. **CAPTCHA Detection Issues**
   ```python
   # Enable human handoff
   config = {'enable_human_handoff': True, 'headless': False}
   ```

3. **Timeout Issues**
   ```python
   # Increase timeout
   config = {'timeout': 600}  # 10 minutes
   ```

4. **Permission Issues**
   ```bash
   # Fix Chrome permissions
   sudo chmod +x /usr/bin/google-chrome-stable
   ```

### **Debug Mode**

```python
# Enable debug mode for detailed logging
config = {'debug': True}
integration = MastermindSearchIntegration(config)

# Check logs for detailed information
results = await integration.search("test query")
```

## 🔒 Security Considerations

1. **User Data** - Each session uses unique user data directory
2. **Stealth Mode** - Removes automation indicators
3. **Timeout Limits** - Prevents infinite waits
4. **Error Handling** - Graceful failure handling
5. **Resource Cleanup** - Automatic browser cleanup

## 📝 License

This unified search engine is part of the ResonantiA Protocol and follows the same licensing terms.

## 🤝 Contributing

To contribute to the unified search engine:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

## 📞 Support

For support and questions:

1. **Check the troubleshooting section**
2. **Review the example files**
3. **Enable debug mode for detailed logs**
4. **Check the search history for patterns**

---

**🎯 The Unified Search Engine provides the best of all worlds: advanced anti-detection, human CAPTCHA handoff, multi-engine support, and seamless mastermind.interact integration.** 