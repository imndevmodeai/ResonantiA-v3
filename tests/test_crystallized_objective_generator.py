import os
import sys
import unittest
import time

# Ensure module import path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from crystallized_objective_generator import (
    CrystallizedObjectiveGenerator,
)


class TestCrystallizedObjectiveGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = CrystallizedObjectiveGenerator(
            spr_bank_loader=CrystallizedObjectiveGenerator.example_spr_bank,
            rng_seed=42
        )

    def _make_m9_mandate(self):
        return {
            "text": "Analyze systemic risks and emergent behaviors in deployment; propose high-level vision and simulations.",
            "issuer": "researcher@example.com",
            "priority": 7,
            "tags": ["system", "emergence", "simulation"],
            "context": {"mandate_type": "M9", "mandate_symbol": "M9"},
            "constraints": {"budget": 10.0},
            "seed": 12345
        }

    def test_generates_objective_with_temporal_analysis(self):
        mandate = self._make_m9_mandate()
        result = self.generator.generate(mandate, mode="deterministic")
        self.assertIsNotNone(result.temporal_scope, "TemporalScope should be populated")
        analysis = result.temporal_scope.analysis_results or {}
        # Ensure H, T, F, C, E, Tr all present
        for key in ("H", "T", "F", "C", "E", "Tr"):
            self.assertIn(key, analysis, f"Temporal analysis must include '{key}'")

    def test_budget_constraint_triggers_warning(self):
        mandate = self._make_m9_mandate()
        result = self.generator.generate(mandate, mode="deterministic")
        # Acceptance is clamped to [0,1]
        self.assertGreaterEqual(result.acceptance_score, 0.0)
        self.assertLessEqual(result.acceptance_score, 1.0)
        # Expect finalized_warning due to budget_exceeded
        self.assertTrue(result.metadata.get("finalized_warning", False))
        self.assertTrue(
            any("budget_exceeded" in msg for msg in (result.explanations or [])),
            "Expected budget_exceeded message in explanations"
        )

    def test_m9_prefers_systemic_simulation_step_presence(self):
        """
        M9 customization boosts systemic/complex_system SPRs (e.g., SimulateCounterfactuals).
        We don't assert absolute ordering, but presence among steps produced.
        """
        mandate = self._make_m9_mandate()
        result = self.generator.generate(mandate, mode="deterministic")
        titles = [s.title for s in (result.steps or [])]
        self.assertIn(
            "SimulateCounterfactuals", titles,
            "Expected 'SimulateCounterfactuals' step to be included under M9 mandate"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)


