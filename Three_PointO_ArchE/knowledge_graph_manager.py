import json
import os
from typing import Dict, Any, List
from pathlib import Path

class KnowledgeGraphManager:
    """
    Manages the knowledge graph, including loading, saving, and querying.
    Now includes comprehensive specifications integration.
    """
    def __init__(self, spr_definitions_path: str, knowledge_tapestry_path: str, specifications_path: str = "specifications"):
        self.spr_definitions_path = spr_definitions_path
        self.knowledge_tapestry_path = knowledge_tapestry_path
        self.specifications_path = specifications_path
        self.spr_definitions = self._load_json(self.spr_definitions_path)
        self.knowledge_tapestry = self._load_json(self.knowledge_tapestry_path)
        self.specifications = self._load_specifications()

    def _load_json(self, path: str) -> Dict[str, Any]:
        """Loads a JSON file."""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_spr_definition(self, spr_id: str) -> Dict[str, Any]:
        """Retrieves a specific SPR definition."""
        if isinstance(self.spr_definitions, list):
            # SPR definitions is a list of dictionaries
            for spr in self.spr_definitions:
                if spr.get('spr_id') == spr_id:
                    return spr
            return {}
        else:
            # SPR definitions is a dictionary
            return self.spr_definitions.get(spr_id, {})

    def get_tapestry_node(self, node_id: str) -> Dict[str, Any]:
        """Retrieves a specific node from the knowledge tapestry."""
        return self.knowledge_tapestry.get(node_id, {})

    def _load_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Loads all specifications from the specifications directory."""
        specifications = {}
        
        if not os.path.exists(self.specifications_path):
            return specifications
            
        for file_path in Path(self.specifications_path).glob("*.md"):
            try:
                spec_name = file_path.stem
                spec_content = self._load_markdown_specification(str(file_path))
                if spec_content:
                    specifications[spec_name] = spec_content
            except Exception as e:
                print(f"Warning: Could not load specification {file_path}: {e}")
                
        return specifications

    def _load_markdown_specification(self, file_path: str) -> Dict[str, Any]:
        """Loads and parses a markdown specification file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract key sections from the markdown
            spec_data = {
                'file_path': file_path,
                'raw_content': content,
                'title': self._extract_title(content),
                'overview': self._extract_section(content, 'Overview'),
                'philosophical_mandate': self._extract_section(content, 'Philosophical Mandate'),
                'allegory': self._extract_section(content, 'Allegory'),
                'technical_implementation': self._extract_section(content, 'Technical Implementation'),
                'key_capabilities': self._extract_section(content, 'Key Capabilities'),
                'usage_examples': self._extract_section(content, 'Usage Examples'),
                'spr_integration': self._extract_section(content, 'SPR Integration'),
                'conclusion': self._extract_section(content, 'Conclusion')
            }
            
            return spec_data
            
        except Exception as e:
            print(f"Error loading specification {file_path}: {e}")
            return {}

    def _extract_title(self, content: str) -> str:
        """Extracts the main title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Unknown Specification"

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extracts a specific section from markdown content."""
        lines = content.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            # Check if this line starts a section
            if line.startswith('## ') and section_name.lower() in line.lower():
                in_section = True
                continue
            elif line.startswith('## ') and in_section:
                # Found next section, stop
                break
            elif in_section:
                section_content.append(line)
        
        return '\n'.join(section_content).strip()

    def get_specification(self, spec_name: str) -> Dict[str, Any]:
        """Retrieves a specific specification by name."""
        return self.specifications.get(spec_name, {})

    def list_specifications(self) -> List[str]:
        """Lists all available specification names."""
        return list(self.specifications.keys())

    def search_specifications(self, query: str) -> List[Dict[str, Any]]:
        """Searches specifications for content matching the query."""
        results = []
        query_lower = query.lower()
        
        for spec_name, spec_data in self.specifications.items():
            # Search in title, overview, and key sections
            searchable_content = [
                spec_data.get('title', ''),
                spec_data.get('overview', ''),
                spec_data.get('philosophical_mandate', ''),
                spec_data.get('technical_implementation', '')
            ]
            
            if any(query_lower in content.lower() for content in searchable_content):
                results.append({
                    'spec_name': spec_name,
                    'title': spec_data.get('title', ''),
                    'overview': spec_data.get('overview', '')[:200] + '...' if len(spec_data.get('overview', '')) > 200 else spec_data.get('overview', ''),
                    'relevance_score': self._calculate_relevance(query_lower, searchable_content)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results

    def _calculate_relevance(self, query: str, content_list: List[str]) -> float:
        """Calculates relevance score for search results."""
        score = 0.0
        for content in content_list:
            content_lower = content.lower()
            # Count occurrences of query terms
            score += content_lower.count(query)
            # Bonus for title matches
            if content == content_list[0] and query in content_lower:
                score += 2.0
        return score 