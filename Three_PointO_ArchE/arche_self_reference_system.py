"""
ArchE Self-Reference System - Universal Abstraction for Dynamic Component Access
Implements MANDATE 14: Universal Abstraction for deterministic self-reference

This system allows ArchE to dynamically reference and use different parts of itself
based on queries, similar to Cursor IDE's @ file reference feature.
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComponentReference:
    """Represents a referenceable component in ArchE."""
    ref_id: str  # e.g., "@PRIME_ARCHE_PROTOCOL.md", "@SPRManager", "@CognitiveResonancE"
    component_type: str  # "file", "class", "function", "spr", "workflow", "protocol"
    path: str  # File path or identifier
    name: str  # Display name
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    content_preview: str = ""  # First 500 chars for preview


class ArcheSelfReferenceSystem:
    """
    Universal Abstraction system for ArchE to reference itself dynamically.
    
    Strategy (MANDATE 14):
    1. Representation: Build lookup tables of all components
    2. Comparison: Pattern matching via keywords and metadata
    3. Learning: Track usage patterns for better matching
    4. Crystallization: Deterministic rules for component selection
    """
    
    def __init__(self, project_root: Path):
        """Initialize the self-reference system."""
        self.project_root = Path(project_root)
        self.components: Dict[str, ComponentReference] = {}
        self.index_by_keyword: Dict[str, Set[str]] = defaultdict(set)
        self.index_by_type: Dict[str, Set[str]] = defaultdict(set)
        self.usage_patterns: Dict[str, int] = defaultdict(int)
        
        # Build component index
        self._build_component_index()
    
    def _build_component_index(self):
        """Build deterministic lookup tables for all components."""
        logger.info("Building ArchE self-reference index...")
        
        # 1. Index all files
        self._index_files()
        
        # 2. Index Python classes and functions
        self._index_code_components()
        
        # 3. Index SPRs
        self._index_sprs()
        
        # 4. Index workflows
        self._index_workflows()
        
        # 5. Index protocol documents
        self._index_protocols()
        
        logger.info(f"Indexed {len(self.components)} components")
    
    def _index_files(self):
        """Index all relevant files in the project."""
        file_patterns = {
            '*.md': 'document',
            '*.py': 'code',
            '*.json': 'data',
            '*.yaml': 'config',
            '*.yml': 'config'
        }
        
        for pattern, file_type in file_patterns.items():
            try:
                for file_path in self.project_root.rglob(pattern):
                    # Skip common exclusions
                    skip_patterns = ['__pycache__', '.git', 'node_modules', '.venv', 'arche_env', 
                                     'backup', 'quarantine', '.next', 'dist', 'build']
                    if any(skip in str(file_path) for skip in skip_patterns):
                        continue
                    
                    try:
                        # Check if file is accessible
                        if not file_path.exists():
                            continue
                        
                        # Try to get file size (will fail if file is inaccessible)
                        try:
                            file_size = file_path.stat().st_size
                        except (OSError, PermissionError):
                            continue
                        
                        rel_path = file_path.relative_to(self.project_root)
                        ref_id = f"@{file_path.name}"
                        
                        # Skip if already indexed (avoid duplicates)
                        if ref_id in self.components:
                            continue
                        
                        # Extract keywords from filename
                        keywords = self._extract_keywords_from_filename(file_path.name)
                        
                        # Get content preview
                        preview = self._get_file_preview(file_path)
                        
                        component = ComponentReference(
                            ref_id=ref_id,
                            component_type=file_type,
                            path=str(rel_path),
                            name=file_path.name,
                            description=f"{file_type.title()} file: {rel_path}",
                            keywords=keywords,
                            content_preview=preview,
                            metadata={
                                "file_type": file_type,
                                "size": file_size,
                                "extension": file_path.suffix
                            }
                        )
                        
                        self.components[ref_id] = component
                        self._add_to_indexes(component)
                    except (OSError, PermissionError, UnicodeDecodeError) as e:
                        logger.debug(f"Skipping {file_path}: {e}")
                        continue
            except Exception as e:
                logger.warning(f"Error indexing {pattern}: {e}")
                continue
    
    def _index_code_components(self):
        """Index Python classes and functions."""
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'node_modules', '.venv', 'arche_env']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract classes
                class_matches = re.finditer(r'^class\s+(\w+).*?:', content, re.MULTILINE)
                for match in class_matches:
                    class_name = match.group(1)
                    ref_id = f"@{class_name}"
                    
                    # Get class docstring if available
                    docstring = self._extract_docstring_after_match(content, match.end())
                    
                    keywords = self._extract_keywords_from_text(class_name + " " + docstring)
                    
                    component = ComponentReference(
                        ref_id=ref_id,
                        component_type="class",
                        path=str(py_file.relative_to(self.project_root)),
                        name=class_name,
                        description=docstring[:200] if docstring else f"Class {class_name}",
                        keywords=keywords,
                        content_preview=docstring[:500] if docstring else "",
                        metadata={
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": content[:match.start()].count('\n') + 1
                        }
                    )
                    
                    self.components[ref_id] = component
                    self._add_to_indexes(component)
                
                # Extract functions
                func_matches = re.finditer(r'^def\s+(\w+).*?:', content, re.MULTILINE)
                for match in func_matches:
                    func_name = match.group(1)
                    # Skip private methods unless they're important
                    if func_name.startswith('_') and not func_name.startswith('__'):
                        continue
                    
                    ref_id = f"@{func_name}"
                    
                    docstring = self._extract_docstring_after_match(content, match.end())
                    keywords = self._extract_keywords_from_text(func_name + " " + docstring)
                    
                    component = ComponentReference(
                        ref_id=ref_id,
                        component_type="function",
                        path=str(py_file.relative_to(self.project_root)),
                        name=func_name,
                        description=docstring[:200] if docstring else f"Function {func_name}",
                        keywords=keywords,
                        content_preview=docstring[:500] if docstring else "",
                        metadata={
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": content[:match.start()].count('\n') + 1
                        }
                    )
                    
                    self.components[ref_id] = component
                    self._add_to_indexes(component)
            
            except Exception as e:
                logger.debug(f"Failed to index {py_file}: {e}")
    
    def _index_sprs(self):
        """Index SPRs from Knowledge Graph."""
        spr_file = self.project_root / "knowledge_graph" / "spr_definitions_tv.json"
        if not spr_file.exists():
            return
        
        try:
            with open(spr_file, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)
            
            if isinstance(spr_data, list):
                for spr in spr_data:
                    spr_id = spr.get('spr_id', '')
                    if spr_id:
                        ref_id = f"@{spr_id}"
                        term = spr.get('term', spr_id)
                        definition = spr.get('definition', '')
                        
                        keywords = self._extract_keywords_from_text(term + " " + definition)
                        
                        component = ComponentReference(
                            ref_id=ref_id,
                            component_type="spr",
                            path=f"knowledge_graph/spr_definitions_tv.json",
                            name=term,
                            description=definition[:200] if definition else f"SPR: {term}",
                            keywords=keywords,
                            content_preview=definition[:500] if definition else "",
                            metadata={
                                "spr_id": spr_id,
                                "category": spr.get('category', ''),
                                "source": spr.get('source', '')
                            }
                        )
                        
                        self.components[ref_id] = component
                        self._add_to_indexes(component)
        
        except Exception as e:
            logger.debug(f"Failed to index SPRs: {e}")
    
    def _index_workflows(self):
        """Index workflow files."""
        workflow_dir = self.project_root / "workflows"
        if not workflow_dir.exists():
            return
        
        for workflow_file in workflow_dir.glob("*.json"):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                
                workflow_name = workflow_file.stem
                ref_id = f"@{workflow_name}"
                
                description = workflow_data.get('description', workflow_data.get('name', ''))
                keywords = self._extract_keywords_from_text(workflow_name + " " + description)
                
                component = ComponentReference(
                    ref_id=ref_id,
                    component_type="workflow",
                    path=str(workflow_file.relative_to(self.project_root)),
                    name=workflow_name,
                    description=description[:200] if description else f"Workflow: {workflow_name}",
                    keywords=keywords,
                    content_preview=json.dumps(workflow_data, indent=2)[:500],
                    metadata={
                        "workflow_name": workflow_name
                    }
                )
                
                self.components[ref_id] = component
                self._add_to_indexes(component)
            
            except Exception as e:
                logger.debug(f"Failed to index workflow {workflow_file}: {e}")
    
    def _index_protocols(self):
        """Index protocol documents."""
        protocol_patterns = ['PRIME_ARCHE_PROTOCOL', 'ResonantiA_Protocol', 'protocol']
        
        for md_file in self.project_root.rglob("*.md"):
            filename_lower = md_file.name.lower()
            if any(pattern.lower() in filename_lower for pattern in protocol_patterns):
                ref_id = f"@{md_file.name}"
                
                # Check if already indexed as file
                if ref_id not in self.components:
                    keywords = self._extract_keywords_from_filename(md_file.name)
                    preview = self._get_file_preview(md_file)
                    
                    component = ComponentReference(
                        ref_id=ref_id,
                        component_type="protocol",
                        path=str(md_file.relative_to(self.project_root)),
                        name=md_file.name,
                        description=f"Protocol document: {md_file.name}",
                        keywords=keywords + ["protocol", "arche", "specification"],
                        content_preview=preview,
                        metadata={
                            "is_protocol": True
                        }
                    )
                    
                    self.components[ref_id] = component
                    self._add_to_indexes(component)
    
    def _extract_keywords_from_filename(self, filename: str) -> List[str]:
        """Extract keywords from filename (deterministic)."""
        # Remove extension
        name = Path(filename).stem
        
        # Split by common separators
        parts = re.split(r'[_\-\s.]+', name)
        
        # Filter and normalize
        keywords = []
        for part in parts:
            part_lower = part.lower()
            if len(part_lower) > 2 and part_lower not in ['the', 'and', 'for', 'with']:
                keywords.append(part_lower)
        
        return keywords
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text (deterministic)."""
        # Simple keyword extraction - find capitalized words and important terms
        keywords = []
        
        # Find capitalized words (likely concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        keywords.extend([w.lower() for w in capitalized if len(w) > 3])
        
        # Find technical terms
        technical = re.findall(r'\b[a-z]+(?:ing|tion|ism|ology|ics|ance|ence)\b', text, re.IGNORECASE)
        keywords.extend([w.lower() for w in technical if len(w) > 4])
        
        # Remove duplicates
        return list(set(keywords))[:20]
    
    def _extract_docstring_after_match(self, content: str, start_pos: int) -> str:
        """Extract docstring after a match position."""
        # Look for triple-quoted strings
        remaining = content[start_pos:]
        docstring_match = re.search(r'"""(.*?)"""', remaining, re.DOTALL)
        if docstring_match:
            return docstring_match.group(1).strip()
        return ""
    
    def _get_file_preview(self, file_path: Path) -> str:
        """Get preview of file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars
                return content[:500]  # Return first 500 for preview
        except:
            return ""
    
    def _add_to_indexes(self, component: ComponentReference):
        """Add component to all indexes."""
        # Index by keywords
        for keyword in component.keywords:
            self.index_by_keyword[keyword].add(component.ref_id)
        
        # Index by type
        self.index_by_type[component.component_type].add(component.ref_id)
    
    def search(self, query: str, limit: int = 10) -> List[ComponentReference]:
        """
        Search for components matching query (deterministic pattern matching).
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching ComponentReference objects, sorted by relevance
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_components = []
        
        for ref_id, component in self.components.items():
            score = 0.0
            
            # Exact ref_id match (highest priority)
            if query_lower in ref_id.lower():
                score += 10.0
            
            # Name match
            if query_lower in component.name.lower():
                score += 5.0
            
            # Keyword matches
            component_keywords = set(kw.lower() for kw in component.keywords)
            keyword_overlap = query_words & component_keywords
            score += len(keyword_overlap) * 2.0
            
            # Description match
            if query_lower in component.description.lower():
                score += 1.0
            
            # Content preview match
            if query_lower in component.content_preview.lower():
                score += 0.5
            
            if score > 0:
                scored_components.append((score, component))
        
        # Sort by score (descending)
        scored_components.sort(key=lambda x: x[0], reverse=True)
        
        return [comp for _, comp in scored_components[:limit]]
    
    def get_reference(self, ref_id: str) -> Optional[ComponentReference]:
        """Get component by exact reference ID."""
        return self.components.get(ref_id)
    
    def resolve_reference(self, ref_string: str) -> Optional[ComponentReference]:
        """
        Resolve a reference string (e.g., "@PRIME_ARCHE_PROTOCOL.md" or "@SPRManager").
        
        Args:
            ref_string: Reference string with or without @ prefix
            
        Returns:
            ComponentReference if found, None otherwise
        """
        # Normalize reference
        if not ref_string.startswith('@'):
            ref_string = '@' + ref_string
        
        # Try exact match first
        component = self.components.get(ref_string)
        if component:
            self.usage_patterns[ref_string] += 1
            return component
        
        # Try fuzzy match (find closest)
        query = ref_string.lstrip('@')
        results = self.search(query, limit=1)
        if results:
            self.usage_patterns[results[0].ref_id] += 1
            return results[0]
        
        return None
    
    def get_content(self, ref_id: str) -> Optional[str]:
        """Get full content of a referenced component."""
        component = self.get_reference(ref_id)
        if not component:
            return None
        
        file_path = self.project_root / component.path
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read {file_path}: {e}")
                return None
        
        return None
    
    def list_by_type(self, component_type: str) -> List[ComponentReference]:
        """List all components of a specific type."""
        ref_ids = self.index_by_type.get(component_type, set())
        return [self.components[ref_id] for ref_id in ref_ids if ref_id in self.components]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the self-reference system."""
        return {
            "total_components": len(self.components),
            "by_type": {t: len(refs) for t, refs in self.index_by_type.items()},
            "total_keywords": len(self.index_by_keyword),
            "most_used": sorted(self.usage_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        }

