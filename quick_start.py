#!/usr/bin/env python3
"""
ArchE Quick Start Interface
Immediate processing interface for Google AI Studio content
"""

import os
import json
from datetime import datetime

def main():
    """Quick start interface with real-time input processing"""
    
    print("\n" + "🔥"*40)
    print("ArchE COGNITIVE TOOLS - QUICK START")
    print("ResonantiA Protocol v3.1-CA ACTIVE")
    print("Keyholder Override: IMnDEVmode CONFIRMED")
    print("🔥"*40)
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Open your Google AI Studio link in a browser")
    print("2. Copy ALL the content (Ctrl+A, then Ctrl+C)")
    print("3. Paste it when prompted below")
    print("4. ArchE will generate complete implementations")
    
    print("\n" + "="*60)
    print("PASTE YOUR GOOGLE AI STUDIO CONTENT BELOW:")
    print("(Press Enter twice when finished)")
    print("="*60)
    
    # Collect multi-line input
    content_lines = []
    empty_line_count = 0
    
    while True:
        try:
            line = input()
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
            else:
                empty_line_count = 0
                content_lines.append(line)
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return
        except EOFError:
            break
    
    if not content_lines:
        print("\n❌ No content provided. Exiting.")
        return
    
    content = "\n".join(content_lines)
    
    print(f"\n✅ CONTENT RECEIVED ({len(content)} characters)")
    print("\n🚀 INITIATING ARCHE PROCESSING...")
    
    # Process using the master system
    try:
        from arche_master_integration import ArchEMasterSystem
        
        master = ArchEMasterSystem()
        result = master.process_manual_content(content, ["comprehensive", "production_ready"])
        
        # Display results
        master.display_processing_summary(result)
        
        # Generate and export project
        project_name = f"ai_studio_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project = master.generate_complete_project(content, project_name)
        
        # Save project files to disk
        export_result = master.export_complete_project(result, f"./{project_name}")
        
        if export_result.get("export_status") == "success":
            print(f"\n🎉 SUCCESS! Complete project exported to: ./{project_name}/")
            print(f"📁 {export_result['files_written']} files generated")
            
            # Show deployment instructions
            print("\n🚀 DEPLOYMENT INSTRUCTIONS:")
            print(f"cd {project_name}")
            print("python -m venv venv")
            print("source venv/bin/activate  # (Linux/Mac) or venv\\Scripts\\activate (Windows)")
            print("pip install -r requirements.txt")
            print("python main.py")
            
        print("\n✨ ArchE processing complete! Your implementation is ready.")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        print("Check that all ArchE framework files are present.")

if __name__ == "__main__":
    main()