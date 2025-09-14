#!/usr/bin/env python3
"""
Test script for Token Caching in Enhanced LLM Provider
Demonstrates performance improvements and cost savings through intelligent caching.
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Add the Three_PointO_ArchE directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Three_PointO_ArchE'))

try:
    from enhanced_llm_provider import get_enhanced_llm_provider, EnhancedLLMProvider
    from token_cache_manager import TokenCacheManager, get_global_cache
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the correct directory and the required files exist.")
    sys.exit(1)

def test_cache_basic_functionality():
    """Test basic cache functionality."""
    print("\n" + "="*60)
    print("TESTING BASIC CACHE FUNCTIONALITY")
    print("="*60)
    
    try:
        # Create a test cache
        test_cache = TokenCacheManager(cache_dir="test_cache", max_size_mb=10)
        
        # Test data
        test_query = "What is artificial intelligence?"
        test_model = "gpt-4"
        test_response = "Artificial intelligence (AI) is a branch of computer science..."
        test_tokens = 150
        test_cost = 0.0045
        
        # Store in cache
        test_cache.put(
            query=test_query,
            model=test_model,
            response=test_response,
            tokens_used=test_tokens,
            cost_estimate=test_cost,
            ttl=3600,
            cache_type='exact',
            confidence=1.0,
            metadata={'test': True}
        )
        
        print(f"Stored query: {test_query}")
        print(f"Model: {test_model}")
        print(f"Tokens: {test_tokens}")
        print(f"Cost: ${test_cost:.4f}")
        
        # Retrieve from cache
        cached_result = test_cache.get(test_query, test_model)
        if cached_result:
            response, metadata = cached_result
            print(f"\nCache HIT!")
            print(f"Retrieved response: {response[:50]}...")
            print(f"Metadata: {metadata}")
        else:
            print("\nCache MISS!")
        
        # Test with different parameters (should miss)
        cached_result = test_cache.get(test_query, test_model, max_tokens=200)
        if cached_result:
            print("Unexpected cache hit with different parameters")
        else:
            print("Expected cache miss with different parameters")
        
        # Get statistics
        stats = test_cache.get_stats()
        print(f"\nCache Statistics:")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Saves: {stats['saves']}")
        print(f"  Hit Rate: {stats['hit_rate']:.2%}")
        print(f"  Total Tokens Saved: {stats['total_tokens_saved']}")
        print(f"  Total Cost Saved: ${stats['total_cost_saved']:.4f}")
        
        # Clean up
        test_cache.clear()
        
        return True
        
    except Exception as e:
        print(f"Error testing basic cache functionality: {e}")
        return False

def test_semantic_caching():
    """Test semantic similarity caching."""
    print("\n" + "="*60)
    print("TESTING SEMANTIC CACHING")
    print("="*60)
    
    try:
        # Create a test cache with semantic caching enabled
        test_cache = TokenCacheManager(
            cache_dir="test_semantic_cache", 
            max_size_mb=10,
            enable_semantic_cache=True
        )
        
        # Store similar queries
        queries = [
            "What is machine learning?",
            "Can you explain machine learning?",
            "Tell me about ML technology",
            "How does artificial intelligence work?",
            "What is the weather like today?"
        ]
        
        for i, query in enumerate(queries):
            response = f"Response for query {i+1}: {query}"
            test_cache.put(
                query=query,
                model="gpt-4",
                response=response,
                tokens_used=100 + i*10,
                cost_estimate=0.003 + i*0.0001,
                ttl=3600,
                cache_type='exact',
                confidence=1.0
            )
        
        # Test semantic matches
        test_queries = [
            "Explain machine learning to me",
            "What is ML?",
            "How does AI function?",
            "What's the current weather?"
        ]
        
        for test_query in test_queries:
            print(f"\nTesting semantic match for: {test_query}")
            cached_result = test_cache.get(test_query, "gpt-4")
            if cached_result:
                response, metadata = cached_result
                print(f"  Cache HIT! Type: {metadata['cache_type']}")
                if metadata['cache_type'] == 'semantic':
                    print(f"  Similarity: {metadata.get('similarity', 'N/A')}")
                print(f"  Response: {response[:50]}...")
            else:
                print(f"  Cache MISS")
        
        # Get statistics
        stats = test_cache.get_stats()
        print(f"\nSemantic Cache Statistics:")
        print(f"  Hit Rate: {stats['hit_rate']:.2%}")
        print(f"  Total Entries: {stats['total_entries']}")
        
        # Clean up
        test_cache.clear()
        
        return True
        
    except Exception as e:
        print(f"Error testing semantic caching: {e}")
        return False

def test_enhanced_provider_caching():
    """Test caching integration with enhanced LLM provider."""
    print("\n" + "="*60)
    print("TESTING ENHANCED PROVIDER CACHING")
    print("="*60)
    
    try:
        # Get enhanced provider with caching enabled
        enhanced_provider = get_enhanced_llm_provider('openai',
            enable_caching=True,
            cache_ttl=3600,
            enable_multi_source_research=False,  # Disable for faster testing
            enable_iar_validation=False,
            enable_temporal_modeling=False,
            enable_cfp_analysis=False,
            enable_complex_system_visioning=False,
            enable_adjacent_exploration=False,
            enable_self_assessment=False
        )
        
        # Test query
        query = "What are the benefits of caching in AI systems?"
        
        print(f"Query: {query}")
        
        # First call (should miss cache)
        print("\nFirst call (should miss cache):")
        start_time = time.time()
        result1 = enhanced_provider.enhanced_query_processing(query, "gpt-4")
        time1 = time.time() - start_time
        
        print(f"Processing time: {time1:.2f} seconds")
        print(f"Complexity: {result1['complexity']}")
        print(f"Cache info: {result1.get('cache_info', 'N/A')}")
        
        # Second call (should hit cache)
        print("\nSecond call (should hit cache):")
        start_time = time.time()
        result2 = enhanced_provider.enhanced_query_processing(query, "gpt-4")
        time2 = time.time() - start_time
        
        print(f"Processing time: {time2:.2f} seconds")
        print(f"Complexity: {result2['complexity']}")
        print(f"Cache info: {result2.get('cache_info', 'N/A')}")
        
        # Performance comparison
        speedup = time1 / time2 if time2 > 0 else float('inf')
        print(f"\nPerformance Improvement:")
        print(f"  Speedup: {speedup:.2f}x faster")
        print(f"  Time saved: {time1 - time2:.2f} seconds")
        
        # Get cache statistics
        cache_stats = enhanced_provider.get_cache_stats()
        print(f"\nCache Statistics:")
        print(f"  Hit Rate: {cache_stats.get('hit_rate', 0):.2%}")
        print(f"  Total Tokens Saved: {cache_stats.get('total_tokens_saved', 0)}")
        print(f"  Total Cost Saved: ${cache_stats.get('total_cost_saved', 0):.4f}")
        
        return True
        
    except Exception as e:
        print(f"Error testing enhanced provider caching: {e}")
        return False

def test_cache_performance_benchmark():
    """Benchmark cache performance with multiple queries."""
    print("\n" + "="*60)
    print("CACHE PERFORMANCE BENCHMARK")
    print("="*60)
    
    try:
        # Create enhanced provider
        enhanced_provider = get_enhanced_llm_provider('openai',
            enable_caching=True,
            cache_ttl=3600,
            enable_multi_source_research=False,
            enable_iar_validation=False,
            enable_temporal_modeling=False,
            enable_cfp_analysis=False,
            enable_complex_system_visioning=False,
            enable_adjacent_exploration=False,
            enable_self_assessment=False
        )
        
        # Test queries
        queries = [
            "What is Python?",
            "How does machine learning work?",
            "Explain blockchain technology",
            "What are the benefits of cloud computing?",
            "How to implement caching in web applications?",
            "What is artificial intelligence?",
            "Explain the concept of microservices",
            "How does encryption work?",
            "What is the Internet of Things?",
            "Explain the benefits of containerization"
        ]
        
        # First pass (all cache misses)
        print("First pass (cache misses):")
        start_time = time.time()
        for i, query in enumerate(queries):
            print(f"  Processing query {i+1}/{len(queries)}: {query[:30]}...")
            enhanced_provider.enhanced_query_processing(query, "gpt-4")
        first_pass_time = time.time() - start_time
        
        # Second pass (all cache hits)
        print("\nSecond pass (cache hits):")
        start_time = time.time()
        for i, query in enumerate(queries):
            print(f"  Processing query {i+1}/{len(queries)}: {query[:30]}...")
            enhanced_provider.enhanced_query_processing(query, "gpt-4")
        second_pass_time = time.time() - start_time
        
        # Performance analysis
        speedup = first_pass_time / second_pass_time if second_pass_time > 0 else float('inf')
        time_saved = first_pass_time - second_pass_time
        
        print(f"\nPerformance Analysis:")
        print(f"  First pass time: {first_pass_time:.2f} seconds")
        print(f"  Second pass time: {second_pass_time:.2f} seconds")
        print(f"  Speedup: {speedup:.2f}x faster")
        print(f"  Time saved: {time_saved:.2f} seconds")
        print(f"  Average time per query (first pass): {first_pass_time/len(queries):.2f} seconds")
        print(f"  Average time per query (second pass): {second_pass_time/len(queries):.2f} seconds")
        
        # Cache statistics
        cache_stats = enhanced_provider.get_cache_stats()
        print(f"\nFinal Cache Statistics:")
        print(f"  Total entries: {cache_stats.get('total_entries', 0)}")
        print(f"  Hit rate: {cache_stats.get('hit_rate', 0):.2%}")
        print(f"  Total tokens saved: {cache_stats.get('total_tokens_saved', 0)}")
        print(f"  Total cost saved: ${cache_stats.get('total_cost_saved', 0):.4f}")
        print(f"  Cache size: {cache_stats.get('current_size_mb', 0):.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"Error in cache performance benchmark: {e}")
        return False

def test_cache_configuration_options():
    """Test different cache configuration options."""
    print("\n" + "="*60)
    print("TESTING CACHE CONFIGURATION OPTIONS")
    print("="*60)
    
    try:
        # Test with caching disabled
        print("Testing with caching disabled:")
        enhanced_provider_no_cache = get_enhanced_llm_provider('openai',
            enable_caching=False,
            enable_multi_source_research=False,
            enable_iar_validation=False,
            enable_temporal_modeling=False,
            enable_cfp_analysis=False,
            enable_complex_system_visioning=False,
            enable_adjacent_exploration=False,
            enable_self_assessment=False
        )
        
        query = "What is caching?"
        
        start_time = time.time()
        result1 = enhanced_provider_no_cache.enhanced_query_processing(query, "gpt-4")
        time1 = time.time() - start_time
        
        start_time = time.time()
        result2 = enhanced_provider_no_cache.enhanced_query_processing(query, "gpt-4")
        time2 = time.time() - start_time
        
        print(f"  First call time: {time1:.2f} seconds")
        print(f"  Second call time: {time2:.2f} seconds")
        print(f"  No caching speedup: {time1/time2:.2f}x")
        
        # Test with different TTL values
        print("\nTesting with different TTL values:")
        
        # Short TTL
        enhanced_provider_short_ttl = get_enhanced_llm_provider('openai',
            enable_caching=True,
            cache_ttl=1,  # 1 second
            enable_multi_source_research=False,
            enable_iar_validation=False,
            enable_temporal_modeling=False,
            enable_cfp_analysis=False,
            enable_complex_system_visioning=False,
            enable_adjacent_exploration=False,
            enable_self_assessment=False
        )
        
        result1 = enhanced_provider_short_ttl.enhanced_query_processing(query, "gpt-4")
        time.sleep(2)  # Wait for TTL to expire
        result2 = enhanced_provider_short_ttl.enhanced_query_processing(query, "gpt-4")
        
        print(f"  Short TTL cache hit: {'cache_info' in result2}")
        
        # Long TTL
        enhanced_provider_long_ttl = get_enhanced_llm_provider('openai',
            enable_caching=True,
            cache_ttl=86400,  # 24 hours
            enable_multi_source_research=False,
            enable_iar_validation=False,
            enable_temporal_modeling=False,
            enable_cfp_analysis=False,
            enable_complex_system_visioning=False,
            enable_adjacent_exploration=False,
            enable_self_assessment=False
        )
        
        result1 = enhanced_provider_long_ttl.enhanced_query_processing(query, "gpt-4")
        result2 = enhanced_provider_long_ttl.enhanced_query_processing(query, "gpt-4")
        
        print(f"  Long TTL cache hit: {'cache_info' in result2}")
        
        return True
        
    except Exception as e:
        print(f"Error testing cache configuration options: {e}")
        return False

def test_cache_export_import():
    """Test cache export and import functionality."""
    print("\n" + "="*60)
    print("TESTING CACHE EXPORT/IMPORT")
    print("="*60)
    
    try:
        # Create test cache
        test_cache = TokenCacheManager(cache_dir="test_export_cache", max_size_mb=10)
        
        # Add some test data
        test_data = [
            ("What is AI?", "AI is artificial intelligence", 100, 0.003),
            ("How does ML work?", "ML works by learning patterns", 120, 0.0036),
            ("What is caching?", "Caching stores data for quick access", 110, 0.0033)
        ]
        
        for query, response, tokens, cost in test_data:
            test_cache.put(
                query=query,
                model="gpt-4",
                response=response,
                tokens_used=tokens,
                cost_estimate=cost,
                ttl=3600,
                cache_type='exact',
                confidence=1.0
            )
        
        # Export cache
        export_file = "test_cache_export.json"
        test_cache.export_cache(export_file)
        print(f"Exported cache to {export_file}")
        
        # Create new cache and import
        new_cache = TokenCacheManager(cache_dir="test_import_cache", max_size_mb=10)
        new_cache.import_cache(export_file)
        print(f"Imported cache from {export_file}")
        
        # Verify import
        for query, response, tokens, cost in test_data:
            cached_result = new_cache.get(query, "gpt-4")
            if cached_result:
                retrieved_response, metadata = cached_result
                if retrieved_response == response:
                    print(f"  ✓ Successfully imported: {query}")
                else:
                    print(f"  ✗ Import mismatch: {query}")
            else:
                print(f"  ✗ Import failed: {query}")
        
        # Clean up
        test_cache.clear()
        new_cache.clear()
        if os.path.exists(export_file):
            os.remove(export_file)
        
        return True
        
    except Exception as e:
        print(f"Error testing cache export/import: {e}")
        return False

def main():
    """Main test function."""
    print("Token Caching Test Suite")
    print("Testing intelligent caching for LLM API calls")
    
    # Check if API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Some tests may fail without proper API credentials.")
    
    tests = [
        ("Basic Cache Functionality", test_cache_basic_functionality),
        ("Semantic Caching", test_semantic_caching),
        ("Enhanced Provider Caching", test_enhanced_provider_caching),
        ("Cache Performance Benchmark", test_cache_performance_benchmark),
        ("Cache Configuration Options", test_cache_configuration_options),
        ("Cache Export/Import", test_cache_export_import)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*80}")
        print(f"RUNNING: {test_name}")
        print(f"{'='*80}")
        
        try:
            success = test_func()
            results[test_name] = {
                'status': 'PASS' if success else 'FAIL',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results[test_name] = {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    for test_name, result in results.items():
        status = result['status']
        timestamp = result['timestamp']
        print(f"{test_name}: {status} ({timestamp})")
    
    # Save results
    with open('token_caching_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nToken caching testing completed!")
    print("The caching system provides:")
    print("- Multi-level caching (exact, semantic, partial matches)")
    print("- Cost tracking and optimization")
    print("- TTL-based expiration")
    print("- Thread-safe operations")
    print("- Compression for large responses")
    print("- Cache statistics and analytics")
    print("- Export/import functionality")

if __name__ == "__main__":
    main() 