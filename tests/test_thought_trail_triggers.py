import unittest
from Three_PointO_ArchE.thought_trail import ThoughtTrail, TriggerType

class TestThoughtTrailTriggers(unittest.TestCase):
    def setUp(self):
        self.trail = ThoughtTrail()
        self.triggered_events = []
        
    def trigger_handler(self, entry):
        self.triggered_events.append(entry)
    
    def test_dissonance_trigger(self):
        """Test that dissonance triggers are automatically detected and handled."""
        # Register handler
        self.trail.register_trigger_handler(TriggerType.DISSONANCE, self.trigger_handler)
        
        # Add entry with dissonance
        entry = self.trail.add_entry(
            task_id='test_task',
            action_type='test_action',
            inputs={'param': 'value'},
            outputs={'result': 'success'},
            iar_reflection={
                'status': 'Success',
                'confidence': 0.9,
                'potential_issues': ['Test issue']
            }
        )
        
        # Verify trigger was executed
        self.assertEqual(len(self.triggered_events), 1)
        self.assertEqual(self.triggered_events[0], entry)
    
    def test_low_confidence_trigger(self):
        """Test that low confidence triggers are automatically detected and handled."""
        # Register handler
        self.trail.register_trigger_handler(TriggerType.LOW_CONFIDENCE, self.trigger_handler)
        
        # Add entry with low confidence
        entry = self.trail.add_entry(
            task_id='test_task',
            action_type='test_action',
            inputs={'param': 'value'},
            outputs={'result': 'success'},
            iar_reflection={
                'status': 'Success',
                'confidence': 0.5,  # Below threshold
                'potential_issues': None
            }
        )
        
        # Verify trigger was executed
        self.assertEqual(len(self.triggered_events), 1)
        self.assertEqual(self.triggered_events[0], entry)
    
    def test_pattern_detector(self):
        """Test that pattern detectors can trigger analysis."""
        # Define pattern detector
        def detect_pattern(entry):
            return entry['action_type'] == 'special_action'
        
        # Register pattern detector and handler
        self.trail.register_pattern_detector(detect_pattern)
        self.trail.register_trigger_handler(TriggerType.PATTERN_DETECTED, self.trigger_handler)
        
        # Add entry matching pattern
        entry = self.trail.add_entry(
            task_id='test_task',
            action_type='special_action',
            inputs={'param': 'value'},
            outputs={'result': 'success'},
            iar_reflection={
                'status': 'Success',
                'confidence': 0.9,
                'potential_issues': None
            }
        )
        
        # Verify trigger was executed
        self.assertEqual(len(self.triggered_events), 1)
        self.assertEqual(self.triggered_events[0], entry)
    
    def test_metacognitive_shift_trigger(self):
        """Test that Metacognitive shifT triggers are automatically detected and handled."""
        # Register handler
        self.trail.register_trigger_handler(TriggerType.METACOGNITIVE_SHIFT, self.trigger_handler)
        
        # Add entry with Metacognitive shifT
        entry = self.trail.add_entry(
            task_id='test_task',
            action_type='metacognitive_shift',
            inputs={'param': 'value'},
            outputs={'result': 'success'},
            iar_reflection={
                'status': 'Success',
                'confidence': 0.9,
                'potential_issues': None
            }
        )
        
        # Verify trigger was executed
        self.assertEqual(len(self.triggered_events), 1)
        self.assertEqual(self.triggered_events[0], entry)
    
    def test_multiple_triggers(self):
        """Test that multiple triggers can be detected in a single entry."""
        # Register handlers for multiple trigger types
        self.trail.register_trigger_handler(TriggerType.DISSONANCE, self.trigger_handler)
        self.trail.register_trigger_handler(TriggerType.LOW_CONFIDENCE, self.trigger_handler)
        
        # Add entry that triggers both
        entry = self.trail.add_entry(
            task_id='test_task',
            action_type='test_action',
            inputs={'param': 'value'},
            outputs={'result': 'success'},
            iar_reflection={
                'status': 'Success',
                'confidence': 0.5,  # Below threshold
                'potential_issues': ['Test issue']  # Has issues
            }
        )
        
        # Verify both triggers were executed
        self.assertEqual(len(self.triggered_events), 2)
        self.assertEqual(self.triggered_events[0], entry)
        self.assertEqual(self.triggered_events[1], entry)
    
    def test_trigger_handler_error_handling(self):
        """Test that errors in trigger handlers are properly handled."""
        def failing_handler(entry):
            raise Exception("Test error")
        
        # Register failing handler
        self.trail.register_trigger_handler(TriggerType.DISSONANCE, failing_handler)
        
        # Add entry that should trigger the handler
        entry = self.trail.add_entry(
            task_id='test_task',
            action_type='test_action',
            inputs={'param': 'value'},
            outputs={'result': 'success'},
            iar_reflection={
                'status': 'Success',
                'confidence': 0.9,
                'potential_issues': ['Test issue']
            }
        )
        
        # Verify the entry was still added despite handler error
        self.assertEqual(len(self.trail.trail), 1)
        self.assertEqual(self.trail.trail[0], entry)

if __name__ == '__main__':
    unittest.main() 