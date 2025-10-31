#!/usr/bin/env python3
"""
Log Organization and Cataloging System for ArchE/RISE Framework

This script reorganizes the chaotic log structure into a hierarchical, 
searchable, and debuggable system with proper naming conventions.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from collections import defaultdict

class LogOrganizer:
    def __init__(self, outputs_dir: str = "outputs"):
        self.outputs_dir = Path(outputs_dir)
        self.organized_dir = Path("logs_organized")
        self.catalog_file = self.organized_dir / "log_catalog.json"
        
        # Create organized directory structure
        self.organized_dir.mkdir(exist_ok=True)
        (self.organized_dir / "workflows").mkdir(exist_ok=True)
        (self.organized_dir / "phases").mkdir(exist_ok=True)
        (self.organized_dir / "errors").mkdir(exist_ok=True)
        (self.organized_dir / "sessions").mkdir(exist_ok=True)
        (self.organized_dir / "analysis").mkdir(exist_ok=True)
        
        self.catalog = self._load_catalog()
    
    def _load_catalog(self) -> Dict[str, Any]:
        """Load existing catalog or create new one"""
        if self.catalog_file.exists():
            with open(self.catalog_file, 'r') as f:
                return json.load(f)
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "total_logs": 0,
                "last_organized": None
            },
            "workflows": {},
            "phases": {},
            "errors": {},
            "sessions": {},
            "analysis": {}
        }
    
    def _save_catalog(self):
        """Save catalog to file"""
        self.catalog["metadata"]["last_organized"] = datetime.now().isoformat()
        with open(self.catalog_file, 'w') as f:
            json.dump(self.catalog, f, indent=2)
    
    def _extract_log_metadata(self, log_file: Path) -> Dict[str, Any]:
        """Extract metadata from a log file"""
        metadata = {
            "original_file": str(log_file),
            "size_bytes": log_file.stat().st_size,
            "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
            "workflow_name": "unknown",
            "run_id": "unknown",
            "phase": "unknown",
            "session_id": "unknown",
            "error_count": 0,
            "task_count": 0,
            "duration_sec": 0,
            "status": "unknown"
        }
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                metadata["line_count"] = len(lines)
                
                # Parse first few lines to extract metadata
                for i, line in enumerate(lines[:10]):  # Check first 10 lines
                    try:
                        data = json.loads(line.strip())
                        if "workflow_name" in data:
                            metadata["workflow_name"] = data["workflow_name"]
                        if "run_id" in data:
                            metadata["run_id"] = data["run_id"]
                        if "session_id" in data:
                            metadata["session_id"] = data["session_id"]
                        if "error" in data.get("result", {}):
                            metadata["error_count"] += 1
                        if "task_key" in data:
                            metadata["task_count"] += 1
                        if "duration_sec" in data:
                            metadata["duration_sec"] += data["duration_sec"]
                            
                        # Determine phase from workflow name
                        workflow = data.get("workflow_name", "").lower()
                        if "knowledge" in workflow or "scaffolding" in workflow:
                            metadata["phase"] = "A"
                        elif "strategy" in workflow or "fusion" in workflow:
                            metadata["phase"] = "B"
                        elif "vetting" in workflow or "high_stakes" in workflow:
                            metadata["phase"] = "C"
                        elif "utopian" in workflow or "refinement" in workflow:
                            metadata["phase"] = "D"
                        else:
                            metadata["phase"] = "unknown"
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            metadata["parse_error"] = str(e)
            
        return metadata
    
    def _generate_organized_filename(self, metadata: Dict[str, Any]) -> str:
        """Generate a descriptive filename for organized logs"""
        # Extract date from modified time
        modified_date = datetime.fromisoformat(metadata["modified"]).strftime("%Y%m%d_%H%M%S")
        
        # Clean workflow name
        workflow_clean = re.sub(r'[^\w\-_]', '_', metadata["workflow_name"])
        workflow_clean = workflow_clean.replace('__', '_').strip('_')
        
        # Generate descriptive filename
        filename_parts = [
            modified_date,
            f"phase_{metadata['phase']}",
            workflow_clean[:30],  # Limit length
            metadata["run_id"][:8],  # Short run ID
            f"{metadata['task_count']}tasks",
            f"{metadata['error_count']}errors"
        ]
        
        return "_".join(filename_parts) + ".jsonl"
    
    def organize_logs(self, dry_run: bool = False) -> Dict[str, Any]:
        """Organize all log files into structured directories"""
        print(f"🔍 Scanning {self.outputs_dir} for log files...")
        
        log_files = list(self.outputs_dir.glob("run_events_run_*.jsonl"))
        print(f"📊 Found {len(log_files)} log files to organize")
        
        organization_stats = {
            "total_processed": 0,
            "by_workflow": defaultdict(int),
            "by_phase": defaultdict(int),
            "by_status": defaultdict(int),
            "errors": [],
            "organized_files": []
        }
        
        for log_file in log_files:
            try:
                metadata = self._extract_log_metadata(log_file)
                organization_stats["total_processed"] += 1
                
                # Update catalog
                workflow_name = metadata["workflow_name"]
                phase = metadata["phase"]
                
                if workflow_name not in self.catalog["workflows"]:
                    self.catalog["workflows"][workflow_name] = {
                        "count": 0,
                        "phases": set(),
                        "sessions": set(),
                        "total_errors": 0,
                        "total_tasks": 0
                    }
                
                self.catalog["workflows"][workflow_name]["count"] += 1
                self.catalog["workflows"][workflow_name]["phases"].add(phase)
                self.catalog["workflows"][workflow_name]["sessions"].add(metadata["session_id"])
                self.catalog["workflows"][workflow_name]["total_errors"] += metadata["error_count"]
                self.catalog["workflows"][workflow_name]["total_tasks"] += metadata["task_count"]
                
                # Clean workflow name for directory
                workflow_clean = re.sub(r'[^\w\-_]', '_', metadata["workflow_name"])
                workflow_clean = workflow_clean.replace('__', '_').strip('_')
                
                # Determine destination directory
                if metadata["error_count"] > 0:
                    dest_dir = self.organized_dir / "errors"
                    organization_stats["by_status"]["error"] += 1
                elif phase != "unknown":
                    dest_dir = self.organized_dir / "phases" / f"phase_{phase}"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    organization_stats["by_phase"][phase] += 1
                else:
                    dest_dir = self.organized_dir / "workflows" / workflow_clean
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    organization_stats["by_workflow"][workflow_name] += 1
                
                # Generate organized filename
                organized_filename = self._generate_organized_filename(metadata)
                dest_path = dest_dir / organized_filename
                
                if not dry_run:
                    # Copy file to organized location
                    shutil.copy2(log_file, dest_path)
                    
                    # Create metadata file
                    metadata_file = dest_path.with_suffix('.metadata.json')
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                
                organization_stats["organized_files"].append({
                    "original": str(log_file),
                    "organized": str(dest_path),
                    "metadata": metadata
                })
                
                print(f"✅ {log_file.name} -> {dest_path}")
                
            except Exception as e:
                error_msg = f"Error processing {log_file}: {str(e)}"
                organization_stats["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        
        # Convert sets to lists for JSON serialization
        for workflow_data in self.catalog["workflows"].values():
            workflow_data["phases"] = list(workflow_data["phases"])
            workflow_data["sessions"] = list(workflow_data["sessions"])
        
        self.catalog["metadata"]["total_logs"] = organization_stats["total_processed"]
        
        if not dry_run:
            self._save_catalog()
            self._generate_analysis_reports()
        
        return organization_stats
    
    def _generate_analysis_reports(self):
        """Generate analysis reports from organized logs"""
        print("📈 Generating analysis reports...")
        
        # Workflow analysis
        workflow_report = {
            "summary": {
                "total_workflows": len(self.catalog["workflows"]),
                "most_common_workflow": max(self.catalog["workflows"].items(), key=lambda x: x[1]["count"])[0] if self.catalog["workflows"] else None,
                "total_errors": sum(w["total_errors"] for w in self.catalog["workflows"].values()),
                "total_tasks": sum(w["total_tasks"] for w in self.catalog["workflows"].values())
            },
            "workflows": self.catalog["workflows"]
        }
        
        with open(self.organized_dir / "analysis" / "workflow_analysis.json", 'w') as f:
            json.dump(workflow_report, f, indent=2)
        
        # Phase analysis
        phase_stats = defaultdict(lambda: {"count": 0, "workflows": set(), "errors": 0})
        
        for workflow_name, workflow_data in self.catalog["workflows"].items():
            for phase in workflow_data["phases"]:
                phase_stats[phase]["count"] += workflow_data["count"]
                phase_stats[phase]["workflows"].add(workflow_name)
                phase_stats[phase]["errors"] += workflow_data["total_errors"]
        
        # Convert sets to lists
        for phase_data in phase_stats.values():
            phase_data["workflows"] = list(phase_data["workflows"])
        
        phase_report = {
            "summary": {
                "total_phases": len(phase_stats),
                "phase_distribution": dict(phase_stats)
            }
        }
        
        with open(self.organized_dir / "analysis" / "phase_analysis.json", 'w') as f:
            json.dump(phase_report, f, indent=2)
        
        # Error analysis
        error_report = {
            "summary": {
                "total_errors": sum(w["total_errors"] for w in self.catalog["workflows"].values()),
                "error_rate": sum(w["total_errors"] for w in self.catalog["workflows"].values()) / max(sum(w["total_tasks"] for w in self.catalog["workflows"].values()), 1)
            },
            "workflows_with_errors": {
                name: data for name, data in self.catalog["workflows"].items() 
                if data["total_errors"] > 0
            }
        }
        
        with open(self.organized_dir / "analysis" / "error_analysis.json", 'w') as f:
            json.dump(error_report, f, indent=2)
    
    def search_logs(self, query: str) -> List[Dict[str, Any]]:
        """Search through organized logs"""
        results = []
        
        for workflow_name, workflow_data in self.catalog["workflows"].items():
            if query.lower() in workflow_name.lower():
                results.append({
                    "type": "workflow",
                    "name": workflow_name,
                    "data": workflow_data
                })
        
        return results
    
    def get_debugging_info(self, run_id: str = None, workflow_name: str = None) -> Dict[str, Any]:
        """Get debugging information for specific run or workflow"""
        debug_info = {
            "run_id": run_id,
            "workflow_name": workflow_name,
            "related_logs": [],
            "error_summary": {},
            "timeline": []
        }
        
        # Find related logs
        for file_info in self.catalog.get("organized_files", []):
            metadata = file_info["metadata"]
            if (run_id and run_id in metadata["run_id"]) or \
               (workflow_name and workflow_name in metadata["workflow_name"]):
                debug_info["related_logs"].append(file_info)
                
                if metadata["error_count"] > 0:
                    debug_info["error_summary"][metadata["run_id"]] = {
                        "error_count": metadata["error_count"],
                        "workflow": metadata["workflow_name"],
                        "phase": metadata["phase"]
                    }
        
        return debug_info

def main():
    """Main function to run log organization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize ArchE/RISE logs for better debugging")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be organized without actually doing it")
    parser.add_argument("--search", type=str, help="Search for specific workflow or run")
    parser.add_argument("--debug", type=str, help="Get debugging info for specific run ID or workflow")
    
    args = parser.parse_args()
    
    organizer = LogOrganizer()
    
    if args.search:
        results = organizer.search_logs(args.search)
        print(f"🔍 Search results for '{args.search}':")
        for result in results:
            print(f"  - {result['name']}: {result['data']['count']} runs")
    
    elif args.debug:
        debug_info = organizer.get_debugging_info(args.debug)
        print(f"🐛 Debug info for '{args.debug}':")
        print(json.dumps(debug_info, indent=2))
    
    else:
        print("🚀 Starting log organization...")
        stats = organizer.organize_logs(dry_run=args.dry_run)
        
        print("\n📊 Organization Summary:")
        print(f"  Total processed: {stats['total_processed']}")
        print(f"  By workflow: {dict(stats['by_workflow'])}")
        print(f"  By phase: {dict(stats['by_phase'])}")
        print(f"  By status: {dict(stats['by_status'])}")
        
        if stats['errors']:
            print(f"\n❌ Errors encountered:")
            for error in stats['errors']:
                print(f"  - {error}")
        
        if not args.dry_run:
            print(f"\n✅ Logs organized in: {organizer.organized_dir}")
            print(f"📋 Catalog saved to: {organizer.catalog_file}")

if __name__ == "__main__":
    main()
