import unittest
import json
import tempfile
from pathlib import Path
from Three_PointO_ArchE.pattern_reflection_system import PatternReflectionSystem, Pattern

class TestPatternReflectionSystem(unittest.TestCase):
    def setUp(self):
        # Create a temporary knowledge tapestry file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.knowledge_tapestry_path = Path(self.temp_dir.name) / "knowledge_tapestry.json"
        
        # Sample knowledge tapestry data
        self.sample_tapestry = {
            "cosmic": [
                {
                    "content": {
                        "universal_principles": ["unity", "harmony", "balance"],
                        "cosmic_patterns": ["fractal", "recursion", "symmetry"],
                        "fundamental_laws": ["conservation", "entropy", "causality"]
                    },
                    "metadata": {"source": "cosmic_observation"},
                    "reflection_strength": 0.95
                }
            ],
            "systemic": [
                {
                    "content": {
                        "system_principles": ["emergence", "self-organization", "adaptation"],
                        "system_patterns": ["feedback", "resonance", "synchronization"],
                        "system_laws": ["homeostasis", "evolution", "complexity"]
                    },
                    "metadata": {"source": "system_analysis"},
                    "reflection_strength": 0.85
                }
            ],
            "local": [
                {
                    "content": {
                        "local_principles": ["cooperation", "competition", "symbiosis"],
                        "local_patterns": ["networks", "flows", "boundaries"],
                        "local_laws": ["stability", "change", "interaction"]
                    },
                    "metadata": {"source": "local_observation"},
                    "reflection_strength": 0.75
                }
            ],
            "micro": [
                {
                    "content": {
                        "micro_principles": ["atomic", "molecular", "cellular"],
                        "micro_patterns": ["structure", "function", "process"],
                        "micro_laws": ["binding", "catalysis", "regulation"]
                    },
                    "metadata": {"source": "micro_analysis"},
                    "reflection_strength": 0.65
                }
            ]
        }
        
        with open(self.knowledge_tapestry_path, 'w') as f:
            json.dump(self.sample_tapestry, f)
        
        self.system = PatternReflectionSystem(str(self.knowledge_tapestry_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialize_hierarchy(self):
        result = self.system.initialize_hierarchy(bidirectional=True)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["bidirectional"])
        self.assertEqual(result["levels"], ["cosmic", "systemic", "local", "micro"])

    def test_extract_patterns(self):
        # Test cosmic level
        result = self.system.extract_patterns("cosmic", "knowledge_tapestry.json")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["patterns"]), 1)
        self.assertEqual(result["level"], "cosmic")
        
        # Test micro level
        result = self.system.extract_patterns("micro", "knowledge_tapestry.json")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["patterns"]), 1)
        self.assertEqual(result["level"], "micro")

    def test_reflect_patterns(self):
        # First extract patterns
        cosmic_result = self.system.extract_patterns("cosmic", "knowledge_tapestry.json")
        
        # Test downward reflection
        result = self.system.reflect_patterns(
            "downward",
            cosmic_result["patterns"],
            ["systemic", "local", "micro"]
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["reflected_patterns"]) > 0)
        
        # Test upward reflection
        micro_result = self.system.extract_patterns("micro", "knowledge_tapestry.json")
        result = self.system.reflect_patterns(
            "upward",
            micro_result["patterns"],
            ["local", "systemic", "cosmic"]
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["reflected_patterns"]) > 0)

    def test_synthesize_patterns(self):
        # Extract and reflect patterns in both directions
        cosmic_result = self.system.extract_patterns("cosmic", "knowledge_tapestry.json")
        downward_result = self.system.reflect_patterns(
            "downward",
            cosmic_result["patterns"],
            ["systemic", "local", "micro"]
        )
        
        micro_result = self.system.extract_patterns("micro", "knowledge_tapestry.json")
        upward_result = self.system.reflect_patterns(
            "upward",
            micro_result["patterns"],
            ["local", "systemic", "cosmic"]
        )
        
        # Test synthesis
        result = self.system.synthesize_patterns(
            upward_result["reflected_patterns"],
            downward_result["reflected_patterns"]
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue("synthesized_patterns" in result)

    def test_validate_coherence(self):
        # First synthesize patterns
        cosmic_result = self.system.extract_patterns("cosmic", "knowledge_tapestry.json")
        downward_result = self.system.reflect_patterns(
            "downward",
            cosmic_result["patterns"],
            ["systemic", "local", "micro"]
        )
        
        micro_result = self.system.extract_patterns("micro", "knowledge_tapestry.json")
        upward_result = self.system.reflect_patterns(
            "upward",
            micro_result["patterns"],
            ["local", "systemic", "cosmic"]
        )
        
        synthesis_result = self.system.synthesize_patterns(
            upward_result["reflected_patterns"],
            downward_result["reflected_patterns"]
        )
        
        # Test validation
        result = self.system.validate_coherence(
            synthesis_result["synthesized_patterns"],
            threshold=0.7
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue("coherence_scores" in result)

    def test_integrate_patterns(self):
        # First validate patterns
        cosmic_result = self.system.extract_patterns("cosmic", "knowledge_tapestry.json")
        downward_result = self.system.reflect_patterns(
            "downward",
            cosmic_result["patterns"],
            ["systemic", "local", "micro"]
        )
        
        micro_result = self.system.extract_patterns("micro", "knowledge_tapestry.json")
        upward_result = self.system.reflect_patterns(
            "upward",
            micro_result["patterns"],
            ["local", "systemic", "cosmic"]
        )
        
        synthesis_result = self.system.synthesize_patterns(
            upward_result["reflected_patterns"],
            downward_result["reflected_patterns"]
        )
        
        validation_result = self.system.validate_coherence(
            synthesis_result["synthesized_patterns"],
            threshold=0.7
        )
        
        # Test integration
        result = self.system.integrate_patterns(
            synthesis_result["synthesized_patterns"],
            "Three_PointO_ArchE"
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue("integration_results" in result)

    def test_generate_report(self):
        # First integrate patterns
        cosmic_result = self.system.extract_patterns("cosmic", "knowledge_tapestry.json")
        downward_result = self.system.reflect_patterns(
            "downward",
            cosmic_result["patterns"],
            ["systemic", "local", "micro"]
        )
        
        micro_result = self.system.extract_patterns("micro", "knowledge_tapestry.json")
        upward_result = self.system.reflect_patterns(
            "upward",
            micro_result["patterns"],
            ["local", "systemic", "cosmic"]
        )
        
        synthesis_result = self.system.synthesize_patterns(
            upward_result["reflected_patterns"],
            downward_result["reflected_patterns"]
        )
        
        validation_result = self.system.validate_coherence(
            synthesis_result["synthesized_patterns"],
            threshold=0.7
        )
        
        integration_result = self.system.integrate_patterns(
            synthesis_result["synthesized_patterns"],
            "Three_PointO_ArchE"
        )
        
        # Test report generation
        result = self.system.generate_report(integration_result, format="markdown")
        self.assertEqual(result["status"], "success")
        self.assertTrue("report" in result)
        self.assertTrue("# Pattern Reflection System Report" in result["report"])

if __name__ == '__main__':
    unittest.main() 