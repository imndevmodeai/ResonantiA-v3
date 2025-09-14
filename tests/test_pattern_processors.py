"""
Tests for pattern processors implementation
"""
import unittest
import asyncio
from typing import Dict, Any
from Three_PointO_ArchE.pattern_processors import (
    PatternProcessor,
    EnhancementPatternProcessor,
    MetacognitivePatternProcessor,
    InsightPatternProcessor,
    CFPPatternProcessor,
    CausalABMPatternProcessor,
    TeslaPatternProcessor,
    KNOPatternProcessor,
    PatternProcessorFactory,
    PatternProcessingResult
)

class TestPatternProcessors(unittest.TestCase):
    """Test suite for pattern processors."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data = {
            "data": {
                "key": "value",
                "nested": {
                    "field": "test"
                }
            },
            "confidence": 0.9
        }
        self.test_context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "timestamp": "2024-03-20T12:00:00Z"
        }
    
    def test_enhancement_processor(self):
        """Test enhancement pattern processor."""
        async def run_test():
            processor = EnhancementPatternProcessor()
            
            # Test valid data
            result = await processor.process(self.test_data, self.test_context)
            
            self.assertIsInstance(result, PatternProcessingResult)
            self.assertEqual(result.pattern_type, "enhancement")
            self.assertIsInstance(result.processed_data, dict)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.issues, list)
            self.assertIsInstance(result.resonance_score, float)
            
            # Test invalid data
            invalid_result = await processor.process({}, self.test_context)
            
            self.assertEqual(invalid_result.confidence, 0.0)
            self.assertTrue(len(invalid_result.issues) > 0)
        
        asyncio.run(run_test())
    
    def test_metacognitive_processor(self):
        """Test metacognitive pattern processor."""
        async def run_test():
            processor = MetacognitivePatternProcessor()
            
            # Test valid data
            result = await processor.process(self.test_data, self.test_context)
            
            self.assertIsInstance(result, PatternProcessingResult)
            self.assertEqual(result.pattern_type, "metacognitive")
            self.assertIsInstance(result.processed_data, dict)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.issues, list)
            self.assertIsInstance(result.resonance_score, float)
            
            # Test invalid data
            invalid_result = await processor.process({}, self.test_context)
            
            self.assertEqual(invalid_result.confidence, 0.0)
            self.assertTrue(len(invalid_result.issues) > 0)
        
        asyncio.run(run_test())
    
    def test_insight_processor(self):
        """Test insight pattern processor."""
        async def run_test():
            processor = InsightPatternProcessor()
            
            # Test valid data
            result = await processor.process(self.test_data, self.test_context)
            
            self.assertIsInstance(result, PatternProcessingResult)
            self.assertEqual(result.pattern_type, "insight")
            self.assertIsInstance(result.processed_data, dict)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.issues, list)
            self.assertIsInstance(result.resonance_score, float)
            
            # Test invalid data
            invalid_result = await processor.process({}, self.test_context)
            
            self.assertEqual(invalid_result.confidence, 0.0)
            self.assertTrue(len(invalid_result.issues) > 0)
        
        asyncio.run(run_test())
    
    def test_cfp_processor(self):
        """Test CFP pattern processor."""
        async def run_test():
            processor = CFPPatternProcessor()
            
            # Test valid data
            result = await processor.process(self.test_data, self.test_context)
            
            self.assertIsInstance(result, PatternProcessingResult)
            self.assertEqual(result.pattern_type, "cfp")
            self.assertIsInstance(result.processed_data, dict)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.issues, list)
            self.assertIsInstance(result.resonance_score, float)
            
            # Test invalid data
            invalid_result = await processor.process({}, self.test_context)
            
            self.assertEqual(invalid_result.confidence, 0.0)
            self.assertTrue(len(invalid_result.issues) > 0)
        
        asyncio.run(run_test())
    
    def test_causal_abm_processor(self):
        """Test Causal-ABM pattern processor."""
        async def run_test():
            processor = CausalABMPatternProcessor()
            
            # Test valid data
            result = await processor.process(self.test_data, self.test_context)
            
            self.assertIsInstance(result, PatternProcessingResult)
            self.assertEqual(result.pattern_type, "causal_abm")
            self.assertIsInstance(result.processed_data, dict)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.issues, list)
            self.assertIsInstance(result.resonance_score, float)
            
            # Test invalid data
            invalid_result = await processor.process({}, self.test_context)
            
            self.assertEqual(invalid_result.confidence, 0.0)
            self.assertTrue(len(invalid_result.issues) > 0)
        
        asyncio.run(run_test())
    
    def test_tesla_processor(self):
        """Test Tesla pattern processor."""
        async def run_test():
            processor = TeslaPatternProcessor()
            
            # Test valid data
            result = await processor.process(self.test_data, self.test_context)
            
            self.assertIsInstance(result, PatternProcessingResult)
            self.assertEqual(result.pattern_type, "tesla")
            self.assertIsInstance(result.processed_data, dict)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.issues, list)
            self.assertIsInstance(result.resonance_score, float)
            
            # Test invalid data
            invalid_result = await processor.process({}, self.test_context)
            
            self.assertEqual(invalid_result.confidence, 0.0)
            self.assertTrue(len(invalid_result.issues) > 0)
        
        asyncio.run(run_test())
    
    def test_kno_processor(self):
        """Test KnO pattern processor."""
        async def run_test():
            processor = KNOPatternProcessor()
            
            # Test valid data
            result = await processor.process(self.test_data, self.test_context)
            
            self.assertIsInstance(result, PatternProcessingResult)
            self.assertEqual(result.pattern_type, "kno")
            self.assertIsInstance(result.processed_data, dict)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.issues, list)
            self.assertIsInstance(result.resonance_score, float)
            
            # Test invalid data
            invalid_result = await processor.process({}, self.test_context)
            
            self.assertEqual(invalid_result.confidence, 0.0)
            self.assertTrue(len(invalid_result.issues) > 0)
        
        asyncio.run(run_test())
    
    def test_factory(self):
        """Test pattern processor factory."""
        # Test valid pattern types
        valid_types = [
            "enhancement",
            "metacognitive",
            "insight",
            "cfp",
            "causal_abm",
            "tesla",
            "kno"
        ]
        
        for pattern_type in valid_types:
            processor = PatternProcessorFactory.create_processor(pattern_type)
            self.assertIsInstance(processor, PatternProcessor)
        
        # Test invalid pattern type
        with self.assertRaises(ValueError):
            PatternProcessorFactory.create_processor("invalid_type")
    
    def test_iar_validation(self):
        """Test IAR validation in pattern processors."""
        async def run_test():
            processor = EnhancementPatternProcessor()
            
            # Test valid IAR data
            valid_iar = {
                "status": "Success",
                "confidence": 0.9,
                "summary": "Test summary",
                "potential_issues": [],
                "alignment_check": {
                    "quality": 0.9
                }
            }
            
            self.assertTrue(processor.validate_iar(valid_iar, self.test_context))
            
            # Test invalid IAR data
            invalid_iar = {
                "status": "Invalid",
                "confidence": 1.5,  # Invalid confidence
                "summary": "Test summary",
                "potential_issues": [],
                "alignment_check": {
                    "quality": 0.9
                }
            }
            
            self.assertFalse(processor.validate_iar(invalid_iar, self.test_context))
        
        asyncio.run(run_test())
    
    def test_resonance_tracking(self):
        """Test resonance tracking in pattern processors."""
        async def run_test():
            processor = EnhancementPatternProcessor()
            
            # Test resonance tracking
            iar_data = {
                "status": "Success",
                "confidence": 0.9,
                "summary": "Test summary",
                "potential_issues": [],
                "alignment_check": {
                    "quality": 0.9
                }
            }
            
            processor.track_resonance("enhancement", iar_data, self.test_context)
            
            # Get execution summary
            summary = processor.resonance_tracker.get_execution_summary()
            
            self.assertIsInstance(summary, dict)
            self.assertIn("total_executions", summary)
            self.assertIn("average_resonance", summary)
            self.assertIn("issues_detected", summary)
        
        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main() 