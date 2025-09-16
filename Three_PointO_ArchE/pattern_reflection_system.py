import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

@dataclass
class Pattern:
    level: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    reflection_strength: float

class PatternReflectionSystem:
    def __init__(self, knowledge_tapestry_path: str):
        self.knowledge_tapestry_path = knowledge_tapestry_path
        self.levels = ["cosmic", "systemic", "local", "micro"]
        self.patterns: Dict = {level: [] for level in self.levels}
        self.logger = logging.getLogger(__name__)

    def initialize_hierarchy(self, bidirectional: bool = True) -> Dict:
        """Initialize the hierarchical system with bidirectional pattern reflection capability."""
        try:
            with open(self.knowledge_tapestry_path, 'r') as f:
                self.knowledge_tapestry = json.load(f)
            
            return {
                "status": "success",
                "message": "Hierarchical system initialized",
                "bidirectional": bidirectional,
                "levels": self.levels
            }
        except Exception as e:
            self.logger.error(f"Failed to initialize hierarchy: {str(e)}")
            return {"status": "error", "message": str(e)}

    def extract_patterns(self, level: str, source: str) -> Dict[str, Any]:
        """Extract patterns from a specific level of abstraction."""
        try:
            if level not in self.levels:
                raise ValueError(f"Invalid level: {level}")

            patterns = []
            for pattern_data in self.knowledge_tapestry.get(level, []):
                pattern = Pattern(
                    level=level,
                    content=pattern_data.get("content", {}),
                    metadata=pattern_data.get("metadata", {}),
                    reflection_strength=pattern_data.get("reflection_strength", 0.0)
                )
                patterns.append(pattern)
            
            self.patterns[level] = patterns
            return {
                "status": "success",
                "patterns": patterns,
                "level": level
            }
        except Exception as e:
            self.logger.error(f"Failed to extract patterns: {str(e)}")
            return {"status": "error", "message": str(e)}

    def reflect_patterns(self, direction: str, patterns: List[Dict], levels: List[str]) -> Dict[str, Any]:
        """Reflect patterns through the hierarchy in the specified direction."""
        try:
            if direction not in ["upward", "downward"]:
                raise ValueError(f"Invalid direction: {direction}")

            reflected_patterns = []
            for pattern in patterns:
                for target_level in levels:
                    reflection = self._reflect_single_pattern(pattern, target_level, direction)
                    if reflection:
                        reflected_patterns.append(reflection)

            return {
                "status": "success",
                "patterns": reflected_patterns,
                "direction": direction,
                "levels": levels
            }
        except Exception as e:
            self.logger.error(f"Failed to reflect patterns: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _reflect_single_pattern(self, pattern: Dict, target_level: str, direction: str) -> Optional[Dict]:
        """Reflect a single pattern to a target level."""
        try:
            source_level = pattern["level"]
            source_idx = self.levels.index(source_level)
            target_idx = self.levels.index(target_level)

            if direction == "downward" and target_idx <= source_idx:
                return None
            if direction == "upward" and target_idx >= source_idx:
                return None

            reflection_strength = self._calculate_reflection_strength(
                pattern["reflection_strength"],
                abs(target_idx - source_idx)
            )

            return {
                "level": target_level,
                "content": self._transform_content(pattern["content"], target_level),
                "metadata": pattern["metadata"],
                "reflection_strength": reflection_strength
            }
        except Exception as e:
            self.logger.error(f"Failed to reflect single pattern: {str(e)}")
            return None

    def _calculate_reflection_strength(self, base_strength: float, level_distance: int) -> float:
        """Calculate the reflection strength based on level distance."""
        decay_factor = 0.1
        return base_strength * (1 - (decay_factor * level_distance))

    def _transform_content(self, content: Dict, target_level: str) -> Dict:
        """Transform pattern content to fit the target level."""
        transformations = {
            "cosmic": lambda x: self._transform_to_cosmic(x),
            "systemic": lambda x: self._transform_to_systemic(x),
            "local": lambda x: self._transform_to_local(x),
            "micro": lambda x: self._transform_to_micro(x)
        }
        return transformations[target_level](content)

    def _transform_to_cosmic(self, content: Dict) -> Dict:
        """Transform content to cosmic level abstraction."""
        return {
            "universal_principles": content.get("principles", []),
            "cosmic_patterns": content.get("patterns", []),
            "fundamental_laws": content.get("laws", [])
        }

    def _transform_to_systemic(self, content: Dict) -> Dict:
        """Transform content to systemic level abstraction."""
        return {
            "system_principles": content.get("universal_principles", []),
            "system_patterns": content.get("cosmic_patterns", []),
            "system_laws": content.get("fundamental_laws", [])
        }

    def _transform_to_local(self, content: Dict) -> Dict:
        """Transform content to local level abstraction."""
        return {
            "local_principles": content.get("system_principles", []),
            "local_patterns": content.get("system_patterns", []),
            "local_laws": content.get("system_laws", [])
        }

    def _transform_to_micro(self, content: Dict) -> Dict:
        """Transform content to micro level abstraction."""
        return {
            "micro_principles": content.get("local_principles", []),
            "micro_patterns": content.get("local_patterns", []),
            "micro_laws": content.get("local_laws", [])
        }

    def synthesize_patterns(self, upward_patterns: List[Dict], downward_patterns: List[Dict]) -> Dict[str, Any]:
        """Synthesize patterns from both directions into a unified model."""
        try:
            synthesized = {}
            for level in self.levels:
                level_patterns = []
                
                # Combine patterns from both directions
                up_patterns = [p for p in upward_patterns if p["level"] == level]
                down_patterns = [p for p in downward_patterns if p["level"] == level]
                
                # Merge patterns with same content
                merged_patterns = self._merge_patterns(up_patterns, down_patterns)
                synthesized[level] = merged_patterns

            return {
                "status": "success",
                "patterns": synthesized
            }
        except Exception as e:
            self.logger.error(f"Failed to synthesize patterns: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _merge_patterns(self, up_patterns: List, down_patterns: List) -> List:
        """Merge patterns from both directions, combining their strengths."""
        merged = {}
        
        for pattern in up_patterns + down_patterns:
            key = str(pattern["content"])
            if key in merged:
                merged[key]["reflection_strength"] = max(
                    merged[key]["reflection_strength"],
                    pattern["reflection_strength"]
                )
            else:
                merged[key] = pattern.copy()
        
        return list(merged.values())

    def validate_coherence(self, synthesized_patterns: Dict, threshold: float) -> Dict[str, Any]:
        """Validate the coherence of patterns across all levels."""
        try:
            coherence_scores = {}
            for level in self.levels:
                patterns = synthesized_patterns.get(level, [])
                if not patterns:
                    continue
                
                # Calculate coherence score for this level
                coherence = self._calculate_level_coherence(patterns)
                coherence_scores[level] = coherence

            # Check if all levels meet the threshold
            is_valid = all(score >= threshold for score in coherence_scores.values())
            
            return {
                "status": "success",
                "is_valid": is_valid,
                "patterns": coherence_scores,
                "threshold": threshold
            }
        except Exception as e:
            self.logger.error(f"Failed to validate coherence: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _calculate_level_coherence(self, patterns: List) -> float:
        """Calculate the coherence score for a level's patterns."""
        if not patterns:
            return 0.0
        
        # Calculate average reflection strength
        if isinstance(patterns[0], Pattern):
            avg_strength = sum(p.reflection_strength for p in patterns) / len(patterns)
        else:
            avg_strength = sum(p["reflection_strength"] for p in patterns) / len(patterns)
        
        # Calculate pattern similarity
        similarity_scores = []
        for i, p1 in enumerate(patterns):
            for p2 in patterns[i+1:]:
                similarity = self._calculate_pattern_similarity(p1, p2)
                similarity_scores.append(similarity)
        
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        
        # Combine scores
        return (avg_strength + avg_similarity) / 2

    def _calculate_pattern_similarity(self, p1: Any, p2: Any) -> float:
        """Calculate similarity between two patterns."""
        # Simple content-based similarity
        if isinstance(p1, Pattern):
            content1 = set(str(p1.content).split())
            content2 = set(str(p2.content).split())
        else:
            content1 = set(str(p1["content"]).split())
            content2 = set(str(p2["content"]).split())
        
        intersection = len(content1.intersection(content2))
        union = len(content1.union(content2))
        
        return intersection / union if union > 0 else 0.0

    def integrate_patterns(self, validated_patterns: Dict, target_system: str) -> Dict[str, Any]:
        """Integrate validated patterns into the system architecture."""
        try:
            integration_results = {}
            for level, patterns in validated_patterns.items():
                # Create level-specific integration
                integration = self._create_level_integration(level, patterns, target_system)
                integration_results[level] = integration

            return {
                "status": "success",
                "patterns": integration_results,
                "target_system": target_system
            }
        except Exception as e:
            self.logger.error(f"Failed to integrate patterns: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _create_level_integration(self, level: str, patterns: List, target_system: str) -> Dict:
        """Create integration for a specific level's patterns."""
        return {
            "level": level,
            "integration_points": [
                {
                    "pattern": pattern,
                    "target_component": self._determine_target_component(pattern, target_system),
                    "integration_method": self._determine_integration_method(pattern, level)
                }
                for pattern in patterns
            ]
        }

    def _determine_target_component(self, pattern: Dict, target_system: str) -> str:
        """Determine the target component for pattern integration."""
        # This would be expanded based on the actual system architecture
        return f"{target_system}/components/{pattern['level']}_integration"

    def _determine_integration_method(self, pattern: Dict, level: str) -> str:
        """Determine the appropriate integration method for a pattern."""
        methods = {
            "cosmic": "universal_integration",
            "systemic": "system_integration",
            "local": "local_integration",
            "micro": "micro_integration"
        }
        return methods.get(level, "default_integration")

    def generate_report(self, integration_results: Dict[str, Any], format: str = "markdown") -> Dict[str, Any]:
        """Generate a comprehensive report of the pattern reflection process."""
        try:
            report = {
                "title": "Pattern Reflection System Report",
                "sections": [
                    {
                        "title": "Pattern Reflection Overview",
                        "content": self._generate_overview_section()
                    },
                    {
                        "title": "Pattern Distribution",
                        "content": self._generate_distribution_section()
                    },
                    {
                        "title": "Integration Results",
                        "content": self._generate_integration_section(integration_results)
                    },
                    {
                        "title": "Coherence Analysis",
                        "content": self._generate_coherence_section()
                    }
                ]
            }

            if format == "markdown":
                report_content = self._format_markdown_report(report)
            else:
                report_content = report

            return {
                "status": "success",
                "patterns": report_content,
                "format": format
            }
        except Exception as e:
            self.logger.error(f"Failed to generate report: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _generate_overview_section(self) -> str:
        """Generate the overview section of the report."""
        return f"""
        # Pattern Reflection System Overview
        
        The system implements the hermetic principle of 'as above so below' through bidirectional pattern reflection
        across {len(self.levels)} levels of abstraction:
        
        {', '.join(self.levels)}
        
        Total patterns processed: {sum(len(patterns) for patterns in self.patterns.values())}
        """

    def _generate_distribution_section(self) -> str:
        """Generate the pattern distribution section of the report."""
        distribution = "\n## Pattern Distribution by Level\n\n"
        for level in self.levels:
            count = len(self.patterns[level])
            distribution += f"- {level}: {count} patterns\n"
        return distribution

    def _generate_integration_section(self, integration_results: Dict[str, Any]) -> str:
        """Generate the integration results section of the report."""
        integration = "\n## Integration Results\n\n"
        for level, results in integration_results.get("patterns", {}).items():
            integration += f"### {level.title()} Level Integration\n"
            for point in results.get("integration_points", []):
                integration += f"- Pattern integrated into {point['target_component']}\n"
                integration += f"  Method: {point['integration_method']}\n"
        return integration

    def _generate_coherence_section(self) -> str:
        """Generate the coherence analysis section of the report."""
        coherence = "\n## Coherence Analysis\n\n"
        for level in self.levels:
            patterns = self.patterns[level]
            if patterns:
                score = self._calculate_level_coherence(patterns)
                coherence += f"- {level}: {score:.2f} coherence score\n"
        return coherence

    def _format_markdown_report(self, report: Dict) -> str:
        """Format the report in markdown."""
        markdown = f"# {report['title']}\n\n"
        for section in report["sections"]:
            markdown += f"## {section['title']}\n\n"
            markdown += section["content"]
            markdown += "\n\n"
        return markdown 