#!/usr/bin/env python3
"""
Natural Language Interface for ArchE
Converts natural language questions into structured ArchE workflow inputs
"""

import json
import sys
import os
from typing import Dict, Any, List
import argparse

# Add ArchE to path
sys.path.append('Three_PointO_ArchE')
from knowledge_graph_manager import KnowledgeGraphManager

class ArchENaturalLanguageInterface:
    """
    Converts natural language questions into structured ArchE inputs
    """
    
    def __init__(self):
        self.kg = KnowledgeGraphManager(
            'Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json',
            'Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json',
            'specifications'
        )
        
    def parse_natural_language_question(self, question: str) -> Dict[str, Any]:
        """
        Parse a natural language question into structured ArchE format
        """
        # Extract key components from the question
        parsed = {
            'goal': self._extract_goal(question),
            'constraints': self._extract_constraints(question),
            'desired_outputs': self._extract_desired_outputs(question),
            'context_type': self._classify_question_type(question),
            'relevant_specifications': self._find_relevant_specs(question)
        }
        
        return parsed
    
    def _extract_goal(self, question: str) -> str:
        """Extract the main goal from the question"""
        # Simple extraction - look for question words and main intent
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['how', 'what', 'why', 'when', 'where', 'who']):
            return question.strip()
        
        # If it's a statement, treat it as a goal
        return question.strip()
    
    def _extract_constraints(self, question: str) -> Dict[str, str]:
        """Extract constraints from the question"""
        constraints = {}
        question_lower = question.lower()
        
        # Look for constraint indicators
        if 'urgent' in question_lower or 'asap' in question_lower:
            constraints['urgency'] = 'high'
        
        if 'detailed' in question_lower or 'comprehensive' in question_lower:
            constraints['detail_level'] = 'high'
        
        if 'simple' in question_lower or 'brief' in question_lower:
            constraints['detail_level'] = 'low'
        
        if 'creative' in question_lower or 'innovative' in question_lower:
            constraints['creativity'] = 'required'
        
        if 'technical' in question_lower:
            constraints['technical_depth'] = 'required'
        
        if 'self' in question_lower or 'your' in question_lower:
            constraints['self_analysis'] = 'required'
        
        return constraints
    
    def _extract_desired_outputs(self, question: str) -> List[str]:
        """Extract desired outputs from the question"""
        outputs = []
        question_lower = question.lower()
        
        # Common output patterns
        if 'analyze' in question_lower:
            outputs.append('Analysis report')
        
        if 'explain' in question_lower:
            outputs.append('Explanation')
        
        if 'recommend' in question_lower or 'suggest' in question_lower:
            outputs.append('Recommendations')
        
        if 'create' in question_lower or 'build' in question_lower:
            outputs.append('Implementation plan')
        
        if 'compare' in question_lower:
            outputs.append('Comparison analysis')
        
        if 'fix' in question_lower or 'solve' in question_lower:
            outputs.append('Solution')
        
        # Default output if none detected
        if not outputs:
            outputs.append('Comprehensive response')
        
        return outputs
    
    def _classify_question_type(self, question: str) -> str:
        """Classify the type of question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['how', 'create', 'build', 'implement']):
            return 'implementation'
        elif any(word in question_lower for word in ['what', 'explain', 'define']):
            return 'explanatory'
        elif any(word in question_lower for word in ['why', 'analyze', 'understand']):
            return 'analytical'
        elif any(word in question_lower for word in ['compare', 'versus', 'vs']):
            return 'comparative'
        elif any(word in question_lower for word in ['fix', 'solve', 'problem']):
            return 'problem_solving'
        elif any(word in question_lower for word in ['self', 'your', 'arche']):
            return 'self_analysis'
        else:
            return 'general'
    
    def _find_relevant_specs(self, question: str) -> List[str]:
        """Find relevant ArchE specifications for the question"""
        # Search specifications for relevant content
        results = self.kg.search_specifications(question)
        return [result['spec_name'] for result in results[:5]]  # Top 5 relevant specs
    
    def generate_arche_command(self, question: str) -> str:
        """Generate the complete ArchE command for the question"""
        parsed = self.parse_natural_language_question(question)
        
        # Create the context JSON
        context = {
            'goal': parsed['goal'],
            'constraints': parsed['constraints'],
            'desired_outputs': parsed['desired_outputs']
        }
        
        # Generate the command
        context_json = json.dumps(context).replace('"', '\\"')
        command = f'python3 execute_playbook.py Happier/workflows/distributed_resonant_corrective_loop.json --context "{context_json}"'
        
        return command
    
    def ask_arche(self, question: str) -> str:
        """Ask ArchE a question and return the response"""
        command = self.generate_arche_command(question)
        
        print(f"🤖 ArchE Natural Language Interface")
        print(f"📝 Question: {question}")
        print(f"🔧 Generated Command: {command}")
        print(f"🚀 Executing ArchE...")
        
        # Execute the command
        import subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='/media/newbu/3626C55326C514B1/Happier')
            return result.stdout
        except Exception as e:
            return f"Error executing ArchE: {e}"

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Natural Language Interface for ArchE')
    parser.add_argument('question', nargs='?', help='The question to ask ArchE')
    parser.add_argument('--parse-only', action='store_true', help='Only parse the question, don\'t execute')
    
    args = parser.parse_args()
    
    interface = ArchENaturalLanguageInterface()
    
    if args.question:
        if args.parse_only:
            # Just parse and show the structure
            parsed = interface.parse_natural_language_question(args.question)
            print("🎯 Parsed Question Structure:")
            print(json.dumps(parsed, indent=2))
        else:
            # Ask ArchE the question
            response = interface.ask_arche(args.question)
            print("📋 ArchE Response:")
            print(response)
    else:
        # Interactive mode
        print("🤖 ArchE Natural Language Interface")
        print("Type your questions (or 'quit' to exit):")
        
        while True:
            question = input("\n❓ Your question: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if question:
                parsed = interface.parse_natural_language_question(question)
                print(f"\n🎯 Parsed as:")
                print(f"   Goal: {parsed['goal']}")
                print(f"   Type: {parsed['context_type']}")
                print(f"   Constraints: {parsed['constraints']}")
                print(f"   Outputs: {parsed['desired_outputs']}")
                
                confirm = input("\n🚀 Execute with ArchE? (y/n): ").strip().lower()
                if confirm == 'y':
                    response = interface.ask_arche(question)
                    print(f"\n📋 ArchE Response:")
                    print(response)

if __name__ == "__main__":
    main()
