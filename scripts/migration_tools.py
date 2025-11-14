#!/usr/bin/env python3
"""
Production-Grade Migration Tools for ArchE Modularization
PhD-Level Enterprise Refactoring Utilities
"""

import os
import sys
import ast
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess

@dataclass
class MigrationMapping:
    """Mapping between old and new import paths"""
    old_module: str
    new_module: str
    old_path: Path
    new_path: Path
    dependencies: List[str]
    priority: int  # 1=critical, 2=high, 3=medium, 4=low

class MigrationAnalyzer:
    """Analyzes codebase for migration dependencies"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.old_package = project_root / "Three_PointO_ArchE"
        self.new_package = project_root / "arche"
        self.mappings: List[MigrationMapping] = []
        self.import_graph: Dict[str, List[str]] = {}
    
    def analyze_imports(self, file_path: Path) -> List[str]:
        """Extract all imports from a Python file"""
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
        
        return imports
    
    def build_dependency_graph(self):
        """Build dependency graph of all modules"""
        python_files = list(self.old_package.rglob("*.py"))
        
        for file_path in python_files:
            if file_path.name == "__init__.py":
                continue
            
            module_name = file_path.stem
            relative_path = file_path.relative_to(self.old_package)
            module_path = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            
            imports = self.analyze_imports(file_path)
            self.import_graph[module_path] = [
                imp for imp in imports 
                if imp.startswith("Three_PointO_ArchE") or imp.startswith(".")
            ]
    
    def calculate_migration_order(self) -> List[str]:
        """Calculate optimal migration order based on dependencies"""
        # Topological sort
        in_degree = {node: 0 for node in self.import_graph}
        
        for node, deps in self.import_graph.items():
            for dep in deps:
                if dep in self.import_graph:
                    in_degree[node] += 1
        
        queue = [node for node, degree in in_degree.items() if degree == 0]
        order = []
        
        while queue:
            node = queue.pop(0)
            order.append(node)
            
            for other_node, deps in self.import_graph.items():
                if node in deps:
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0:
                        queue.append(other_node)
        
        return order

class MigrationExecutor:
    """Executes migration steps with validation"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.old_package = project_root / "Three_PointO_ArchE"
        self.new_package = project_root / "arche"
        self.backup_dir = project_root / "migration_backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, file_path: Path) -> Path:
        """Create backup of file before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file_path.stem}_{timestamp}.py"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def migrate_file(self, mapping: MigrationMapping, dry_run: bool = False) -> Dict[str, any]:
        """Migrate a single file to new location"""
        result = {
            'success': False,
            'backup_path': None,
            'new_file_path': None,
            'imports_updated': 0,
            'errors': []
        }
        
        try:
            # Create backup
            backup_path = self.create_backup(mapping.old_path)
            result['backup_path'] = str(backup_path)
            
            if dry_run:
                result['success'] = True
                return result
            
            # Ensure new directory exists
            mapping.new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read old file
            with open(mapping.old_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update imports
            updated_content = self.update_imports(content, mapping)
            result['imports_updated'] = updated_content['count']
            
            # Write new file
            with open(mapping.new_path, 'w', encoding='utf-8') as f:
                f.write(updated_content['content'])
            
            result['new_file_path'] = str(mapping.new_path)
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
        
        return result
    
    def update_imports(self, content: str, mapping: MigrationMapping) -> Dict[str, any]:
        """Update import statements in file content"""
        updated_content = content
        import_count = 0
        
        # Pattern for old imports
        old_pattern = rf"from\s+Three_PointO_ArchE\.{mapping.old_module}\s+import"
        new_import = f"from {mapping.new_module} import"
        
        updated_content = re.sub(old_pattern, new_import, updated_content)
        if updated_content != content:
            import_count += len(re.findall(old_pattern, content))
        
        # Also handle: from Three_PointO_ArchE import module
        old_pattern2 = rf"from\s+Three_PointO_ArchE\s+import\s+{mapping.old_module}"
        updated_content = re.sub(old_pattern2, f"from {mapping.new_module} import", updated_content)
        
        return {
            'content': updated_content,
            'count': import_count
        }
    
    def create_compatibility_shim(self, mapping: MigrationMapping) -> bool:
        """Create compatibility shim in old location"""
        shim_content = f'''"""
Compatibility shim for {mapping.old_module}
Routes to new location based on feature flags
"""
import os
import sys
from pathlib import Path

# Add new package to path if not already there
_project_root = Path(__file__).parent.parent
_new_package_path = _project_root / "arche"
if _new_package_path.exists() and str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from arche.core.feature_flags import FeatureFlags
    
    if FeatureFlags.should_use_new_import('{mapping.old_module}'):
        from {mapping.new_module} import *
    else:
        # Fallback to legacy implementation
        from .{mapping.old_module}_legacy import *
except ImportError:
    # If feature flags not available, use legacy
    try:
        from .{mapping.old_module}_legacy import *
    except ImportError:
        # Last resort: try new location
        from {mapping.new_module} import *
'''
        
        shim_path = mapping.old_path
        legacy_path = mapping.old_path.parent / f"{mapping.old_path.stem}_legacy.py"
        
        try:
            # Move old file to legacy
            if mapping.old_path.exists():
                shutil.move(mapping.old_path, legacy_path)
            
            # Write shim
            with open(shim_path, 'w', encoding='utf-8') as f:
                f.write(shim_content)
            
            return True
        except Exception as e:
            print(f"Error creating shim: {e}")
            return False

class MigrationValidator:
    """Validates migration correctness"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def validate_imports(self, module_name: str) -> Dict[str, any]:
        """Validate that imports work for both old and new"""
        result = {
            'old_import_works': False,
            'new_import_works': False,
            'both_equivalent': False,
            'errors': []
        }
        
        # Test old import
        try:
            old_module = __import__(f"Three_PointO_ArchE.{module_name}", fromlist=[''])
            result['old_import_works'] = True
        except Exception as e:
            result['errors'].append(f"Old import failed: {e}")
        
        # Test new import
        try:
            # Determine new path from mapping
            new_path = self.get_new_path(module_name)
            new_module = __import__(new_path, fromlist=[''])
            result['new_import_works'] = True
        except Exception as e:
            result['errors'].append(f"New import failed: {e}")
        
        # Compare if both work
        if result['old_import_works'] and result['new_import_works']:
            try:
                # Compare key attributes/functions
                old_attrs = dir(old_module)
                new_attrs = dir(new_module)
                
                # Check if key exports match
                key_exports = [attr for attr in old_attrs if not attr.startswith('_')]
                matching = all(attr in new_attrs for attr in key_exports)
                result['both_equivalent'] = matching
            except Exception as e:
                result['errors'].append(f"Equivalence check failed: {e}")
        
        return result
    
    def get_new_path(self, module_name: str) -> str:
        """Get new import path for module"""
        # This would use the migration mapping
        # Simplified for now
        mapping = {
            'temporal_core': 'arche.core.temporal.core',
            'config': 'arche.core.config',
            'iar_components': 'arche.core.iar.components',
        }
        return mapping.get(module_name, f"arche.{module_name}")

def main():
    """Main migration tool entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ArchE Migration Tools')
    parser.add_argument('command', choices=['analyze', 'migrate', 'validate', 'rollback'])
    parser.add_argument('--module', help='Specific module to migrate')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--project-root', type=Path, default=Path.cwd(), help='Project root directory')
    
    args = parser.parse_args()
    
    project_root = args.project_root
    
    if args.command == 'analyze':
        analyzer = MigrationAnalyzer(project_root)
        analyzer.build_dependency_graph()
        order = analyzer.calculate_migration_order()
        print("Migration Order:")
        for i, module in enumerate(order, 1):
            print(f"{i}. {module}")
    
    elif args.command == 'migrate':
        # Implementation would go here
        print("Migration command - implementation needed")
    
    elif args.command == 'validate':
        validator = MigrationValidator(project_root)
        if args.module:
            result = validator.validate_imports(args.module)
            print(json.dumps(result, indent=2))
        else:
            print("Please specify --module")
    
    elif args.command == 'rollback':
        print("Rollback command - implementation needed")

if __name__ == "__main__":
    main()


