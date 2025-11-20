#!/usr/bin/env python3
"""
VCD Guide Accessor - Access How-To Guides from VCD System
Provides programmatic access to VCD component documentation

Part of ResonantiA Protocol v3.5-GP Implementation Resonance initiative.
Created: 2025-11-19
Last Updated: 2025-11-19 06:27:10 EST
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer

logger = logging.getLogger(__name__)

@dataclass
class GuideMetadata:
    """Metadata for a VCD guide."""
    guide_id: str
    title: str
    component: str
    file_path: str
    version: str
    created: str
    last_updated: str
    description: str
    sections: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

class VCDGuideAccessor:
    """
    VCD Guide Accessor - Provides access to VCD component documentation.
    
    Provides:
    - Guide retrieval by ID or component name
    - Guide search functionality
    - Guide listing and metadata
    - Integration with VCD system
    """
    
    def __init__(self, guides_dir: Optional[Path] = None):
        """
        Initialize VCD Guide Accessor.
        
        Args:
            guides_dir: Directory containing guide files (default: docs/vcd_guides/)
        """
        if guides_dir is None:
            # Try to find guides directory relative to project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            
            # Try multiple possible locations
            possible_paths = [
                project_root / "docs" / "vcd_guides",
                Path.cwd() / "docs" / "vcd_guides",
                Path("docs/vcd_guides"),
                Path("../docs/vcd_guides")
            ]
            
            guides_dir = None
            for path in possible_paths:
                if path.exists():
                    guides_dir = path
                    break
            
            if guides_dir is None:
                # Default to project root
                guides_dir = project_root / "docs" / "vcd_guides"
        
        self.guides_dir = Path(guides_dir).resolve()
        
        # Load guide index
        self.guide_index = self._load_guide_index()
        
        logger.info(f"VCDGuideAccessor initialized with {len(self.guide_index)} guides")
    
    def _load_guide_index(self) -> Dict[str, GuideMetadata]:
        """Load guide index from directory."""
        index = {}
        
        if not self.guides_dir.exists():
            logger.warning(f"Guides directory not found: {self.guides_dir}")
            return index
        
        # Map of component names to guide files
        guide_files = {
            "vcd_bridge": "01_VCD_Bridge_Guide.md",
            "vcd_analysis_agent": "02_VCD_Analysis_Agent_Guide.md",
            "vcd_health_dashboard": "03_VCD_Health_Dashboard_Guide.md",
            "vcd_backup_recovery": "04_VCD_Backup_Recovery_Guide.md",
            "vcd_configuration_management": "05_VCD_Configuration_Management_Guide.md",
            "vcd_testing_suite": "06_VCD_Testing_Suite_Guide.md",
            "vcd_ui": "07_VCD_UI_Component_Guide.md",
            "free_model_options": "08_Free_Model_Options_Guide.md"
        }
        
        for component, filename in guide_files.items():
            guide_path = self.guides_dir / filename
            if guide_path.exists():
                try:
                    metadata = self._extract_metadata(guide_path, component)
                    index[component] = metadata
                    index[metadata.guide_id] = metadata
                    logger.debug(f"Loaded guide: {component} from {guide_path}")
                except Exception as e:
                    logger.warning(f"Failed to load guide {component}: {e}")
            else:
                logger.debug(f"Guide file not found: {guide_path}")
        
        logger.info(f"Loaded {len([k for k in index.keys() if k in guide_files])} guides")
        return index
    
    def _extract_metadata(self, guide_path: Path, component: str) -> GuideMetadata:
        """Extract metadata from guide file."""
        guide_id = component
        title = component.replace("_", " ").title() + " - Complete How-To Guide"
        version = "1.0"
        created = "2025-11-19"
        last_updated = "2025-11-19 06:38:29 EST"
        description = f"Complete how-to guide for {component}"
        sections = []
        keywords = [component, "vcd", "guide", "how-to"]
        
        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract title from first line
                if content.startswith('#'):
                    first_line = content.split('\n')[0]
                    title = first_line.replace('#', '').strip()
                
                # Extract metadata from headers
                lines = content.split('\n')
                for i, line in enumerate(lines[:50]):  # Check first 50 lines
                    line_stripped = line.strip()
                    if '**Version**:' in line_stripped:
                        version = line_stripped.split('**Version**:')[1].strip()
                    elif '**Created**:' in line_stripped:
                        created = line_stripped.split('**Created**:')[1].strip()
                    elif '**Last Updated**:' in line_stripped:
                        last_updated = line_stripped.split('**Last Updated**:')[1].strip()
                    elif '**Component**:' in line_stripped:
                        component_name = line_stripped.split('**Component**:')[1].strip()
                        if component_name:
                            component = component_name
                    elif line_stripped.startswith('##') and not line_stripped.startswith('###'):
                        section = line_stripped.replace('##', '').strip()
                        if section and section not in sections:
                            sections.append(section)
                    elif '**File**:' in line_stripped:
                        file_ref = line_stripped.split('**File**:')[1].strip()
                        if file_ref:
                            keywords.append(file_ref)
        
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {guide_path}: {e}")
        
        return GuideMetadata(
            guide_id=guide_id,
            title=title,
            component=component,
            file_path=str(guide_path),
            version=version,
            created=created,
            last_updated=last_updated,
            description=description,
            sections=sections[:10],  # Limit sections
            keywords=keywords
        )
    
    def get_guide(self, guide_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a guide by ID or component name.
        
        Args:
            guide_id: Guide ID or component name
            
        Returns:
            Dictionary with guide content and metadata, or None if not found
        """
        if guide_id not in self.guide_index:
            logger.warning(f"Guide not found: {guide_id}")
            return None
        
        metadata = self.guide_index[guide_id]
        guide_path = Path(metadata.file_path)
        
        if not guide_path.exists():
            logger.error(f"Guide file not found: {guide_path}")
            return None
        
        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "metadata": asdict(metadata),
                "content": content,
                "guide_id": metadata.guide_id,
                "component": metadata.component
            }
        except Exception as e:
            logger.error(f"Failed to read guide {guide_id}: {e}")
            return None
    
    def list_guides(self) -> List[Dict[str, Any]]:
        """
        List all available guides.
        
        Returns:
            List of guide metadata dictionaries
        """
        # Return unique guides (by component name, not guide_id duplicates)
        seen_components = set()
        guides = []
        for metadata in self.guide_index.values():
            if metadata.component not in seen_components:
                seen_components.add(metadata.component)
                guides.append(asdict(metadata))
        return guides
    
    def search_guides(self, query: str) -> List[Dict[str, Any]]:
        """
        Search guides by keyword.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching guide metadata dictionaries
        """
        query_lower = query.lower()
        results = []
        seen_components = set()
        
        for metadata in self.guide_index.values():
            # Skip duplicate entries (guide_id vs component)
            if metadata.component in seen_components:
                continue
            seen_components.add(metadata.component)
            
            # Search in title, description, keywords, sections, component name
            searchable_text = (
                metadata.title.lower() + " " +
                metadata.description.lower() + " " +
                metadata.component.lower() + " " +
                " ".join(kw.lower() for kw in metadata.keywords) + " " +
                " ".join(section.lower() for section in metadata.sections)
            )
            
            if query_lower in searchable_text:
                results.append(asdict(metadata))
        
        return results
    
    def get_guide_summary(self, guide_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a guide (metadata without full content).
        
        Args:
            guide_id: Guide ID or component name
            
        Returns:
            Dictionary with guide metadata, or None if not found
        """
        if guide_id not in self.guide_index:
            return None
        
        metadata = self.guide_index[guide_id]
        return asdict(metadata)
    
    def get_guide_section(self, guide_id: str, section_name: str) -> Optional[str]:
        """
        Get a specific section from a guide.
        
        Args:
            guide_id: Guide ID or component name
            section_name: Name of section to extract
            
        Returns:
            Section content as string, or None if not found
        """
        guide = self.get_guide(guide_id)
        if not guide:
            return None
        
        content = guide["content"]
        lines = content.split('\n')
        
        # Find section
        in_section = False
        section_lines = []
        
        for line in lines:
            if line.startswith('##') and section_name.lower() in line.lower():
                in_section = True
                section_lines.append(line)
            elif in_section:
                if line.startswith('##'):
                    # Next section, stop
                    break
                section_lines.append(line)
        
        if section_lines:
            return '\n'.join(section_lines)
        
        return None
    
    def get_guide_index(self) -> Dict[str, Any]:
        """
        Get the complete guide index.
        
        Returns:
            Dictionary with guide index information
        """
        return {
            "timestamp": now_iso(),
            "total_guides": len([m for m in self.guide_index.values() if m.guide_id == m.component]),
            "guides": [asdict(m) for m in self.guide_index.values() if m.guide_id == m.component]
        }


def main():
    """Demo the VCD Guide Accessor."""
    print("📚 Initializing VCD Guide Accessor...")
    print()
    
    accessor = VCDGuideAccessor()
    
    print(f"✓ Accessor initialized with {len(accessor.guide_index)} guides")
    print()
    
    # List all guides
    print("Available Guides:")
    guides = accessor.list_guides()
    for guide in guides:
        print(f"  - {guide['title']} ({guide['component']})")
    print()
    
    # Search guides
    print("Searching for 'backup':")
    results = accessor.search_guides("backup")
    for result in results:
        print(f"  - {result['title']}")
    print()
    
    # Get specific guide
    print("Getting VCD Bridge Guide:")
    guide = accessor.get_guide("vcd_bridge")
    if guide:
        print(f"  Title: {guide['metadata']['title']}")
        print(f"  Component: {guide['metadata']['component']}")
        print(f"  Sections: {len(guide['metadata']['sections'])}")
    print()
    
    print("✓ VCD Guide Accessor operational!")


if __name__ == "__main__":
    main()

