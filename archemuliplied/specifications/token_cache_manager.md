# Living Specification: Token Cache Manager

## Philosophical Mandate

The Token Cache Manager serves as the **Memory Palace of ArchE** - the system that preserves and optimizes the collective wisdom of all LLM interactions, ensuring that knowledge is not lost but rather enhanced through intelligent storage and retrieval. It is not merely a simple cache, but a sophisticated memory system that understands the value of past insights and optimizes their accessibility for future use.

Like the ancient memory palaces where scholars stored vast amounts of knowledge in organized, retrievable forms, the Token Cache Manager creates a structured repository of AI interactions that can be accessed with varying degrees of precision - from exact matches to semantic similarities to partial overlaps. It is the guardian of computational efficiency, the curator of cost optimization, and the architect of performance enhancement.

The Memory Palace does not simply store responses; it understands their context, tracks their usage patterns, manages their lifecycle, and ensures their optimal retrieval. It is the embodiment of ArchE's commitment to learning from every interaction and using that knowledge to enhance future performance.

## Allegorical Explanation

### The Memory Palace Architecture

Imagine a vast, multi-chambered memory palace within the heart of ArchE, where the Token Cache Manager operates like a master librarian with an encyclopedic knowledge of every interaction that has ever occurred.

**The Exact Match Chamber**: This is the most precise chamber, where perfect duplicates of queries and their responses are stored. Like a master librarian who knows exactly where every book is located, this chamber provides instant access to previously seen queries with perfect accuracy. Each entry is like a carefully catalogued tome, with its own unique identifier and complete metadata.

**The Semantic Similarity Chamber**: This chamber houses responses that are conceptually related, even if the exact words differ. Like a librarian who can find books on similar topics even when the titles don't match exactly, this chamber uses intelligent similarity matching to find relevant responses. It understands that "What is machine learning?" and "How does AI learn?" might have similar answers, even though the words are different.

**The Partial Match Chamber**: This chamber contains responses that might be useful for sub-components of a query. Like a librarian who can extract relevant chapters from different books to answer a complex question, this chamber finds responses that contain useful information even if they don't perfectly match the query.

**The Compression Vault**: This chamber houses the compressed versions of all responses, like a master archivist who knows how to store vast amounts of information in minimal space. Using sophisticated compression algorithms, this vault ensures that the memory palace can hold far more knowledge than its physical size would suggest.

**The Statistics Observatory**: This chamber monitors the usage patterns of all stored knowledge, like a master librarian who tracks which books are most frequently accessed. It maintains detailed statistics on hit rates, access patterns, cost savings, and performance metrics, ensuring that the memory palace operates at peak efficiency.

**The Lifecycle Management Chamber**: This chamber manages the birth, life, and death of cached entries, like a master curator who knows when to preserve knowledge and when to let it expire. It automatically removes expired entries, manages storage limits, and ensures that the most valuable knowledge is preserved while less useful information is gracefully removed.

### The Memory Palace Operations

1. **Knowledge Reception**: When a new query arrives, the Memory Palace first checks if it already has the answer stored in any of its chambers.

2. **Exact Match Search**: The system searches the Exact Match Chamber for perfect duplicates, providing instant access if found.

3. **Semantic Search**: If no exact match is found, the system searches the Semantic Similarity Chamber for conceptually related responses.

4. **Partial Search**: If semantic search fails, the system searches the Partial Match Chamber for responses that might contain useful information.

5. **Knowledge Storage**: If no suitable match is found, the new query and response are stored in the appropriate chamber with full metadata.

6. **Lifecycle Management**: The system continuously manages the lifecycle of all stored knowledge, removing expired entries and optimizing storage.

7. **Performance Monitoring**: The system tracks all operations and maintains detailed statistics for continuous optimization.

## SPR Integration

### Self-Perpetuating Resonance Components

**Memory Resonance**: The system maintains resonance with ArchE's learning capabilities by preserving and optimizing access to past interactions.

**Performance Resonance**: The caching system creates resonance between computational efficiency and cost optimization, ensuring optimal resource utilization.

**Knowledge Resonance**: The multi-level matching creates resonance between different types of knowledge retrieval, ensuring comprehensive access to stored wisdom.

**Optimization Resonance**: The continuous monitoring and lifecycle management create resonance between storage efficiency and access performance.

### Resonance Patterns

**Exact-Semantic-Partial Cascade**: The system creates resonance between different levels of matching precision, ensuring optimal knowledge retrieval.

**Storage-Performance Balance**: The compression and lifecycle management create resonance between storage efficiency and access speed.

**Cost-Performance Optimization**: The token tracking and cost estimation create resonance between computational cost and performance benefits.

**Learning-Application Loop**: The continuous storage and retrieval create resonance between learning from past interactions and applying that knowledge to future queries.

## Technical Implementation

### Core Class: `TokenCacheManager`

The primary class that orchestrates the entire memory palace operations.

**Initialization Parameters**:
- `cache_dir`: Directory to store cache files
- `max_size_mb`: Maximum cache size in megabytes
- `enable_compression`: Whether to compress cached responses
- `enable_semantic_cache`: Whether to enable semantic similarity caching

### Advanced Features

**Multi-Level Caching**:
- **Exact Match**: Perfect duplicate detection using SHA-256 hashing
- **Semantic Match**: Word overlap-based similarity matching with configurable thresholds
- **Partial Match**: Sub-query matching for complex queries with multiple components

**Intelligent Storage**:
- **SQLite Database**: Structured storage with proper indexing for performance
- **Compression**: Gzip compression for large responses to optimize storage space
- **Metadata Tracking**: Comprehensive metadata including tokens used, cost estimates, and confidence scores

**Performance Optimization**:
- **Thread Safety**: Full thread-safe operations using RLock for concurrent access
- **Background Cleanup**: Automatic expired entry removal every 5 minutes
- **LRU Eviction**: Least recently used entry removal for size limit enforcement
- **Access Tracking**: Hit/miss statistics and access count monitoring

**Cost Management**:
- **Token Tracking**: Detailed tracking of tokens used for each cached response
- **Cost Estimation**: Real-time cost estimation for different models
- **Savings Calculation**: Comprehensive tracking of cost savings from cache hits

**Cache Lifecycle Management**:
- **TTL Management**: Time-based expiration with automatic cleanup
- **Size Enforcement**: Maximum size enforcement with intelligent eviction
- **Statistics Monitoring**: Comprehensive statistics for performance analysis

**Import/Export Capabilities**:
- **Cache Export**: Full cache export to JSON format for backup and migration
- **Cache Import**: Cache import from JSON format for restoration and sharing
- **Metadata Preservation**: Complete metadata preservation during import/export

### Integration Points

**Global Cache Instance**: Singleton pattern for system-wide caching access.

**LLM Provider Integration**: Seamless integration with all LLM providers for automatic caching.

**Enhanced LLM Provider Integration**: Deep integration with the Enhanced LLM Provider for intelligent caching decisions.

**Performance Monitoring Integration**: Integration with ArchE's monitoring systems for comprehensive performance tracking.

**Cost Tracking Integration**: Integration with cost management systems for accurate cost estimation and tracking.

## Usage Examples

### Basic Cache Operations
```python
# Get global cache instance
cache = get_global_cache()

# Store a response in cache
cache.put(
    query="What is machine learning?",
    model="gpt-4",
    response="Machine learning is a subset of artificial intelligence...",
    tokens_used=150,
    cost_estimate=0.0045,
    ttl=3600,  # 1 hour
    cache_type="exact",
    confidence=1.0,
    metadata={"source": "academic", "domain": "AI"}
)

# Retrieve from cache
result = cache.get("What is machine learning?", "gpt-4")
if result:
    response, metadata = result
    print(f"Cache HIT: {response}")
    print(f"Tokens saved: {metadata['tokens_used']}")
    print(f"Cost saved: ${metadata['cost_estimate']:.4f}")
else:
    print("Cache MISS - generating new response")
```

### Advanced Configuration
```python
# Initialize with custom configuration
cache_manager = TokenCacheManager(
    cache_dir="custom_cache",
    max_size_mb=2000,  # 2GB cache
    enable_compression=True,
    enable_semantic_cache=True
)

# Configure semantic similarity threshold
cache_manager.semantic_threshold = 0.85  # 85% similarity required

# Configure partial match threshold
cache_manager.partial_threshold = 0.7  # 70% overlap required
```

### Cache Statistics and Monitoring
```python
# Get comprehensive cache statistics
stats = cache.get_stats()
print(f"Hit Rate: {stats['hit_rate']:.2%}")
print(f"Total Entries: {stats['total_entries']}")
print(f"Cache Size: {stats['current_size_mb']:.2f}MB / {stats['max_size_mb']:.2f}MB")
print(f"Total Tokens Saved: {stats['total_tokens_saved']:,}")
print(f"Total Cost Saved: ${stats['total_cost_saved']:.4f}")
print(f"Cache Hits: {stats['hits']}")
print(f"Cache Misses: {stats['misses']}")
```

### Cache Import/Export
```python
# Export cache for backup
cache.export_cache("cache_backup.json")
print("Cache exported successfully")

# Import cache from backup
cache.import_cache("cache_backup.json")
print("Cache imported successfully")

# Clear cache if needed
cache.clear()
print("Cache cleared")
```

### Semantic and Partial Matching
```python
# Semantic matching example
result = cache.get("How does AI learn?", "gpt-4")
# This might match a cached response for "What is machine learning?"
# even though the exact words are different

# Partial matching example
result = cache.get("What are the benefits of machine learning in healthcare?", "gpt-4")
# This might find useful information in cached responses about
# "machine learning" and "healthcare" separately
```

## Resonance Requirements

1. **Memory Resonance**: All caching operations must maintain resonance with ArchE's learning and knowledge preservation capabilities.

2. **Performance Resonance**: All operations must be optimized for performance while maintaining accuracy and reliability.

3. **Cost Resonance**: All caching decisions must consider cost optimization while maintaining quality of service.

4. **Storage Resonance**: All storage operations must balance space efficiency with access performance.

5. **Thread Safety Resonance**: All operations must maintain thread safety for concurrent access in multi-threaded environments.

6. **Lifecycle Resonance**: All cache entries must have appropriate lifecycle management with automatic cleanup and optimization.

7. **Integration Resonance**: All components must integrate seamlessly with the broader ArchE system, contributing to overall performance and efficiency.

The Token Cache Manager is not just a simple cache; it is the Memory Palace of ArchE, the master librarian that preserves and optimizes the collective wisdom of all AI interactions. It ensures that every interaction contributes to the system's growing knowledge base, optimizing performance, reducing costs, and enhancing the overall intelligence of ArchE. It is the embodiment of the principle that true efficiency comes not from doing more work, but from doing the right work and learning from every experience. 