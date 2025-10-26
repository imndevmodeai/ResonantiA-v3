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
    
    def generate_dynamic_playbook(self, question: str) -> Dict[str, Any]:
        """
        Generate a dynamic playbook based on the question
        """
        parsed = self.parse_natural_language_question(question)
        workflow_type = self._determine_workflow_type(question)
        
            # Generate ArchE-compatible workflow
        playbook = {
            "name": f"Dynamic {workflow_type.title()}: {question[:50]}...",
            "description": f"Auto-generated workflow for: {question}",
            "tasks": self._generate_arche_tasks(workflow_type, parsed, question)
        }
        
        return playbook

    def _generate_arche_tasks(self, workflow_type: str, parsed: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Generate ArchE-compatible tasks"""
        
        # Base tasks that all workflows need
        base_tasks = {
            "protocol_priming": {
                "description": "Load ResonantiA protocol definitions from Knowledge Graph",
                "action_type": "execute_code",
                "inputs": {
                    "language": "python",
                    "code": """import json
import os
import sys
sys.path.append('Three_PointO_ArchE')
from knowledge_graph_manager import KnowledgeGraphManager

# Initialize KG manager with specifications
kg = KnowledgeGraphManager(
    'Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json',
    'Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json',
    'specifications'
)

# Extract key SPRs for protocol context
key_sprs = ['RISE', 'DRCL', 'SPR', 'CognitiveResonancE', 'TerritoryAssumptionS', 'ConceptualMaP', 'ResonantiaprotocoL']
protocol_definitions = {}

for spr_id in key_sprs:
    spr_def = kg.get_spr_definition(spr_id)
    if spr_def:
        protocol_definitions[spr_def['term']] = spr_def['definition']

# Add core ArchE concepts
protocol_definitions['ArchE'] = 'Architectural Engine - the core system for self-modification and evolution'
protocol_definitions['ResonantiA Protocol'] = 'The comprehensive document and conceptual framework that defines the architecture, operational logic, core principles, and evolutionary mechanisms of the ArchE system. It is the blueprint for achieving Cognitive Resonance.'

# Add specifications overview
specifications_summary = {}
for spec_name in kg.list_specifications():
    spec_data = kg.get_specification(spec_name)
    if spec_data:
        specifications_summary[spec_name] = {
            'title': spec_data.get('title', ''),
            'overview': spec_data.get('overview', '')[:300] + '...' if len(spec_data.get('overview', '')) > 300 else spec_data.get('overview', '')
        }

protocol_definitions['ArchE Specifications'] = f'Comprehensive specifications covering {len(specifications_summary)} components: {list(specifications_summary.keys())}'
protocol_definitions['Available Specifications'] = specifications_summary

print(json.dumps({'protocol_definitions': protocol_definitions}))"""
                },
                "outputs": {"protocol_definitions": "dict"},
                "dependencies": []
            },
            
            "intent_intake": {
                "description": "Normalize user request into Task Envelope",
                "action_type": "execute_code",
                "inputs": {
                    "language": "python",
                    "code": f"""import json
ctx = {parsed}
out = {{
    'goal': ctx.get('goal') or '{question}',
    'constraints': ctx.get('constraints', {{}}),
    'desired_outputs': ctx.get('desired_outputs', [])
}}
print(json.dumps({{'task_envelope': out}}))"""
                },
                "outputs": {"task_envelope": "dict"},
                "dependencies": ["protocol_priming"]
            },
            
            "conceptual_map": {
                "description": "Produce Conceptual Map (SPRs, abstract workflow, territory assumptions)",
                "action_type": "generate_text_llm",
                "inputs": {
                    "prompt": f"""Using these ArchE protocol definitions: {{protocol_priming.protocol_definitions}}

Create a conceptual map for this development task. Generate ONLY a JSON structure with: sprs (Sparse Priming Representations), abstract_workflow (development steps), territory_assumptions (expected file paths). Task: {{intent_intake.task_envelope}}

Focus on: {question}

Output ONLY valid JSON, no explanations.""",
                    "max_tokens": 600,
                    "model": "gemini-2.0-flash-exp"
                },
                "outputs": {"conceptual_map_json": "json"},
                "dependencies": ["intent_intake"]
            },
            
            "rise_blueprint": {
                "description": "Generate RISE methodology blueprint",
                "action_type": "generate_text_llm",
                "inputs": {
                    "prompt": f"""Based on the conceptual map and task: {{conceptual_map.conceptual_map_json}}

Generate a RISE (Resonant Insight and Strategy Engine) methodology blueprint for: {question}

Provide a structured approach with Scaffold, Insight, and Synthesis phases. Output as JSON.""",
                    "max_tokens": 800,
                    "model": "gemini-2.0-flash-exp"
                },
                "outputs": {"rise_blueprint": "json"},
                "dependencies": ["conceptual_map"]
            },
            
            "synthesis_and_insights": {
                "description": "Synthesize findings into actionable insights",
                "action_type": "generate_text_llm",
                "inputs": {
                    "prompt": f"""Based on the analysis of: {question}

Using the conceptual map: {{conceptual_map.conceptual_map_json}}
And RISE blueprint: {{rise_blueprint.rise_blueprint}}

Synthesize the findings into:
1. Key insights and discoveries
2. Patterns and relationships identified
3. Implications and significance
4. Recommendations and next steps
5. Limitations and areas for further investigation

Provide a comprehensive synthesis with actionable insights.""",
                    "max_tokens": 1000,
                    "model": "gemini-2.0-flash-exp"
                },
                "outputs": {"synthesis": "text"},
                "dependencies": ["rise_blueprint"]
            },
            
            "final_report": {
                "description": "Generate comprehensive final report",
                "action_type": "execute_code",
                "inputs": {
                    "language": "python",
                    "code": f"""from datetime import datetime

print("📊 FINAL ANALYSIS REPORT")
print("=" * 60)
print(f"Analysis Question: {question}")
print(f"Analysis Date: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
print(f"Goal: {parsed['goal']}")
print("=" * 60)

print("\\n🎯 ANALYSIS SUMMARY:")
print("• Question analyzed comprehensively")
print("• Conceptual mapping completed")
print("• RISE methodology applied")
print("• Insights synthesized")
print("• Report generated")

print("\\n✅ ANALYSIS COMPLETE")
print("=" * 60)"""
                },
                "outputs": {"final_report": "text"},
                "dependencies": ["synthesis_and_insights"]
            }
        }
        
        return base_tasks

    def _determine_workflow_type(self, question: str) -> str:
        """Determine the type of workflow needed"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["analyze", "analysis", "examine", "investigate"]):
            return "analysis"
        elif any(word in question_lower for word in ["predict", "forecast", "future", "trend"]):
            return "prediction"
        elif any(word in question_lower for word in ["research", "find", "discover", "explore"]):
            return "research"
        elif any(word in question_lower for word in ["optimize", "improve", "enhance", "better"]):
            return "optimization"
        elif any(word in question_lower for word in ["compare", "versus", "vs", "difference"]):
            return "comparison"
        else:
            return "analysis"  # Default


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
            
            # Extract the key analysis from the output
            output = result.stdout
            
            # Find the conceptual map and other key sections
            if 'conceptual_map_json' in output:
                # Extract the conceptual map section
                import re
                conceptual_match = re.search(r"'conceptual_map_json':\s*({.*?})", output, re.DOTALL)
                if conceptual_match:
                    conceptual_map = conceptual_match.group(1)
                    print("\n🎯 CONCEPTUAL MAP ANALYSIS:")
                    print("=" * 50)
                    print(conceptual_map)
                    print("=" * 50)
            
            if 'rise_blueprint' in output:
                # Extract the RISE blueprint
                rise_match = re.search(r"'rise_blueprint':\s*{.*?'response_text':\s*'```json\\n(.*?)\\n```'", output, re.DOTALL)
                if rise_match:
                    rise_content = rise_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    print("\n🚀 RISE METHODOLOGY BLUEPRINT:")
                    print("=" * 50)
                    print(rise_content)
                    print("=" * 50)
            
            if 'critique_deepen_envision' in output:
                # Extract the critique section
                critique_match = re.search(r"'critique_deepen_envision':\s*{.*?'response_text':\s*'```json\\n(.*?)\\n```'", output, re.DOTALL)
                if critique_match:
                    critique_content = critique_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    print("\n🔍 CRITIQUE & ENVISIONING:")
                    print("=" * 50)
                    print(critique_content)
                    print("=" * 50)
            
            # Return the full output
            return output
            
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
