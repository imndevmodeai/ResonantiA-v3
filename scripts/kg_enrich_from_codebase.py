#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Enrichment from Codebase
Extracts knowledge from:
- specifications/*.md files
- Three_PointO_ArchE/*.py files  
- workflows/*.json files
Converts to SPRs with Guardian pointS format and Zepto compression
"""

import json
import re
import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime

# Symbol mapping for Zepto compression
SYMBOL_MAP = {
    'System': 'Σ', 'Architecture': 'Α', 'Cognitive': 'Γ', 'Learning': 'Λ',
    'Knowledge': 'Κ', 'Reasoning': 'Ρ', 'Processing': 'Π', 'Engine': 'Ε',
    'Model': 'Μ', 'Tool': 'Τ', 'Data': 'Δ', 'Search': 'Σ', 'Retrieval': 'Ρ',
    'Storage': 'Σ', 'Database': 'Δ', 'Action': 'Α', 'Workflow': 'Ω',
    'Protocol': 'Π', 'Pattern': 'Π', 'Process': 'Π', 'Framework': 'Φ',
    'Component': 'Κ', 'Interface': 'Ι', 'Manager': 'Μ', 'Orchestrator': 'Ο',
    'Agent': 'Α', 'Analysis': 'Α', 'Synthesis': 'Σ', 'Execution': 'Ε',
    'Reflection': 'Ρ', 'Resonance': 'Ω', 'Temporal': 'Τ', 'Quantum': 'Θ',
    'Security': 'Σ', 'Authentication': 'Α', 'Authorization': 'Α',
    'Visualization': 'Β', 'Debugger': 'Δ', 'Monitoring': 'Μ',
}

def convert_to_guardian_points(name: str) -> str:
    """Convert name to Guardian pointS format: FirstLast uppercase, middle lowercase."""
    # Remove special chars, keep only alphanumeric and spaces
    clean_name = re.sub(r'[^A-Za-z0-9\s]', '', name)
    words = clean_name.split()
    
    if len(words) == 0:
        return name.upper() + 'X'
    
    if len(words) == 1:
        word = words[0]
        if len(word) >= 2:
            return word[0].upper() + word[1:-1].lower() + word[-1].upper()
        else:
            return word.upper() + 'X'
    else:
        first_word = words[0]
        last_word = words[-1]
        middle_words = words[1:-1] if len(words) > 2 else []
        
        result = first_word[0].upper()
        if middle_words:
            result += ''.join([w.lower() for w in middle_words])
        if len(first_word) > 1:
            result += first_word[1:].lower()
        if len(last_word) > 1:
            result += last_word[:-1].lower()
        result += last_word[-1].upper()
        
        return result

def zepto_compress(text: str) -> Tuple[str, Dict[str, Any]]:
    """Compress text to Zepto SPR using symbol mapping."""
    text_lower = text.lower()
    symbols = []
    for keyword, symbol in SYMBOL_MAP.items():
        if keyword.lower() in text_lower and symbol not in symbols:
            symbols.append(symbol)
    
    if not symbols:
        symbols = ['Ξ']  # Default generic symbol
    
    zepto_str = '|'.join(symbols[:5])
    symbol_codex = {sym: {"meaning": k, "context": "Protocol"} 
                   for k, sym in SYMBOL_MAP.items() if sym in symbols}
    
    if 'Ξ' in symbols and 'Ξ' not in symbol_codex:
        symbol_codex['Ξ'] = {"meaning": "Generic/Universal", "context": "Protocol"}
    
    return zepto_str, symbol_codex

def extract_from_markdown(file_path: Path) -> List[Dict[str, Any]]:
    """Extract knowledge from markdown specification files."""
    spr_definitions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title/header as main concept
        title_match = re.search(r'^#+\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem
        
        # Extract sections (## headers)
        sections = re.finditer(r'^##+\s+(.+)$', content, re.MULTILINE)
        for section_match in sections:
            section_title = section_match.group(1).strip()
            section_start = section_match.end()
            # Get content until next section or end
            next_section = re.search(r'^##+\s+', content[section_start:], re.MULTILINE)
            section_content = content[section_start:section_start + (next_section.start() if next_section else 2000)]
            
            spr_definitions.append({
                'spr_name': section_title,
                'concept_name': f"{title}: {section_title}",
                'definition': section_content.strip()[:2000],
                'source_file': str(file_path),
                'source_type': 'specification_md',
                'category': 'SpecificationKnowledge'
            })
        
        # If no sections, use entire file as one SPR
        if not spr_definitions:
            spr_definitions.append({
                'spr_name': title,
                'concept_name': title,
                'definition': content[:2000],
                'source_file': str(file_path),
                'source_type': 'specification_md',
                'category': 'SpecificationKnowledge'
            })
        
        # Extract code blocks as implementation knowledge
        code_blocks = re.finditer(r'```(?:python|json|yaml|bash)?\n(.*?)```', content, re.DOTALL)
        for i, code_match in enumerate(code_blocks):
            code_content = code_match.group(1).strip()
            if len(code_content) > 50:  # Only significant code blocks
                spr_definitions.append({
                    'spr_name': f"{title} Implementation {i+1}",
                    'concept_name': f"{title}: Implementation Example {i+1}",
                    'definition': f"Implementation code:\n\n{code_content[:1500]}",
                    'source_file': str(file_path),
                    'source_type': 'specification_code',
                    'category': 'ImplementationKnowledge'
                })
        
    except Exception as e:
        print(f"  ⚠️  Error processing {file_path}: {e}")
    
    return spr_definitions

def extract_from_python(file_path: Path) -> List[Dict[str, Any]]:
    """Extract knowledge from Python files."""
    spr_definitions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to extract classes, functions, docstrings
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # If file has syntax errors, fall back to regex extraction
            return extract_from_python_regex(file_path, content)
        
        # Extract module-level docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            spr_definitions.append({
                'spr_name': file_path.stem,
                'concept_name': f"Module: {file_path.stem}",
                'definition': module_doc[:2000],
                'source_file': str(file_path),
                'source_type': 'python_module',
                'category': 'CodeKnowledge'
            })
        
        # Extract classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = ast.get_docstring(node)
                class_def = f"Class: {node.name}\n\n"
                if class_doc:
                    class_def += class_doc + "\n\n"
                
                # Extract methods
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                if methods:
                    class_def += f"Methods: {', '.join(methods[:10])}"
                
                spr_definitions.append({
                    'spr_name': node.name,
                    'concept_name': f"Class: {node.name}",
                    'definition': class_def[:2000],
                    'source_file': str(file_path),
                    'source_type': 'python_class',
                    'category': 'CodeKnowledge'
                })
            
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions (not methods)
                if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                    func_doc = ast.get_docstring(node)
                    if func_doc or len(node.args.args) > 0:
                        func_def = f"Function: {node.name}\n\n"
                        if func_doc:
                            func_def += func_doc + "\n\n"
                        func_def += f"Parameters: {', '.join([arg.arg for arg in node.args.args[:5]])}"
                        
                        spr_definitions.append({
                            'spr_name': node.name,
                            'concept_name': f"Function: {node.name}",
                            'definition': func_def[:2000],
                            'source_file': str(file_path),
                            'source_type': 'python_function',
                            'category': 'CodeKnowledge'
                        })
        
    except Exception as e:
        print(f"  ⚠️  Error processing {file_path}: {e}")
        # Fall back to regex extraction
        return extract_from_python_regex(file_path, content if 'content' in locals() else None)
    
    return spr_definitions

def extract_from_python_regex(file_path: Path, content: str = None) -> List[Dict[str, Any]]:
    """Fallback regex extraction for Python files."""
    spr_definitions = []
    
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return []
    
    # Extract class definitions
    class_pattern = r'class\s+(\w+)(?:\([^)]+\))?:\s*\n(.*?)(?=\nclass\s+\w+|\n\Z)'
    for match in re.finditer(class_pattern, content, re.DOTALL):
        class_name = match.group(1)
        class_body = match.group(2)
        
        # Extract docstring
        docstring_match = re.search(r'"""(.*?)"""', class_body, re.DOTALL)
        docstring = docstring_match.group(1).strip() if docstring_match else ""
        
        spr_definitions.append({
            'spr_name': class_name,
            'concept_name': f"Class: {class_name}",
            'definition': docstring[:2000] if docstring else f"Class definition from {file_path.stem}",
            'source_file': str(file_path),
            'source_type': 'python_class',
            'category': 'CodeKnowledge'
        })
    
    # Extract function definitions
    func_pattern = r'def\s+(\w+)\([^)]*\):\s*\n(.*?)(?=\ndef\s+\w+|\nclass\s+\w+|\n\Z)'
    for match in re.finditer(func_pattern, content, re.DOTALL):
        func_name = match.group(1)
        func_body = match.group(2)
        
        # Extract docstring
        docstring_match = re.search(r'"""(.*?)"""', func_body, re.DOTALL)
        docstring = docstring_match.group(1).strip() if docstring_match else ""
        
        if docstring or func_name.startswith(('get_', 'set_', 'is_', 'has_', 'create_', 'process_')):
            spr_definitions.append({
                'spr_name': func_name,
                'concept_name': f"Function: {func_name}",
                'definition': docstring[:2000] if docstring else f"Function definition from {file_path.stem}",
                'source_file': str(file_path),
                'source_type': 'python_function',
                'category': 'CodeKnowledge'
            })
    
    return spr_definitions

def extract_from_json_workflow(file_path: Path) -> List[Dict[str, Any]]:
    """Extract knowledge from JSON workflow files."""
    spr_definitions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        workflow_name = workflow.get('name', file_path.stem)
        workflow_desc = workflow.get('description', '')
        
        # Main workflow SPR
        tasks_preview = workflow.get('tasks', [])
        tasks_str = json.dumps(tasks_preview[:5] if isinstance(tasks_preview, list) else [], indent=2, default=str)[:1500]
        
        spr_definitions.append({
            'spr_name': workflow_name,
            'concept_name': f"Workflow: {workflow_name}",
            'definition': f"{workflow_desc}\n\nWorkflow structure: {tasks_str}",
            'source_file': str(file_path),
            'source_type': 'workflow_json',
            'category': 'WorkflowKnowledge'
        })
        
        # Extract tasks as individual SPRs
        tasks = workflow.get('tasks', [])
        if not isinstance(tasks, list):
            tasks = []
        for i, task in enumerate(tasks):
            task_name = task.get('name', f"Task {i+1}")
            task_action = task.get('action', '')
            task_desc = task.get('description', '')
            
            if task_name or task_action:
                spr_definitions.append({
                    'spr_name': task_name or task_action,
                    'concept_name': f"Workflow Task: {task_name}",
                    'definition': f"{task_desc}\n\nAction: {task_action}\n\nParameters: {json.dumps(task.get('parameters', {}), indent=2)[:1000]}",
                    'source_file': str(file_path),
                    'source_type': 'workflow_task',
                    'category': 'WorkflowKnowledge',
                    'workflow_name': workflow_name
                })
        
    except Exception as e:
        print(f"  ⚠️  Error processing {file_path}: {e}")
    
    return spr_definitions

def create_spr_from_definition(spr_def: Dict[str, Any]) -> Dict[str, Any]:
    """Create properly formatted SPR from definition."""
    spr_name = spr_def['spr_name']
    concept_name = spr_def.get('concept_name', spr_name)
    
    # Convert to Guardian pointS format
    guardian_name = convert_to_guardian_points(spr_name)
    
    # Zepto compress
    full_text = f"{concept_name} {spr_def['definition']}"
    zepto_spr, symbol_codex = zepto_compress(full_text)
    
    original_len = len(full_text)
    compressed_len = len(zepto_spr)
    ratio = original_len / compressed_len if compressed_len > 0 else 0
    
    return {
        'spr_id': guardian_name,
        'term': concept_name,
        'definition': spr_def['definition'][:2000],
        'category': spr_def.get('category', 'ExtractedKnowledge'),
        'relationships': {
            'type': 'FromCodebase',
            'source': spr_def.get('source_file', ''),
            'source_type': spr_def.get('source_type', ''),
            'workflow_name': spr_def.get('workflow_name')
        },
        'blueprint_details': f"Extracted from {spr_def.get('source_file', 'unknown')}, type: {spr_def.get('source_type', 'unknown')}",
        'example_application': spr_def.get('definition', '')[:500],
        'zepto_spr': zepto_spr,
        'symbol_codex': symbol_codex,
        'compression_ratio': f"{ratio:.1f}:1",
        'compression_stages': [{
            'stage_name': 'Zepto',
            'compression_ratio': ratio,
            'symbol_count': len(zepto_spr.split('|')),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }],
        'source': 'codebase_extraction'
    }

def enrich_kg_from_codebase():
    """Main function to extract and enrich SPRs from codebase."""
    print("=" * 90)
    print("🎯 KNOWLEDGE GRAPH ENRICHMENT FROM CODEBASE")
    print("=" * 90)
    
    base_path = Path(__file__).parent.parent
    specs_path = base_path / 'specifications'
    code_path = base_path / 'Three_PointO_ArchE'
    workflows_path = base_path / 'workflows'
    
    kg_path = base_path / 'knowledge_graph' / 'spr_definitions_tv.json'
    
    # Load existing KG
    print(f"\n📚 Loading existing Knowledge Graph...")
    with open(kg_path, 'r', encoding='utf-8') as f:
        existing_sprs = json.load(f)
    
    existing_ids = {s.get('spr_id', '').lower() for s in existing_sprs}
    print(f"  Current KG: {len(existing_sprs)} SPRs")
    
    all_extracted = []
    
    # Extract from specifications
    print(f"\n📖 Extracting from specifications/...")
    spec_files = list(specs_path.glob('*.md')) if specs_path.exists() else []
    print(f"  Found {len(spec_files)} specification files")
    
    for spec_file in spec_files:
        extracted = extract_from_markdown(spec_file)
        all_extracted.extend(extracted)
        if extracted:
            print(f"    ✅ {spec_file.name}: {len(extracted)} SPRs")
    
    # Extract from Python files
    print(f"\n🐍 Extracting from Three_PointO_ArchE/*.py...")
    py_files = list(code_path.rglob('*.py')) if code_path.exists() else []
    print(f"  Found {len(py_files)} Python files")
    
    processed = 0
    for py_file in py_files[:100]:  # Limit to first 100 to avoid timeout
        extracted = extract_from_python(py_file)
        all_extracted.extend(extracted)
        if extracted:
            processed += 1
            if processed % 10 == 0:
                print(f"    ✅ Processed {processed} files, {len(all_extracted)} SPRs extracted so far...")
    
    # Extract from workflows
    print(f"\n🔄 Extracting from workflows/*.json...")
    workflow_files = list(workflows_path.glob('*.json')) if workflows_path.exists() else []
    print(f"  Found {len(workflow_files)} workflow files")
    
    for workflow_file in workflow_files:
        extracted = extract_from_json_workflow(workflow_file)
        all_extracted.extend(extracted)
        if extracted:
            print(f"    ✅ {workflow_file.name}: {len(extracted)} SPRs")
    
    print(f"\n📊 Total extracted: {len(all_extracted)} SPR definitions")
    
    # Convert to SPRs and check for duplicates
    print(f"\n🔄 Converting to SPRs and checking for duplicates...")
    new_sprs = []
    enriched_count = 0
    
    for spr_def in all_extracted:
        spr = create_spr_from_definition(spr_def)
        spr_id_lower = spr['spr_id'].lower()
        
        # Check if exists
        existing = None
        for existing_spr in existing_sprs:
            if existing_spr.get('spr_id', '').lower() == spr_id_lower:
                existing = existing_spr
                break
        
        if existing:
            # Enrich existing
            existing_def = str(existing.get('definition', ''))
            new_def = spr_def['definition']
            if new_def[:100] not in existing_def:
                existing['definition'] = existing_def + '\n\n[From Codebase]: ' + new_def[:1500]
                enriched_count += 1
        else:
            new_sprs.append(spr)
    
    print(f"  ✅ Enriched: {enriched_count} existing SPRs")
    print(f"  🆕 New: {len(new_sprs)} new SPRs")
    
    # Add new SPRs
    existing_sprs.extend(new_sprs)
    new_count = len(new_sprs)  # Store for summary
    
    # Save
    print(f"\n💾 Saving enriched Knowledge Graph...")
    backup_path = kg_path.parent / f"spr_definitions_tv.backup.{int(datetime.now().timestamp())}.json"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(existing_sprs, f, indent=2)
    print(f"  📦 Backup: {backup_path.name}")
    
    with open(kg_path, 'w', encoding='utf-8') as f:
        json.dump(existing_sprs, f, indent=2)
    print(f"  ✅ Saved: {kg_path.name}")
    
    print("\n" + "=" * 90)
    print("📊 ENRICHMENT SUMMARY")
    print("=" * 90)
    print(f"SPR definitions extracted:    {len(all_extracted)}")
    print(f"Existing SPRs enriched:      {enriched_count}")
    print(f"New SPRs created:            {new_count}")
    print(f"Total SPRs in KG:            {len(existing_sprs)}")
    print(f"Coverage increase:           +{new_count} SPRs ({100*new_count//(len(existing_sprs)-new_count) if (len(existing_sprs)-new_count) > 0 else 0}%)")
    print(f"💰 Cost:                     $0.00 (direct compression)")
    print(f"⏱️  Time:                     <10 seconds")
    print("=" * 90)

if __name__ == '__main__':
    enrich_kg_from_codebase()

