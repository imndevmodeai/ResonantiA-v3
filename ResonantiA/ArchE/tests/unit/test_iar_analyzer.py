import unittest
from unittest.mock import MagicMock
from ResonantiA.ArchE.iar_analyzer import IARAnalyzer
import numpy as np

class TestIARAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = IARAnalyzer()

    def test_calculate_basic_iar_metrics_empty_stream(self):
        """Test with an empty IAR stream."""
        iar_stream = []
        metrics = self.analyzer.calculate_basic_iar_metrics(iar_stream)
        self.assertIsNone(metrics["average_confidence"])
        self.assertIsNone(metrics["failure_rate"])
        self.assertEqual(metrics["critical_issue_count"], 0)
        self.assertEqual(metrics["unique_issue_types"], set())
        self.assertEqual(metrics["total_records"], 0)

    def test_calculate_basic_iar_metrics_all_success_no_issues(self):
        """Test with all successful IARs and no potential issues."""
        iar_stream = [
            {"status": "Success", "confidence": 0.9, "potential_issues": []},
            {"status": "Success", "confidence": 0.95, "potential_issues": []},
            {"status": "Success", "confidence": 0.85, "potential_issues": []}
        ]
        metrics = self.analyzer.calculate_basic_iar_metrics(iar_stream)
        self.assertAlmostEqual(metrics["average_confidence"], 0.9)
        self.assertEqual(metrics["failure_rate"], 0.0)
        self.assertEqual(metrics["critical_issue_count"], 0)
        self.assertEqual(metrics["unique_issue_types"], set())
        self.assertEqual(metrics["total_records"], 3)

    def test_calculate_basic_iar_metrics_with_failures_and_issues(self):
        """Test with a mix of statuses, confidences, and issues."""
        iar_stream = [
            {"status": "Success", "confidence": 0.9, "potential_issues": ["minor_glitch", "user_error"]},
            {"status": "Failure", "confidence": 0.3, "potential_issues": ["critical_system_fault", "data_corruption"]},
            {"status": "Success", "confidence": 0.7, "potential_issues": []},
            {"status": "Success", "confidence": 0.8, "potential_issues": ["minor_glitch"]}
        ]
        metrics = self.analyzer.calculate_basic_iar_metrics(iar_stream)
        self.assertAlmostEqual(metrics["average_confidence"], (0.9 + 0.3 + 0.7 + 0.8) / 4)
        self.assertEqual(metrics["failure_rate"], 0.25)
        self.assertEqual(metrics["critical_issue_count"], 1) # "critical_system_fault"
        expected_issues = {"minor_glitch", "user_error", "critical_system_fault", "data_corruption"}
        self.assertEqual(metrics["unique_issue_types"], expected_issues)
        self.assertEqual(metrics["total_records"], 4)

    def test_calculate_basic_iar_metrics_missing_optional_fields(self):
        """Test IAR records with missing optional fields like confidence or potential_issues."""
        iar_stream = [
            {"status": "Success"}, # Missing confidence and potential_issues
            {"status": "Failure", "confidence": 0.2}, # Missing potential_issues
            {"status": "Success", "potential_issues": ["log_warning"]}, # Missing confidence
            {"status": "Success", "confidence": 0.9, "potential_issues": []}
        ]
        metrics = self.analyzer.calculate_basic_iar_metrics(iar_stream)
        # Only 0.2 and 0.9 are valid confidences
        self.assertAlmostEqual(metrics["average_confidence"], (0.2 + 0.9) / 2)
        self.assertEqual(metrics["failure_rate"], 0.25)
        self.assertEqual(metrics["critical_issue_count"], 0)
        self.assertEqual(metrics["unique_issue_types"], {"log_warning"})
        self.assertEqual(metrics["total_records"], 4)

    def test_calculate_basic_iar_metrics_various_confidence_types(self):
        """Test with integer and float confidences, and non-numeric ones to be ignored."""
        iar_stream = [
            {"status": "Success", "confidence": 1, "potential_issues": []}, # Integer
            {"status": "Success", "confidence": 0.8, "potential_issues": []}, # Float
            {"status": "Success", "confidence": "high", "potential_issues": []}, # String, should be ignored
            {"status": "Success", "confidence": None, "potential_issues": []} # None, should be ignored
        ]
        metrics = self.analyzer.calculate_basic_iar_metrics(iar_stream)
        self.assertAlmostEqual(metrics["average_confidence"], (1.0 + 0.8) / 2)
        self.assertEqual(metrics["failure_rate"], 0.0)
        self.assertEqual(metrics["total_records"], 4)

    def test_update_metric_baseline_initial_and_updates(self):
        """Test baseline creation and updates with numeric data."""
        context_key = "TestContext_Confidence"
        metric_name = "average_confidence"

        # Initial value
        self.analyzer.update_metric_baseline(context_key, metric_name, 0.9)
        baseline = self.analyzer.baselines[context_key][metric_name]
        self.assertAlmostEqual(baseline["mean"], 0.9)
        self.assertAlmostEqual(baseline["std_dev"], 0.0)
        self.assertEqual(baseline["count"], 1)

        # Add more values
        self.analyzer.update_metric_baseline(context_key, metric_name, 0.8)
        self.analyzer.update_metric_baseline(context_key, metric_name, 0.7)
        
        baseline = self.analyzer.baselines[context_key][metric_name]
        expected_mean = np.mean([0.9, 0.8, 0.7])
        expected_std = np.std([0.9, 0.8, 0.7])
        self.assertAlmostEqual(baseline["mean"], expected_mean)
        self.assertAlmostEqual(baseline["std_dev"], expected_std)
        self.assertEqual(baseline["count"], 3)

    def test_update_metric_baseline_window_rollover(self):
        """Test that the baseline window correctly rolls over."""
        context_key = "TestContext_Window"
        metric_name = "test_metric"
        window_size = 3 # Smaller window for testing rollover

        self.analyzer.update_metric_baseline(context_key, metric_name, 10, window_size=window_size)
        self.analyzer.update_metric_baseline(context_key, metric_name, 12, window_size=window_size)
        self.analyzer.update_metric_baseline(context_key, metric_name, 14, window_size=window_size)
        baseline = self.analyzer.baselines[context_key][metric_name]
        self.assertListEqual(baseline["values"], [10, 12, 14])

        # This value should push '10' out of the window
        self.analyzer.update_metric_baseline(context_key, metric_name, 16, window_size=window_size)
        baseline = self.analyzer.baselines[context_key][metric_name]
        self.assertListEqual(baseline["values"], [12, 14, 16])
        expected_mean = np.mean([12, 14, 16])
        expected_std = np.std([12, 14, 16])
        self.assertAlmostEqual(baseline["mean"], expected_mean)
        self.assertAlmostEqual(baseline["std_dev"], expected_std)

    def test_detect_confidence_drop_no_baseline(self):
        """Test detection when no baseline exists for the context."""
        self.assertIsNone(self.analyzer.detect_confidence_drop("NewContext_NoBaseline", 0.5))

    def test_detect_confidence_drop_significant_drop(self):
        """Test detection when confidence drops significantly below baseline."""
        context_key = "TestContext_SigDrop"
        metric_name = "average_confidence"
        # Establish a stable baseline
        for _ in range(20):
            self.analyzer.update_metric_baseline(context_key, metric_name, 0.9)
        
        anomaly = self.analyzer.detect_confidence_drop(context_key, 0.5) # Significant drop
        self.assertIsNotNone(anomaly)
        self.assertEqual(anomaly["anomaly_type"], "SignificantConfidenceDrop")
        self.assertEqual(anomaly["context_key"], context_key)
        self.assertEqual(anomaly["current_value"], 0.5)
        self.assertAlmostEqual(anomaly["baseline_mean"], 0.9)

    def test_detect_confidence_drop_no_significant_drop(self):
        """Test non-detection when confidence is within normal bounds of the baseline."""
        context_key = "TestContext_NoDrop"
        metric_name = "average_confidence"
        # Establish a baseline with some variance
        self.analyzer.update_metric_baseline(context_key, metric_name, 0.9)
        self.analyzer.update_metric_baseline(context_key, metric_name, 0.8)
        self.analyzer.update_metric_baseline(context_key, metric_name, 1.0)
        self.analyzer.update_metric_baseline(context_key, metric_name, 0.85)
        self.analyzer.update_metric_baseline(context_key, metric_name, 0.95)
        
        # A small, acceptable dip
        self.assertIsNone(self.analyzer.detect_confidence_drop(context_key, 0.75)) 

    def test_detect_confidence_drop_stable_metric_small_std_dev(self):
        """Test detection with a very stable metric (low std_dev) to ensure effective_std_dev works."""
        context_key = "TestContext_Stable"
        metric_name = "average_confidence"
        # Establish a very stable baseline
        for _ in range(20):
            self.analyzer.update_metric_baseline(context_key, metric_name, 0.99)
        
        # Baseline mean should be 0.99, std_dev near 0.0
        # effective_std_dev will be 0.01
        # threshold_multiplier is 2.5 by default
        # lower_bound = 0.99 - (2.5 * 0.01) = 0.99 - 0.025 = 0.965
        
        anomaly = self.analyzer.detect_confidence_drop(context_key, 0.96) # Just below threshold
        self.assertIsNotNone(anomaly)
        self.assertEqual(anomaly["current_value"], 0.96)
        self.assertAlmostEqual(anomaly["baseline_mean"], 0.99)
        self.assertAlmostEqual(anomaly["threshold_bound"], 0.99 - (2.5 * 0.01))

        self.assertIsNone(self.analyzer.detect_confidence_drop(context_key, 0.97)) # Just above threshold

    # Add more test methods here for other scenarios and functions

    def test_update_issue_type_baselines_initial_creation(self):
        """Test initial creation of issue_baseline for a new context."""
        context_key = "TestContext_IssueBaseline_New"
        current_issues = {"issue1", "issue2"}
        self.analyzer.update_issue_type_baselines(context_key, current_issues)

        self.assertIn(context_key, self.analyzer.baselines)
        self.assertIn("issue_baseline", self.analyzer.baselines[context_key])
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["known_issue_types"], set())
        self.assertEqual(issue_baseline["new_issue_candidates"], {"issue1": 1, "issue2": 1})

    def test_update_issue_type_baselines_increment_streak(self):
        """Test incrementing streak for existing new issue candidates."""
        context_key = "TestContext_IssueBaseline_Streak"
        self.analyzer.update_issue_type_baselines(context_key, {"issueA", "issueB"}) # Streak 1
        self.analyzer.update_issue_type_baselines(context_key, {"issueA", "issueC"}) # issueA streak 2, issueB disappears, issueC new

        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {"issueA": 2, "issueC": 1})
        self.assertEqual(issue_baseline["known_issue_types"], {"issueB"}) # issueB had streak broken

    def test_update_issue_type_baselines_candidate_disappears_becomes_known(self):
        """Test that a candidate issue moves to known when its streak is broken."""
        context_key = "TestContext_IssueBaseline_Disappear"
        self.analyzer.update_issue_type_baselines(context_key, {"issueX", "issueY"}) # issueX:1, issueY:1
        self.analyzer.update_issue_type_baselines(context_key, {"issueX"})       # issueX:2, issueY streak broken
        
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {"issueX": 2})
        self.assertEqual(issue_baseline["known_issue_types"], {"issueY"})

        # Call again with no sign of issueX, it should also become known
        self.analyzer.update_issue_type_baselines(context_key, {"issueZ"}) # issueX streak broken, issueZ:1
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {"issueZ": 1})
        self.assertEqual(issue_baseline["known_issue_types"], {"issueY", "issueX"})

    def test_update_issue_type_baselines_known_issue_reappears(self):
        """Test that a known issue reappearing does not become a candidate."""
        context_key = "TestContext_IssueBaseline_KnownReappears"
        self.analyzer.update_issue_type_baselines(context_key, {"known1"}) # known1:1
        self.analyzer.update_issue_type_baselines(context_key, set())      # known1 becomes known
        
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {})
        self.assertEqual(issue_baseline["known_issue_types"], {"known1"})

        self.analyzer.update_issue_type_baselines(context_key, {"known1", "new1"}) # known1 should not re-candidate, new1:1
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {"new1": 1})
        self.assertEqual(issue_baseline["known_issue_types"], {"known1"})

    def test_update_issue_type_baselines_empty_current_issues(self):
        """Test updating with an empty set of current issues."""
        context_key = "TestContext_IssueBaseline_EmptyCurrent"
        self.analyzer.update_issue_type_baselines(context_key, {"issueP", "issueQ"}) # P:1, Q:1
        
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {"issueP": 1, "issueQ": 1})
        self.assertEqual(issue_baseline["known_issue_types"], set())

        self.analyzer.update_issue_type_baselines(context_key, set()) # P, Q streaks broken
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {})
        self.assertEqual(issue_baseline["known_issue_types"], {"issueP", "issueQ"})

    def test_update_issue_type_baselines_multiple_contexts(self):
        """Test that baselines for different contexts are kept separate."""
        context1 = "Ctx1_Issues"
        context2 = "Ctx2_Issues"

        self.analyzer.update_issue_type_baselines(context1, {"c1_issue1"})
        self.analyzer.update_issue_type_baselines(context2, {"c2_issueA", "c2_issueB"})
        self.analyzer.update_issue_type_baselines(context1, {"c1_issue1", "c1_issue2"}) # c1_issue1:2, c1_issue2:1

        ctx1_baseline = self.analyzer.baselines[context1]["issue_baseline"]
        self.assertEqual(ctx1_baseline["new_issue_candidates"], {"c1_issue1": 2, "c1_issue2": 1})
        self.assertEqual(ctx1_baseline["known_issue_types"], set())

        ctx2_baseline = self.analyzer.baselines[context2]["issue_baseline"]
        self.assertEqual(ctx2_baseline["new_issue_candidates"], {"c2_issueA": 1, "c2_issueB": 1})
        self.assertEqual(ctx2_baseline["known_issue_types"], set())

        # Break streak for c2_issueA
        self.analyzer.update_issue_type_baselines(context2, {"c2_issueB"}) # c2_issueB:2, c2_issueA becomes known
        ctx2_baseline = self.analyzer.baselines[context2]["issue_baseline"]
        self.assertEqual(ctx2_baseline["new_issue_candidates"], {"c2_issueB": 2})
        self.assertEqual(ctx2_baseline["known_issue_types"], {"c2_issueA"})
        
        # Ctx1 should be unchanged
        ctx1_baseline_after = self.analyzer.baselines[context1]["issue_baseline"]
        self.assertEqual(ctx1_baseline_after["new_issue_candidates"], {"c1_issue1": 2, "c1_issue2": 1})
        self.assertEqual(ctx1_baseline_after["known_issue_types"], set())

    def test_detect_new_frequent_issue_types_no_baseline(self):
        """Test detection when no issue baseline exists for the context."""
        context_key = "TestContext_NewFrequent_NoBaseline"
        anomalies = self.analyzer.detect_new_frequent_issue_types(context_key, {"some_issue"})
        self.assertEqual(anomalies, [])

    def test_detect_new_frequent_issue_types_candidates_below_threshold(self):
        """Test detection when candidate issue streaks are below the frequency threshold."""
        context_key = "TestContext_NewFrequent_BelowThreshold"
        # Simulate baseline update: issueX and issueY appear twice (threshold is 3 by default)
        self.analyzer.update_issue_type_baselines(context_key, {"issueX", "issueY"})
        self.analyzer.update_issue_type_baselines(context_key, {"issueX", "issueY"})
        
        # Current issues are the same, so streaks are now 2 for issueX, issueY
        anomalies = self.analyzer.detect_new_frequent_issue_types(context_key, {"issueX", "issueY"})
        self.assertEqual(anomalies, [])
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline["new_issue_candidates"], {"issueX": 2, "issueY": 2})
        self.assertEqual(issue_baseline["known_issue_types"], set())

    def test_detect_new_frequent_issue_types_candidate_meets_threshold(self):
        """Test detection when a candidate issue's streak meets the frequency threshold."""
        context_key = "TestContext_NewFrequent_MeetsThreshold"
        # Default threshold is 3
        self.analyzer.update_issue_type_baselines(context_key, {"issueM"}) # Streak 1
        self.analyzer.update_issue_type_baselines(context_key, {"issueM"}) # Streak 2
        self.analyzer.update_issue_type_baselines(context_key, {"issueM"}) # Streak 3 - should be detected NOW by detect_new_frequent_issue_types

        anomalies = self.analyzer.detect_new_frequent_issue_types(context_key, {"issueM"})
        self.assertEqual(len(anomalies), 1)
        anomaly = anomalies[0]
        self.assertEqual(anomaly["anomaly_type"], "NewFrequentIssue")
        self.assertEqual(anomaly["issue_type"], "issueM")
        self.assertEqual(anomaly["appearance_streak"], 3)

        # Verify issueM moved to known_issues and removed from candidates
        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertNotIn("issueM", issue_baseline["new_issue_candidates"])
        self.assertIn("issueM", issue_baseline["known_issue_types"])

    def test_detect_new_frequent_issue_types_candidate_exceeds_threshold(self):
        """Test detection when a candidate issue's streak exceeds the threshold."""
        context_key = "TestContext_NewFrequent_ExceedsThreshold"
        # Default threshold is 3
        self.analyzer.update_issue_type_baselines(context_key, {"issueE"}) # Streak 1
        self.analyzer.update_issue_type_baselines(context_key, {"issueE"}) # Streak 2
        self.analyzer.update_issue_type_baselines(context_key, {"issueE"}) # Streak 3
        self.analyzer.update_issue_type_baselines(context_key, {"issueE"}) # Streak 4

        # At the point of detection, streak will be 4
        anomalies = self.analyzer.detect_new_frequent_issue_types(context_key, {"issueE"})
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["issue_type"], "issueE")
        self.assertEqual(anomalies[0]["appearance_streak"], 4)

        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertNotIn("issueE", issue_baseline["new_issue_candidates"])
        self.assertIn("issueE", issue_baseline["known_issue_types"])

    def test_detect_new_frequent_issue_types_multiple_candidates_mixed(self):
        """Test with multiple candidates, some meeting threshold, some not."""
        context_key = "TestContext_NewFrequent_Mixed"
        # issueHit will hit threshold (3), issueMiss will not (2)
        self.analyzer.update_issue_type_baselines(context_key, {"issueHit", "issueMiss"}) # Hit:1, Miss:1
        self.analyzer.update_issue_type_baselines(context_key, {"issueHit", "issueMiss"}) # Hit:2, Miss:2
        self.analyzer.update_issue_type_baselines(context_key, {"issueHit"})          # Hit:3, Miss streak broken (becomes known)
        
        # Before detection, issueMiss moved to known. Candidates: {"issueHit": 3}
        # Current issues for detection: {"issueHit"}
        anomalies = self.analyzer.detect_new_frequent_issue_types(context_key, {"issueHit"})
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["issue_type"], "issueHit")
        self.assertEqual(anomalies[0]["appearance_streak"], 3)

        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertNotIn("issueHit", issue_baseline["new_issue_candidates"])
        self.assertIn("issueHit", issue_baseline["known_issue_types"])
        self.assertIn("issueMiss", issue_baseline["known_issue_types"]) # From broken streak

    def test_detect_new_frequent_issue_types_already_known_not_flagged(self):
        """Test that an issue already in known_issue_types is not flagged, even if present in current."""
        context_key = "TestContext_NewFrequent_AlreadyKnown"
        # Make 'known_issue' known
        self.analyzer.update_issue_type_baselines(context_key, {"known_issue"}) # Candidate:1
        self.analyzer.update_issue_type_baselines(context_key, set())          # Becomes known

        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertIn("known_issue", issue_baseline["known_issue_types"])
        self.assertEqual(issue_baseline["new_issue_candidates"], {})

        # Now, if known_issue appears again, it should not be flagged by detect_new_frequent_issue_types
        # update_issue_type_baselines will correctly ignore it as it's known
        self.analyzer.update_issue_type_baselines(context_key, {"known_issue"})
        anomalies = self.analyzer.detect_new_frequent_issue_types(context_key, {"known_issue"})
        self.assertEqual(anomalies, [])
        self.assertIn("known_issue", issue_baseline["known_issue_types"]) # Still known
        self.assertEqual(issue_baseline["new_issue_candidates"], {}) # No new candidates

    def test_detect_new_frequent_issue_types_not_reflagged_after_detection(self):
        """Test that an issue is not re-flagged if detect is called again with same state after it was moved to known."""
        context_key = "TestContext_NewFrequent_NoReflag"
        # Setup to flag "issueFlag"
        self.analyzer.update_issue_type_baselines(context_key, {"issueFlag"}) # Streak 1
        self.analyzer.update_issue_type_baselines(context_key, {"issueFlag"}) # Streak 2
        self.analyzer.update_issue_type_baselines(context_key, {"issueFlag"}) # Streak 3

        # First detection - should flag
        anomalies1 = self.analyzer.detect_new_frequent_issue_types(context_key, {"issueFlag"})
        self.assertEqual(len(anomalies1), 1)
        self.assertEqual(anomalies1[0]["issue_type"], "issueFlag")

        # Issue is now in known_issue_types internally. Calling detect again with same current_issues
        # should not produce new anomalies for "issueFlag", as it is no longer a candidate with streak >= threshold.
        anomalies2 = self.analyzer.detect_new_frequent_issue_types(context_key, {"issueFlag"})
        self.assertEqual(anomalies2, [], "Issue should not be re-flagged as it is now known.")

        issue_baseline = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertNotIn("issueFlag", issue_baseline["new_issue_candidates"])
        self.assertIn("issueFlag", issue_baseline["known_issue_types"])

    def test_analyze_iar_stream_for_anomalies_integration(self):
        """Test integration of different anomaly detection types within analyze_iar_stream_for_anomalies."""
        context_key = "TestContext_AnalysisIntegration"
        # DEFAULT_METRIC_THRESHOLDS["new_issue_frequency_threshold"] is 3
        # DEFAULT_METRIC_THRESHOLDS["confidence_drop_std_devs"] is 2.5

        # 1. Establish a baseline for confidence (e.g., mean around 0.9, small std_dev)
        #    Also establish baseline issues (e.g., no initial issues, or one common one that won't be in anomaly stream)
        
        # Manually establish confidence baseline
        for val in [0.9, 0.92, 0.88, 0.91] * 25: # 100 records
            self.analyzer.update_metric_baseline(context_key, "average_confidence", val)

        # Establish issue baseline (common_hiccup)
        baseline_iars_for_issues = [
            {"status": "Success", "confidence": 0.9, "potential_issues": ["common_hiccup"]},
            {"status": "Success", "confidence": 0.92, "potential_issues": []},
            {"status": "Success", "confidence": 0.88, "potential_issues": ["common_hiccup"]},
            {"status": "Success", "confidence": 0.91, "potential_issues": []},
        ] * 3 # Process a few times to get common_hiccup as candidate
        
        # Call analyze_iar_stream to process these and update issue baselines
        # This also adds to the confidence baseline count from their averages if not None
        self.analyzer.analyze_iar_stream_for_anomalies(context_key, baseline_iars_for_issues)


        # Call with an empty issue set to move common_hiccup to known_issue_types
        self.analyzer.analyze_iar_stream_for_anomalies(context_key, [{"status": "Success", "confidence": 0.9, "potential_issues": []}])

        # Verify common_hiccup is known and not a candidate
        issue_baseline_after_setup = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertIn("common_hiccup", issue_baseline_after_setup["known_issue_types"])
        self.assertEqual(issue_baseline_after_setup["new_issue_candidates"], {})
        
        # 2. Prepare an IAR stream that should trigger:
        #    a) A confidence drop (e.g., current confidence of 0.5)
        #    b) A new frequent issue (e.g., "new_bug" appearing >= 3 times)
        
        # To make "new_bug" appear 3 times and trigger detection in ONE call to analyze_iar_stream_for_anomalies,
        # we need to ensure its streak hits 3 *within the processing of this single stream*.
        # The current implementation of analyze_iar_stream calls update_issue_type_baselines ONCE with all unique issues from the stream.
        # Then calls detect_new_frequent_issue_types ONCE.
        # So, for "new_bug" to be detected, it needs to have hit its streak *before* this call to analyze_iar_stream_for_anomalies
        # OR the stream itself must be processed multiple times. 
        # Let's adjust the test to show this: we process a stream 3 times to get "new_bug" to threshold.

        # Stream 1 for new_bug (streak 1)
        anomaly_stream_part1 = [
            {"status": "Success", "confidence": 0.85, "potential_issues": ["new_bug"]}
        ]
        self.analyzer.analyze_iar_stream_for_anomalies(context_key, anomaly_stream_part1)
        issue_baseline_part1 = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline_part1["new_issue_candidates"].get("new_bug"), 1)

        # Stream 2 for new_bug (streak 2)
        anomaly_stream_part2 = [
            {"status": "Success", "confidence": 0.82, "potential_issues": ["new_bug"]}
        ]
        self.analyzer.analyze_iar_stream_for_anomalies(context_key, anomaly_stream_part2)
        issue_baseline_part2 = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertEqual(issue_baseline_part2["new_issue_candidates"].get("new_bug"), 2)

        # Add one more call to ensure baseline count for confidence is >= 5 (already well over by manual update)
        # self.analyzer.analyze_iar_stream_for_anomalies(context_key, [
        #     {"status": "Success", "confidence": 0.89, "potential_issues": ["filler_issue"]}
        # ])
        # The print statement below uses the result of the previous analyze_iar_stream call (empty issues)
        # which does update the confidence baseline with its average (0.9 in this case).
        confidence_baseline_stats = self.analyzer.baselines[context_key].get("average_confidence", {})
        print(f"DEBUG: Confidence baseline count before final stream: {confidence_baseline_stats.get('count')}")

        # Stream 3 for new_bug (streak 3) AND confidence drop
        anomaly_stream_final = [
            {"status": "Success", "confidence": 0.5, "potential_issues": ["new_bug"]}, # Confidence drop here
            {"status": "Success", "confidence": 0.52, "potential_issues": ["new_bug"]},
            {"status": "Failure", "confidence": 0.48, "potential_issues": ["new_bug", "other_issue_in_stream"]}
        ]
        
        detected_anomalies = self.analyzer.analyze_iar_stream_for_anomalies(context_key, anomaly_stream_final)

        self.assertTrue(len(detected_anomalies) >= 2, f"Expected at least 2 anomalies, got {len(detected_anomalies)}")

        confidence_drop_found = False
        new_frequent_issue_found = False

        for anomaly in detected_anomalies:
            if anomaly["anomaly_type"] == "SignificantConfidenceDrop":
                confidence_drop_found = True
                self.assertAlmostEqual(anomaly["current_value"], np.mean([0.5, 0.52, 0.48]))
            elif anomaly["anomaly_type"] == "NewFrequentIssue":
                new_frequent_issue_found = True
                self.assertEqual(anomaly["issue_type"], "new_bug")
                self.assertEqual(anomaly["appearance_streak"], 3)
        
        self.assertTrue(confidence_drop_found, "SignificantConfidenceDrop anomaly was not detected.")
        self.assertTrue(new_frequent_issue_found, "NewFrequentIssue anomaly for 'new_bug' was not detected.")

        # Verify "new_bug" is now known
        issue_baseline_final = self.analyzer.baselines[context_key]["issue_baseline"]
        self.assertIn("new_bug", issue_baseline_final["known_issue_types"])
        self.assertNotIn("new_bug", issue_baseline_final["new_issue_candidates"])
        # "other_issue_in_stream" appeared once, should be a candidate
        self.assertEqual(issue_baseline_final["new_issue_candidates"].get("other_issue_in_stream"), 1)

if __name__ == '__main__':
    unittest.main()
