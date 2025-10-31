#!/usr/bin/env python3
"""
ArchE System Setup and Validation Script
This script helps users configure the ArchE system properly and validates all prerequisites.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

def print_header(title: str):
    """Print a formatted header."""
    print("=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)

def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")

def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠️  {message}")

def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")

def check_python_version():
    """Check if Python version is compatible."""
    print_header("Python Version Check")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} is not compatible. Requires Python 3.8+")
        return False

def check_environment_file():
    """Check and create environment file if needed."""
    print_header("Environment Configuration")
    
    env_file = Path(".env")
    env_template = Path("env.template")
    
    if env_file.exists():
        print_success("Environment file (.env) exists")
        
        # Check if GEMINI_API_KEY is set
        with open(env_file, 'r') as f:
            content = f.read()
            if "GEMINI_API_KEY" in content and "your_gemini_api_key_here" not in content:
                print_success("GEMINI_API_KEY appears to be configured")
                return True
            else:
                print_warning("GEMINI_API_KEY not properly configured in .env file")
                return False
    else:
        if env_template.exists():
            print_warning("Environment file (.env) not found, but template exists")
            print("Please:")
            print("1. Copy env.template to .env")
            print("2. Add your Google Gemini API key to the .env file")
            print("3. Get your API key from: https://makersuite.google.com/app/apikey")
            return False
        else:
            print_error("Neither .env nor env.template found")
            return False

def check_critical_files():
    """Check if critical files exist and are valid."""
    print_header("Critical Files Check")
    
    critical_files = [
        ("knowledge_graph/spr_definitions_tv.json", "SPR Definitions"),
        ("workflows/", "Workflows Directory"),
        ("chronicles/genesis_chronicle.json", "Genesis Chronicle"),
        ("Three_PointO_ArchE/", "Core Module Directory")
    ]
    
    all_good = True
    
    for file_path, description in critical_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                # Check if file is not empty
                if path.stat().st_size > 0:
                    print_success(f"{description}: {file_path}")
                else:
                    print_warning(f"{description} is empty: {file_path}")
                    all_good = False
            else:
                print_success(f"{description}: {file_path}")
        else:
            print_error(f"{description} not found: {file_path}")
            all_good = False
    
    return all_good

def check_python_dependencies():
    """Check if required Python packages are installed."""
    print_header("Python Dependencies Check")
    
    required_packages = [
        "google.generativeai",
        "requests",
        "numpy",
        "scipy",
        "pandas",
        "dotenv"
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is available")
        except ImportError:
            print_error(f"{package} is not installed")
            all_good = False
    
    return all_good

def validate_json_files():
    """Validate that JSON files are properly formatted."""
    print_header("JSON File Validation")
    
    json_files = [
        "knowledge_graph/spr_definitions_tv.json",
        "chronicles/genesis_chronicle.json",
        "workflows/temporal_forecasting_workflow.json"
    ]
    
    all_good = True
    
    for json_file in json_files:
        path = Path(json_file)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print_success(f"{json_file} is valid JSON")
            except json.JSONDecodeError as e:
                print_error(f"{json_file} has JSON syntax errors: {e}")
                all_good = False
        else:
            print_warning(f"{json_file} not found")
    
    return all_good

def test_system_initialization():
    """Test if the system can initialize without errors."""
    print_header("System Initialization Test")
    
    try:
        # Test importing key modules
        sys.path.insert(0, str(Path.cwd()))
        
        from Three_PointO_ArchE.spr_manager import SPRManager
        from Three_PointO_ArchE.genesis_chronicle import GenesisChronicle
        
        # Test SPRManager initialization
        spr_path = Path("knowledge_graph/spr_definitions_tv.json")
        if spr_path.exists():
            spr_manager = SPRManager(str(spr_path))
            print_success("SPRManager initialized successfully")
        else:
            print_error("Cannot test SPRManager - spr_definitions_tv.json not found")
            return False
        
        # Test GenesisChronicle initialization
        genesis_chronicle = GenesisChronicle()
        print_success("GenesisChronicle initialized successfully")
        
        return True
        
    except Exception as e:
        print_error(f"System initialization failed: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    print_header("Creating Environment File")
    
    env_file = Path(".env")
    env_template = Path("env.template")
    
    if env_file.exists():
        print_warning(".env file already exists")
        return False
    
    if not env_template.exists():
        print_error("env.template not found")
        return False
    
    try:
        with open(env_template, 'r') as f:
            template_content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(template_content)
        
        print_success("Created .env file from template")
        print_warning("Please edit .env file and add your GEMINI_API_KEY")
        return True
        
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False

def main():
    """Main setup function."""
    print_header("ArchE System Setup and Validation")
    print("This script will check your ArchE system configuration and help you set it up properly.")
    print()
    
    # Check Python version
    if not check_python_version():
        print_error("Python version check failed. Please upgrade to Python 3.8+")
        return False
    
    print()
    
    # Check environment
    env_ok = check_environment_file()
    if not env_ok:
        print()
        response = input("Would you like to create a .env file from template? (y/n): ")
        if response.lower() == 'y':
            create_env_file()
            print()
            print_warning("Please edit the .env file and add your GEMINI_API_KEY before continuing")
            print_warning("Get your API key from: https://makersuite.google.com/app/apikey")
            return False
    
    print()
    
    # Check critical files
    if not check_critical_files():
        print_error("Critical files check failed")
        return False
    
    print()
    
    # Check Python dependencies
    if not check_python_dependencies():
        print_error("Python dependencies check failed")
        print_warning("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    print()
    
    # Validate JSON files
    if not validate_json_files():
        print_error("JSON validation failed")
        return False
    
    print()
    
    # Test system initialization
    if not test_system_initialization():
        print_error("System initialization test failed")
        return False
    
    print()
    print_header("Setup Complete")
    print_success("All checks passed! Your ArchE system is ready to use.")
    print()
    print("Next steps:")
    print("1. Ensure your .env file contains a valid GEMINI_API_KEY")
    print("2. Start the WebSocket server: node webSocketServer.js")
    print("3. Start the Next.js frontend: cd nextjs-chat && npm run dev")
    print("4. Open your browser to the URL shown by the Next.js server")
    print()
    print("For help, see the README.md file or run: python mastermind/interact.py --help")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 