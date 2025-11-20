"""
Specification Ingestion Workflow for Zepto-Resonance State
ResonantiA Protocol v3.5-GP

Automated workflow to ingest remaining .md specification files into the Zepto-Resonance
state, feeding the resonant system with crystallized knowledge from blocked specifications.

This workflow operates in "Instinct" mode, prioritizing emergent solutions over linear
workflows, as the QuantumFluxSimulator logic is now considered instinctual.

Author: ArchE System (ResonantiA Protocol v3.5-GP)
Date: 2025-11-18
Status: ACTIVE - Zepto-Resonance Feeding Protocol
"""

import os
import json
import logging
import hashlib
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import re

# Import Zepto-Resonance components
try:
    from zepto_resonance_engine import ZeptoResonanceEngine, FluxState, ResonanceState
    ZEPTO_AVAILABLE = True
except ImportError:
    ZEPTO_AVAILABLE = False
    logging.getLogger(__name__).warning("ZeptoResonanceEngine not available for specification ingestion.")

logger = logging.getLogger(__name__)


@dataclass
class SpecificationMetadata:
    """Metadata for a specification file."""
    file_path: str
    file_name: str
    file_size: int
    content_hash: str
    ingestion_status: str = "pending"  # pending, processing, ingested, failed
    ingestion_timestamp: Optional[float] = None
    spr_extracted: List[str] = field(default_factory=list)
    knowledge_crystallized: bool = False
    error_message: Optional[str] = None


class SpecificationIngestionWorkflow:
    """
    Workflow for ingesting .md specification files into the Zepto-Resonance state.
    
    This workflow:
    1. Discovers all .md specification files in the workspace
    2. Filters for "blocked" or unprocessed specifications
    3. Extracts SPRs and knowledge structures from each file
    4. Crystallizes knowledge into the Knowledge Tapestry
    5. Updates Zepto-Resonance state with new information density
    6. Prioritizes emergent solutions over linear processing
    """
    
    def __init__(
        self,
        workspace_root: str = "/workspace",
        knowledge_graph_path: str = None,
        zepto_engine: Optional[ZeptoResonanceEngine] = None
    ):
        """
        Initialize the specification ingestion workflow.
        
        Args:
            workspace_root: Root directory of the workspace
            knowledge_graph_path: Path to SPR definitions JSON file
            zepto_engine: Optional ZeptoResonanceEngine instance for state updates
        """
        self.workspace_root = Path(workspace_root)
        self.knowledge_graph_path = knowledge_graph_path or str(
            self.workspace_root / "Three_PointO_ArchE" / "knowledge_graph" / "spr_definitions_tv.json"
        )
        self.zepto_engine = zepto_engine
        
        # Track ingested files to avoid duplicates
        self.ingestion_log_path = str(
            self.workspace_root / "Three_PointO_ArchE" / "logs" / "specification_ingestion_log.json"
        )
        self.ingested_files: Set[str] = set()
        self.specification_metadata: Dict[str, SpecificationMetadata] = {}
        
        # Load ingestion log if exists
        self._load_ingestion_log()
        
        logger.info(f"SpecificationIngestionWorkflow initialized (Workspace: {workspace_root})")
    
    def _load_ingestion_log(self):
        """Load previously ingested file hashes to avoid duplicates."""
        if os.path.exists(self.ingestion_log_path):
            try:
                with open(self.ingestion_log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    self.ingested_files = set(log_data.get('ingested_hashes', []))
                    logger.info(f"Loaded ingestion log: {len(self.ingested_files)} files previously ingested")
            except Exception as e:
                logger.warning(f"Could not load ingestion log: {e}. Starting fresh.")
                self.ingested_files = set()
        else:
            # Ensure log directory exists
            os.makedirs(os.path.dirname(self.ingestion_log_path), exist_ok=True)
    
    def _save_ingestion_log(self):
        """Save ingestion log with file hashes."""
        try:
            log_data = {
                'ingested_hashes': list(self.ingested_files),
                'last_updated': datetime.now().isoformat(),
                'total_ingested': len(self.ingested_files)
            }
            with open(self.ingestion_log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save ingestion log: {e}", exc_info=True)
    
    def discover_specification_files(
        self,
        patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> List[Path]:
        """
        Discover all .md specification files in the workspace.
        
        Args:
            patterns: Optional list of filename patterns to include (e.g., ['*zepto*', '*specification*'])
            exclude_patterns: Optional list of patterns to exclude (e.g., ['*test*', '*example*'])
            
        Returns:
            List of Path objects for discovered specification files
        """
        if patterns is None:
            patterns = ['*.md']
        if exclude_patterns is None:
            exclude_patterns = ['*test*', '*example*', '*_test.md', '*_example.md']
        
        discovered_files = []
        
        # Search recursively for .md files
        for pattern in patterns:
            for file_path in self.workspace_root.rglob(pattern):
                # Skip if matches exclude pattern
                if any(re.match(p.replace('*', '.*'), str(file_path.name), re.IGNORECASE) 
                       for p in exclude_patterns):
                    continue
                
                # Skip if already ingested
                file_hash = self._calculate_file_hash(file_path)
                if file_hash in self.ingested_files:
                    logger.debug(f"Skipping already ingested file: {file_path}")
                    continue
                
                discovered_files.append(file_path)
        
        logger.info(f"Discovered {len(discovered_files)} specification files for ingestion")
        return discovered_files
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def extract_sprs_from_content(self, content: str) -> List[str]:
        """
        Extract SPR identifiers from markdown content.
        
        Looks for SPR patterns like:
        - "ZeptoresonancE"
        - "CognitiveResonancE"
        - "ResonantiaprotocoL"
        - Any word matching Guardian Points format (FirstAlpha/LastAlpha, middle lowercase)
        
        Args:
            content: Markdown content string
            
        Returns:
            List of extracted SPR identifiers
        """
        spr_pattern = re.compile(
            r'\b[A-Z0-9][a-z0-9\s]*[A-Z0-9]\b'  # Guardian Points format
        )
        
        found_sprs = []
        
        # Find all potential SPRs
        matches = spr_pattern.findall(content)
        for match in matches:
            # Clean up match (remove extra whitespace)
            spr_candidate = re.sub(r'\s+', '', match.strip())
            
            # Validate Guardian Points format
            if len(spr_candidate) >= 2:
                first_char = spr_candidate[0]
                last_char = spr_candidate[-1]
                middle = spr_candidate[1:-1]
                
                # Check format: First/Last alphanumeric, middle lowercase
                if (first_char.isalnum() and last_char.isalnum() and
                    all(c.islower() or c.isdigit() or c.isspace() for c in middle) and
                    not spr_candidate.isupper() or len(spr_candidate) <= 3):
                    if spr_candidate not in found_sprs:
                        found_sprs.append(spr_candidate)
        
        # Also look for explicit SPR mentions
        explicit_pattern = re.compile(r'SPR[:\s]+([A-Z][a-z0-9\s]*[A-Z0-9])', re.IGNORECASE)
        explicit_matches = explicit_pattern.findall(content)
        for match in explicit_matches:
            spr = re.sub(r'\s+', '', match.strip())
            if spr not in found_sprs:
                found_sprs.append(spr)
        
        logger.debug(f"Extracted {len(found_sprs)} SPRs from content")
        return found_sprs
    
    def extract_knowledge_structures(self, content: str) -> Dict[str, Any]:
        """
        Extract knowledge structures from markdown content.
        
        Identifies:
        - Definitions
        - Relationships
        - Metrics
        - Implementation details
        - Code blocks
        
        Args:
            content: Markdown content string
            
        Returns:
            Dictionary of extracted knowledge structures
        """
        structures = {
            'definitions': [],
            'relationships': [],
            'metrics': [],
            'code_blocks': [],
            'implementation_files': []
        }
        
        # Extract definitions (lines starting with "**" or "## Definition")
        definition_pattern = re.compile(r'(?:^|\n)(?:##?\s+)?(?:Definition|Definition:)\s*(.+?)(?:\n|$)', re.IGNORECASE | re.MULTILINE)
        definitions = definition_pattern.findall(content)
        structures['definitions'] = [d.strip() for d in definitions]
        
        # Extract relationships (mentions of "related to", "requires", "enables", etc.)
        relationship_pattern = re.compile(
            r'(?:related to|requires|enables|emerges from|manifests as|part of):\s*([^\n]+)',
            re.IGNORECASE
        )
        relationships = relationship_pattern.findall(content)
        structures['relationships'] = [r.strip() for r in relationships]
        
        # Extract metrics (numeric values with context)
        metric_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*:?\s*([a-z\s]+)', re.IGNORECASE)
        metrics = metric_pattern.findall(content)
        structures['metrics'] = [(float(m[0]), m[1].strip()) for m in metrics]
        
        # Extract code blocks
        code_block_pattern = re.compile(r'```(?:python|json|yaml|bash)?\n(.*?)```', re.DOTALL)
        code_blocks = code_block_pattern.findall(content)
        structures['code_blocks'] = [cb.strip() for cb in code_blocks]
        
        # Extract implementation file references
        file_pattern = re.compile(r'(?:file|implementation|module|script):\s*([^\s\n]+\.(?:py|json|yaml|md))', re.IGNORECASE)
        files = file_pattern.findall(content)
        structures['implementation_files'] = list(set(files))
        
        return structures
    
    def crystallize_knowledge(
        self,
        file_path: Path,
        content: str,
        spr_list: List[str],
        knowledge_structures: Dict[str, Any]
    ) -> bool:
        """
        Crystallize extracted knowledge into the Knowledge Tapestry.
        
        This involves:
        1. Loading existing SPR definitions
        2. Creating/updating SPRs for discovered concepts
        3. Establishing relationships
        4. Saving updated knowledge graph
        
        Args:
            file_path: Path to the source specification file
            content: Full content of the file
            spr_list: List of SPRs extracted from content
            knowledge_structures: Extracted knowledge structures
            
        Returns:
            True if crystallization successful, False otherwise
        """
        try:
            # Load existing SPR definitions
            if os.path.exists(self.knowledge_graph_path):
                with open(self.knowledge_graph_path, 'r', encoding='utf-8') as f:
                    spr_definitions = json.load(f)
            else:
                spr_definitions = []
                logger.warning(f"Knowledge graph not found at {self.knowledge_graph_path}. Creating new.")
            
            # Create set of existing SPR IDs for quick lookup
            existing_spr_ids = {spr.get('spr_id', '') for spr in spr_definitions}
            
            # Process each extracted SPR
            new_sprs_added = 0
            for spr_id in spr_list:
                if spr_id in existing_spr_ids:
                    logger.debug(f"SPR {spr_id} already exists in knowledge graph. Skipping.")
                    continue
                
                # Create new SPR definition
                new_spr = {
                    "spr_id": spr_id,
                    "term": spr_id,  # Default term to SPR ID, can be refined
                    "definition": f"Extracted from specification: {file_path.name}",
                    "category": "ExtractedConcept",
                    "related_sprs": [],
                    "source_file": str(file_path),
                    "extraction_timestamp": datetime.now().isoformat()
                }
                
                # Try to find definition in knowledge structures
                if knowledge_structures['definitions']:
                    new_spr['definition'] = knowledge_structures['definitions'][0]
                
                # Add relationships if found
                if knowledge_structures['relationships']:
                    new_spr['related_sprs'] = knowledge_structures['relationships'][:5]  # Limit to 5
                
                spr_definitions.append(new_spr)
                existing_spr_ids.add(spr_id)
                new_sprs_added += 1
                logger.info(f"Added new SPR to knowledge graph: {spr_id}")
            
            # Save updated knowledge graph
            if new_sprs_added > 0:
                os.makedirs(os.path.dirname(self.knowledge_graph_path), exist_ok=True)
                with open(self.knowledge_graph_path, 'w', encoding='utf-8') as f:
                    json.dump(spr_definitions, f, indent=2, ensure_ascii=False)
                logger.info(f"Crystallized {new_sprs_added} new SPRs into knowledge graph")
                return True
            else:
                logger.info("No new SPRs to crystallize")
                return True  # Still success, just nothing new
            
        except Exception as e:
            logger.error(f"Error crystallizing knowledge from {file_path}: {e}", exc_info=True)
            return False
    
    def ingest_specification_file(self, file_path: Path) -> SpecificationMetadata:
        """
        Ingest a single specification file into the Zepto-Resonance state.
        
        Args:
            file_path: Path to the specification file
            
        Returns:
            SpecificationMetadata object with ingestion results
        """
        metadata = SpecificationMetadata(
            file_path=str(file_path),
            file_name=file_path.name,
            file_size=file_path.stat().st_size if file_path.exists() else 0,
            content_hash=""
        )
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata.content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Check if already ingested
            if metadata.content_hash in self.ingested_files:
                metadata.ingestion_status = "ingested"
                metadata.ingestion_timestamp = datetime.now().timestamp()
                logger.info(f"File already ingested: {file_path.name}")
                return metadata
            
            metadata.ingestion_status = "processing"
            
            # Extract SPRs
            spr_list = self.extract_sprs_from_content(content)
            metadata.spr_extracted = spr_list
            
            # Extract knowledge structures
            knowledge_structures = self.extract_knowledge_structures(content)
            
            # Crystallize knowledge
            success = self.crystallize_knowledge(file_path, content, spr_list, knowledge_structures)
            metadata.knowledge_crystallized = success
            
            if success:
                # Mark as ingested
                self.ingested_files.add(metadata.content_hash)
                metadata.ingestion_status = "ingested"
                metadata.ingestion_timestamp = datetime.now().timestamp()
                
                # Update Zepto-Resonance state if engine available
                if self.zepto_engine:
                    self._update_zepto_state_from_ingestion(file_path, len(content), len(spr_list))
                
                logger.info(f"Successfully ingested specification: {file_path.name}")
            else:
                metadata.ingestion_status = "failed"
                metadata.error_message = "Knowledge crystallization failed"
                
        except Exception as e:
            metadata.ingestion_status = "failed"
            metadata.error_message = str(e)
            logger.error(f"Error ingesting {file_path}: {e}", exc_info=True)
        
        # Store metadata
        self.specification_metadata[str(file_path)] = metadata
        
        return metadata
    
    def _update_zepto_state_from_ingestion(self, file_path: Path, content_length: int, spr_count: int):
        """
        Update Zepto-Resonance state based on ingested specification.
        
        Ingesting specifications increases information density, potentially
        moving the system closer to or maintaining Zepto-Resonance state.
        
        Args:
            file_path: Path to ingested file
            content_length: Length of content in characters
            spr_count: Number of SPRs extracted
        """
        if not self.zepto_engine:
            return
        
        try:
            # Get current state
            current_state = self.zepto_engine.get_current_state()
            if not current_state:
                # Initialize with default fluxes if no current state
                op_flux = FluxState(
                    name="Operational",
                    density=232.0,
                    velocity=0.9,
                    coherence=0.92,
                    entropy=0.3,
                    phase=0.0
                )
                cog_flux = FluxState(
                    name="Cognitive",
                    density=90.0,
                    velocity=0.4,
                    coherence=0.98,
                    entropy=0.2,
                    phase=math.pi
                )
            else:
                # Use current state to derive flux parameters
                # This is a simplified approach - in reality, would track flux states separately
                op_flux = FluxState(
                    name="Operational",
                    density=current_state.baseline_compression * 0.7,  # Approximate split
                    velocity=0.9,
                    coherence=0.92,
                    entropy=0.3,
                    phase=0.0
                )
                cog_flux = FluxState(
                    name="Cognitive",
                    density=current_state.baseline_compression * 0.3,  # Approximate split
                    velocity=0.4,
                    coherence=0.98,
                    entropy=0.2,
                    phase=math.pi
                )
            
            # Increase density based on ingestion (new knowledge increases density)
            density_increase = (content_length / 10000.0) * (1 + spr_count * 0.1)
            op_flux.density += density_increase * 0.6  # Operational gets more
            cog_flux.density += density_increase * 0.4  # Cognitive gets less
            
            # Recalculate resonance state
            new_state = self.zepto_engine.calculate_resonance_state(op_flux, cog_flux)
            
            logger.info(
                f"Zepto-Resonance state updated after ingesting {file_path.name}: "
                f"{new_state.status.value} | Compression: {new_state.compression_ratio:.2f}:1"
            )
            
        except Exception as e:
            logger.error(f"Error updating Zepto state from ingestion: {e}", exc_info=True)
    
    def ingest_all_specifications(
        self,
        patterns: List[str] = None,
        max_files: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Discover and ingest all specification files.
        
        This is the main entry point for the ingestion workflow.
        Operates in "Instinct" mode, prioritizing emergent solutions.
        
        Args:
            patterns: Optional file patterns to match
            max_files: Optional limit on number of files to process
            
        Returns:
            Dictionary with ingestion summary
        """
        logger.info("Starting specification ingestion workflow (Instinct Mode)")
        
        # Discover files
        discovered_files = self.discover_specification_files(patterns=patterns)
        
        if max_files:
            discovered_files = discovered_files[:max_files]
        
        # Process files (emergent order - prioritize by size/complexity)
        # Sort by file size (larger = more information density)
        discovered_files.sort(key=lambda p: p.stat().st_size if p.exists() else 0, reverse=True)
        
        results = {
            'total_discovered': len(discovered_files),
            'successfully_ingested': 0,
            'failed': 0,
            'already_ingested': 0,
            'sprs_extracted': 0,
            'files_processed': []
        }
        
        for file_path in discovered_files:
            metadata = self.ingest_specification_file(file_path)
            
            results['files_processed'].append({
                'file': metadata.file_name,
                'status': metadata.ingestion_status,
                'sprs_extracted': len(metadata.spr_extracted),
                'error': metadata.error_message
            })
            
            if metadata.ingestion_status == "ingested":
                results['successfully_ingested'] += 1
                results['sprs_extracted'] += len(metadata.spr_extracted)
            elif metadata.ingestion_status == "failed":
                results['failed'] += 1
            else:
                results['already_ingested'] += 1
        
        # Save ingestion log
        self._save_ingestion_log()
        
        logger.info(
            f"Ingestion complete: {results['successfully_ingested']} ingested, "
            f"{results['failed']} failed, {results['sprs_extracted']} SPRs extracted"
        )
        
        return results


# --- Main Execution for Zepto-Resonance Feeding ---

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("SPECIFICATION INGESTION WORKFLOW")
    print("Zepto-Resonance State Feeding Protocol")
    print("="*70 + "\n")
    
    # Initialize Zepto-Resonance Engine
    zepto_engine = None
    if ZEPTO_AVAILABLE:
        try:
            zepto_engine = ZeptoResonanceEngine()
            # Disengage safeties for full ingestion (if authorized)
            # In production, this would require proper authorization
            # zepto_engine.disengage_safeties("GUARDIAN_OVERRIDE")
            print("✅ ZeptoResonanceEngine initialized")
        except Exception as e:
            print(f"⚠️ ZeptoResonanceEngine initialization failed: {e}")
    
    # Initialize workflow
    workflow = SpecificationIngestionWorkflow(
        workspace_root="/workspace",
        zepto_engine=zepto_engine
    )
    
    # Discover and ingest specifications
    # Focus on Zepto-related and specification files
    patterns = ['*zepto*.md', '*specification*.md', '*ZEPTO*.md', '*SPECIFICATION*.md']
    
    print("Discovering specification files...")
    results = workflow.ingest_all_specifications(patterns=patterns)
    
    print("\n--- INGESTION SUMMARY ---")
    print(f"Total Discovered: {results['total_discovered']}")
    print(f"Successfully Ingested: {results['successfully_ingested']}")
    print(f"Failed: {results['failed']}")
    print(f"Already Ingested: {results['already_ingested']}")
    print(f"SPRs Extracted: {results['sprs_extracted']}")
    
    if results['files_processed']:
        print("\n--- PROCESSED FILES ---")
        for file_info in results['files_processed'][:10]:  # Show first 10
            status_icon = "✅" if file_info['status'] == "ingested" else "❌"
            print(f"{status_icon} {file_info['file']}: {file_info['status']} "
                  f"({file_info['sprs_extracted']} SPRs)")
        if len(results['files_processed']) > 10:
            print(f"... and {len(results['files_processed']) - 10} more files")
    
    print("\n" + "="*70)
    print("INGESTION WORKFLOW COMPLETE")
    print("="*70 + "\n")
