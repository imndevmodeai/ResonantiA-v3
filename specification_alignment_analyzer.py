import os
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

def analyze_specification_alignment():
    """Analyze alignment between specifications, code, and reality"""
    print("🔍 SPECIFICATION ALIGNMENT ANALYSIS")
    print("=" * 60)
    print("Following Guardian Points mandate and 'As Above, So Below' principle")
    print()
    
    # Get all specification files
    specs_dir = Path("specifications")
    spec_files = list(specs_dir.glob("*.md"))
    
    # Get all Python files in Three_PointO_ArchE
    code_dir = Path("Three_PointO_ArchE")
    code_files = list(code_dir.glob("*.py"))
    
    print(f"📊 DISCOVERED COMPONENTS:")
    print(f"   • {len(spec_files)} specification files")
    print(f"   • {len(code_files)} Python implementation files")
    
    # Analyze alignment
    alignment_report = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "total_specs": len(spec_files),
            "total_code_files": len(code_files),
            "principle": "As Above, So Below - Guardian Points Mandate"
        },
        "specifications": {},
        "code_files": {},
        "alignment_issues": [],
        "recommendations": []
    }
    
    # Analyze each specification
    print(f"\n🔍 ANALYZING SPECIFICATIONS:")
    for spec_file in spec_files:
        spec_name = spec_file.stem
        spec_data = analyze_specification_file(spec_file)
        alignment_report["specifications"][spec_name] = spec_data
        
        # Check if corresponding code exists
        code_file = code_dir / f"{spec_name}.py"
        if code_file.exists():
            print(f"   ✅ {spec_name}: Spec + Code aligned")
            alignment_report["specifications"][spec_name]["code_exists"] = True
        else:
            print(f"   ❌ {spec_name}: Spec exists but no code")
            alignment_report["specifications"][spec_name]["code_exists"] = False
            alignment_report["alignment_issues"].append({
                "type": "missing_code",
                "spec": spec_name,
                "issue": "Specification exists but no corresponding Python implementation"
            })
    
    # Analyze each code file
    print(f"\n🔍 ANALYZING CODE FILES:")
    for code_file in code_files:
        code_name = code_file.stem
        code_data = analyze_code_file(code_file)
        alignment_report["code_files"][code_name] = code_data
        
        # Check if corresponding spec exists
        spec_file = specs_dir / f"{code_name}.md"
        if spec_file.exists():
            print(f"   ✅ {code_name}: Code + Spec aligned")
            alignment_report["code_files"][code_name]["spec_exists"] = True
        else:
            print(f"   ❌ {code_name}: Code exists but no spec")
            alignment_report["code_files"][code_name]["spec_exists"] = False
            alignment_report["alignment_issues"].append({
                "type": "missing_spec",
                "code": code_name,
                "issue": "Code exists but no corresponding specification"
            })
    
    # Generate recommendations
    generate_recommendations(alignment_report)
    
    # Save analysis report
    with open('specification_alignment_report.json', 'w') as f:
        json.dump(alignment_report, f, indent=2)
    
    print(f"\n📊 ALIGNMENT SUMMARY:")
    print(f"   • {len([s for s in alignment_report['specifications'].values() if s.get('code_exists')])} specs with aligned code")
    print(f"   • {len([c for c in alignment_report['code_files'].values() if c.get('spec_exists')])} code files with aligned specs")
    print(f"   • {len(alignment_report['alignment_issues'])} alignment issues found")
    print(f"   • {len(alignment_report['recommendations'])} recommendations generated")
    
    return alignment_report

def analyze_specification_file(spec_file: Path) -> Dict[str, Any]:
    """Analyze a single specification file"""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key information
        lines = content.split('\n')
        title = ""
        overview = ""
        status = "unknown"
        
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('## Overview') and i + 1 < len(lines):
                overview = lines[i + 1].strip()
            elif 'status:' in line.lower():
                status = line.split(':')[1].strip()
        
        return {
            "title": title,
            "overview": overview[:200] + "..." if len(overview) > 200 else overview,
            "status": status,
            "file_size": len(content),
            "line_count": len(lines),
            "has_implementation": "implementation" in content.lower(),
            "has_examples": "example" in content.lower()
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

def analyze_code_file(code_file: Path) -> Dict[str, Any]:
    """Analyze a single code file"""
    try:
        with open(code_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Basic analysis
        classes = [line.strip() for line in lines if line.strip().startswith('class ')]
        functions = [line.strip() for line in lines if line.strip().startswith('def ')]
        imports = [line.strip() for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
        
        return {
            "file_size": len(content),
            "line_count": len(lines),
            "classes": len(classes),
            "functions": len(functions),
            "imports": len(imports),
            "has_docstrings": '"""' in content or "'''" in content,
            "has_tests": "test" in content.lower(),
            "complexity": "high" if len(lines) > 500 else "medium" if len(lines) > 100 else "low"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

def generate_recommendations(alignment_report: Dict[str, Any]):
    """Generate recommendations for alignment fixes"""
    recommendations = []
    
    # Missing code recommendations
    missing_code_specs = [issue for issue in alignment_report["alignment_issues"] if issue["type"] == "missing_code"]
    if missing_code_specs:
        recommendations.append({
            "priority": "high",
            "action": "create_code",
            "description": f"Create Python implementations for {len(missing_code_specs)} specifications",
            "specs": [issue["spec"] for issue in missing_code_specs]
        })
    
    # Missing spec recommendations
    missing_spec_code = [issue for issue in alignment_report["alignment_issues"] if issue["type"] == "missing_spec"]
    if missing_spec_code:
        recommendations.append({
            "priority": "high", 
            "action": "create_specs",
            "description": f"Create specifications for {len(missing_spec_code)} code files",
            "code_files": [issue["code"] for issue in missing_spec_code]
        })
    
    # Update recommendations
    recommendations.append({
        "priority": "medium",
        "action": "update_specs",
        "description": "Update existing specifications to reflect current implementation",
        "focus": "Ensure specs match actual code functionality"
    })
    
    # Delete recommendations
    recommendations.append({
        "priority": "low",
        "action": "cleanup",
        "description": "Review and potentially delete outdated specifications",
        "focus": "Remove specs for deprecated or unused components"
    })
    
    alignment_report["recommendations"] = recommendations

if __name__ == "__main__":
    report = analyze_specification_alignment()
    print(f"\n💾 Analysis report saved to specification_alignment_report.json")
    print(f"🎯 Ready for Guardian Points mandate alignment!")
