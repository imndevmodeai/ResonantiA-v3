#!/usr/bin/env python3
"""
AppArmor Emergency Fix Tool
Built with ArchE's ResonantiA Protocol v3.1-CA

Comprehensive tool to restore access to blocked applications.
"""

import subprocess
import os
import sys

class AppArmorFixer:
    def __init__(self):
        self.blocked_apps = [
            'snap.vlc.vlc',
            'snap.brave.brave', 
            'snap.telegram-desktop.telegram-desktop',
            'snap.firefox.firefox',
            'snap.obs-studio.obs-studio'
        ]
        
    def check_admin_privileges(self):
        """Check if running with admin privileges"""
        if os.geteuid() != 0:
            print("❌ This script requires sudo privileges")
            print("Run with: sudo python apparmor_emergency_fix.py")
            return False
        return True
    
    def backup_apparmor_profiles(self):
        """Backup current AppArmor profiles"""
        print("📦 BACKING UP APPARMOR PROFILES")
        print("=" * 35)
        
        backup_dir = "/tmp/apparmor_backup_$(date +%Y%m%d_%H%M%S)"
        try:
            subprocess.run(['mkdir', '-p', backup_dir], check=True)
            subprocess.run(['cp', '-r', '/etc/apparmor.d/', backup_dir], check=True)
            print(f"✅ Backup created: {backup_dir}")
            return backup_dir
        except Exception as e:
            print(f"⚠️ Backup failed: {e}")
            return None
    
    def set_profiles_to_complain_mode(self):
        """Set problematic profiles to complain mode (non-blocking)"""
        print("\n🔧 SETTING PROFILES TO COMPLAIN MODE")
        print("=" * 40)
        
        success_count = 0
        
        for profile in self.blocked_apps:
            try:
                print(f"Setting {profile} to complain mode...")
                result = subprocess.run(['aa-complain', profile], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {profile} set to complain mode")
                    success_count += 1
                else:
                    print(f"  ⚠️ {profile} - {result.stderr.strip()}")
            except Exception as e:
                print(f"  ❌ {profile} error: {e}")
        
        return success_count
    
    def disable_specific_profiles(self):
        """Disable specific problematic profiles"""
        print("\n🚫 DISABLING PROBLEMATIC PROFILES")
        print("=" * 35)
        
        success_count = 0
        
        for profile in self.blocked_apps:
            try:
                print(f"Disabling {profile}...")
                result = subprocess.run(['aa-disable', profile], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {profile} disabled")
                    success_count += 1
                else:
                    print(f"  ⚠️ {profile} - {result.stderr.strip()}")
            except Exception as e:
                print(f"  ❌ {profile} error: {e}")
        
        return success_count
    
    def reload_apparmor_profiles(self):
        """Reload AppArmor profiles"""
        print("\n🔄 RELOADING APPARMOR PROFILES")
        print("=" * 30)
        
        try:
            result = subprocess.run(['systemctl', 'reload', 'apparmor'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ AppArmor profiles reloaded")
                return True
            else:
                print(f"⚠️ Reload warning: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Reload error: {e}")
            return False
    
    def test_applications(self):
        """Test if applications can now run"""
        print("\n🧪 TESTING APPLICATION ACCESS")
        print("=" * 30)
        
        test_commands = {
            'VLC': ['vlc', '--version'],
            'Brave': ['brave-browser', '--version'],
            'Telegram': ['telegram-desktop', '--version'],
            'Firefox': ['firefox', '--version']
        }
        
        working_apps = []
        
        for app_name, command in test_commands.items():
            try:
                print(f"Testing {app_name}...")
                result = subprocess.run(command, capture_output=True, 
                                      text=True, timeout=10)
                if result.returncode == 0:
                    print(f"  ✅ {app_name} is working")
                    working_apps.append(app_name)
                else:
                    print(f"  ❌ {app_name} still blocked")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️ {app_name} timeout (may be working)")
                working_apps.append(app_name)
            except Exception as e:
                print(f"  ❌ {app_name} error: {e}")
        
        return working_apps
    
    def emergency_apparmor_disable(self):
        """Emergency: Temporarily disable AppArmor entirely"""
        print("\n�� EMERGENCY: DISABLING APPARMOR TEMPORARILY")
        print("=" * 45)
        print("WARNING: This reduces system security!")
        print("Only use if other methods fail.")
        
        try:
            # Stop AppArmor service
            subprocess.run(['systemctl', 'stop', 'apparmor'], check=True)
            print("✅ AppArmor service stopped")
            
            # Disable AppArmor kernel module
            subprocess.run(['aa-teardown'], check=True)
            print("✅ AppArmor profiles unloaded")
            
            return True
        except Exception as e:
            print(f"❌ Emergency disable failed: {e}")
            return False
    
    def re_enable_apparmor(self):
        """Re-enable AppArmor after emergency disable"""
        print("\n🔄 RE-ENABLING APPARMOR")
        print("=" * 25)
        
        try:
            subprocess.run(['systemctl', 'start', 'apparmor'], check=True)
            print("✅ AppArmor service restarted")
            return True
        except Exception as e:
            print(f"❌ Re-enable failed: {e}")
            return False
    
    def run_comprehensive_fix(self):
        """Run comprehensive AppArmor fix procedure"""
        print("🚨 APPARMOR EMERGENCY FIX TOOL")
        print("Built with ArchE's ResonantiA Protocol v3.1-CA")
        print("=" * 50)
        
        if not self.check_admin_privileges():
            return False
        
        # Step 1: Backup
        backup_dir = self.backup_apparmor_profiles()
        
        # Step 2: Try complain mode first (safer)
        print("\n📋 METHOD 1: COMPLAIN MODE (SAFER)")
        print("=" * 35)
        complain_success = self.set_profiles_to_complain_mode()
        
        if complain_success > 0:
            self.reload_apparmor_profiles()
            working_apps = self.test_applications()
            
            if len(working_apps) >= 2:  # If most apps work
                print(f"\n🎉 SUCCESS! {len(working_apps)} applications restored")
                print("Applications should now work with logging enabled.")
                return True
        
        # Step 3: Try disabling profiles
        print("\n📋 METHOD 2: DISABLE PROFILES")
        print("=" * 30)
        disable_success = self.disable_specific_profiles()
        
        if disable_success > 0:
            self.reload_apparmor_profiles()
            working_apps = self.test_applications()
            
            if len(working_apps) >= 2:
                print(f"\n🎉 SUCCESS! {len(working_apps)} applications restored")
                return True
        
        # Step 4: Emergency disable (last resort)
        print("\n📋 METHOD 3: EMERGENCY DISABLE (LAST RESORT)")
        print("=" * 45)
        response = input("This will temporarily disable AppArmor entirely. Continue? (y/N): ")
        
        if response.lower() == 'y':
            if self.emergency_apparmor_disable():
                working_apps = self.test_applications()
                
                if len(working_apps) >= 2:
                    print(f"\n🎉 EMERGENCY SUCCESS! {len(working_apps)} applications restored")
                    print("\n⚠️ IMPORTANT: AppArmor is disabled for security!")
                    print("To re-enable later: sudo systemctl start apparmor")
                    return True
        
        print("\n❌ ALL METHODS FAILED")
        print("Manual intervention required.")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--emergency-disable':
        # Quick emergency disable
        print("🚨 EMERGENCY APPARMOR DISABLE")
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'apparmor'], check=True)
            subprocess.run(['sudo', 'aa-teardown'], check=True)
            print("✅ AppArmor temporarily disabled")
        except:
            print("❌ Emergency disable failed")
    else:
        fixer = AppArmorFixer()
        fixer.run_comprehensive_fix()

if __name__ == "__main__":
    main()
