#!/usr/bin/env python3
"""
Integrity verification script for Four_PointO_ArchE
"""
import os, json, hashlib

def verify_integrity():
    target_root = os.path.dirname(os.path.abspath(__file__))
    backup_dirs = [d for d in os.listdir('.') if d.startswith(f'{os.path.basename(target_root)}_backup_')]
    
    if not backup_dirs:
        print("ERROR: No backup found")
        return False
    
    latest_backup = sorted(backup_dirs)[-1]
    safety_manifest_path = os.path.join(latest_backup, 'safety_manifest.json')
    
    if not os.path.exists(safety_manifest_path):
        print("ERROR: Safety manifest not found")
        return False
    
    with open(safety_manifest_path, 'r') as f:
        manifest = json.load(f)
    
    all_good = True
    for file_info in manifest.get('critical_files', []):
        file_path = os.path.join(target_root, file_info['path'])
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            if current_hash == file_info['hash']:
                print(f"✓ {file_info['path']} - OK")
            else:
                print(f"✗ {file_info['path']} - MODIFIED")
                all_good = False
        else:
            print(f"✗ {file_info['path']} - MISSING")
            all_good = False
    
    return all_good

if __name__ == '__main__':
    if verify_integrity():
        print("
SUCCESS: All files verified")
    else:
        print("
WARNING: Some files have been modified")
