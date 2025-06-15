import unittest
from datetime import datetime
from Three_PointO_ArchE.thought_trail import ThoughtTrail
import json
import os
import tempfile

class TestThoughtTrail(unittest.TestCase):
    def setUp(self):
        self.trail = ThoughtTrail(max_history=5)
        self.sample_entry = {
            'task_id': 'test_task_1',
            'action_type': 'test_action',
            'inputs': {'param1': 'value1'},
            'outputs': {'result': 'success'},
            'iar_reflection': {
                'status': 'Success',
                'confidence': 0.9,
                'potential_issues': None
            }
        }
    
    def test_add_entry(self):
        entry = self.trail.add_entry(**self.sample_entry)
        self.assertEqual(len(self.trail.trail), 1)
        self.assertEqual(entry['task_id'], 'test_task_1')
        self.assertIn('timestamp', entry)
    
    def test_get_recent_entries(self):
        # Add multiple entries
        for i in range(3):
            self.sample_entry['task_id'] = f'test_task_{i}'
            self.trail.add_entry(**self.sample_entry)
        
        recent = self.trail.get_recent_entries(count=2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[-1]['task_id'], 'test_task_2')
    
    def test_get_entries_by_task_id(self):
        # Add entries with different task IDs
        self.trail.add_entry(**self.sample_entry)
        self.sample_entry['task_id'] = 'test_task_2'
        self.trail.add_entry(**self.sample_entry)
        
        entries = self.trail.get_entries_by_task_id('test_task_1')
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['task_id'], 'test_task_1')
    
    def test_get_entries_with_dissonance(self):
        # Add entries with and without dissonance
        self.trail.add_entry(**self.sample_entry)  # No dissonance
        
        dissonant_entry = self.sample_entry.copy()
        dissonant_entry['iar_reflection'] = {
            'status': 'Success',
            'confidence': 0.5,  # Low confidence
            'potential_issues': ['Potential problem detected']
        }
        self.trail.add_entry(**dissonant_entry)
        
        dissonant_entries = self.trail.get_entries_with_dissonance()
        self.assertEqual(len(dissonant_entries), 1)
        self.assertEqual(dissonant_entries[0]['iar_reflection']['confidence'], 0.5)
    
    def test_get_context_surrounding_dissonance(self):
        # Add multiple entries
        for i in range(5):
            entry = self.sample_entry.copy()
            entry['task_id'] = f'test_task_{i}'
            if i == 2:  # Middle entry has dissonance
                entry['iar_reflection'] = {
                    'status': 'Success',
                    'confidence': 0.5,
                    'potential_issues': ['Issue detected']
                }
            self.trail.add_entry(**entry)
        
        dissonant_entry = self.trail.trail[2]
        context = self.trail.get_context_surrounding_dissonance(dissonant_entry, context_depth=1)
        self.assertEqual(len(context), 3)  # Dissonant entry + 1 before + 1 after
    
    def test_export_import(self):
        # Add some entries
        for i in range(3):
            self.sample_entry['task_id'] = f'test_task_{i}'
            self.trail.add_entry(**self.sample_entry)
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
        
        try:
            self.trail.export_trail(temp_path)
            
            # Create new trail and import
            new_trail = ThoughtTrail()
            new_trail.import_trail(temp_path)
            
            self.assertEqual(len(new_trail.trail), 3)
            self.assertEqual(new_trail.trail[0]['task_id'], 'test_task_0')
        finally:
            os.unlink(temp_path)
    
    def test_history_trimming(self):
        # Add more entries than max_history
        for i in range(7):  # max_history is 5
            self.sample_entry['task_id'] = f'test_task_{i}'
            self.trail.add_entry(**self.sample_entry)
        
        self.assertEqual(len(self.trail.trail), 5)  # Should be trimmed
        self.assertEqual(self.trail.trail[0]['task_id'], 'test_task_2')  # Oldest remaining
    
    def test_context_update(self):
        initial_context = {'key1': 'value1'}
        self.trail.update_current_context(initial_context)
        
        # Add entry without explicit context
        entry = self.trail.add_entry(**self.sample_entry)
        self.assertEqual(entry['context'], initial_context)
        
        # Update context
        new_context = {'key2': 'value2'}
        self.trail.update_current_context(new_context)
        
        # Add another entry
        entry = self.trail.add_entry(**self.sample_entry)
        self.assertEqual(entry['context'], {'key1': 'value1', 'key2': 'value2'})

if __name__ == '__main__':
    unittest.main() 