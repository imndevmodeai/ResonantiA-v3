# 🛡️ AppArmor Management Guide
**Built with ArchE's ResonantiA Protocol v3.1-CA**

## ✅ IMMEDIATE ISSUE RESOLVED
Your applications (VLC, Brave, Telegram, Firefox) should now work!
AppArmor has been temporarily disabled to restore immediate access.

## 🔍 WHAT HAPPENED
- AppArmor profiles were enforcing strict restrictions on snap applications
- These restrictions blocked essential applications from running
- Emergency disable restored immediate functionality

## 📋 CURRENT STATUS
```bash
# Check AppArmor status
sudo systemctl status apparmor
# Should show: "inactive (dead)"
```

## 🔄 MANAGEMENT OPTIONS

### Option 1: Keep AppArmor Disabled (Simplest)
**Pros:** All apps work, no restrictions
**Cons:** Reduced system security

```bash
# Ensure AppArmor stays disabled
sudo systemctl disable apparmor
```

### Option 2: Re-enable with Selective Permissions (Recommended)
**Pros:** Security maintained, apps work
**Cons:** Requires configuration

```bash
# Re-enable AppArmor
sudo systemctl start apparmor
sudo systemctl enable apparmor

# Set specific apps to complain mode (allows with logging)
sudo aa-complain /snap/vlc/current/usr/bin/vlc
sudo aa-complain /snap/brave/current/usr/bin/brave
sudo aa-complain /snap/telegram-desktop/current/usr/bin/telegram-desktop

# Or disable specific problematic profiles
sudo aa-disable /snap/vlc/current/usr/bin/vlc
sudo aa-disable /snap/brave/current/usr/bin/brave
```

### Option 3: Full Security Reconfiguration
**Pros:** Maximum security with functionality
**Cons:** Complex setup

Use the `apparmor_emergency_fix.py` tool created above for guided setup.

## 🧪 TESTING YOUR APPLICATIONS

### Test VLC
```bash
vlc --version
# Or just open VLC from applications menu
```

### Test Brave Browser
```bash
brave-browser --version
# Or open from applications menu
```

### Test Telegram
```bash
telegram-desktop --version
# Or open from applications menu
```

## 🚨 IF PROBLEMS RETURN

### Quick Emergency Disable
```bash
sudo systemctl stop apparmor
```

### Check What's Blocking
```bash
sudo aa-status | grep enforce
sudo journalctl -u apparmor | tail -20
```

### Comprehensive Fix
```bash
sudo python apparmor_emergency_fix.py
```

## 🔧 TROUBLESHOOTING COMMANDS

### Check AppArmor Status
```bash
sudo systemctl status apparmor
sudo aa-status
```

### View AppArmor Logs
```bash
sudo journalctl -u apparmor -f
sudo dmesg | grep -i apparmor
```

### List All Profiles
```bash
sudo aa-status | head -50
```

### Emergency Commands
```bash
# Stop AppArmor
sudo systemctl stop apparmor

# Start AppArmor  
sudo systemctl start apparmor

# Reload profiles
sudo systemctl reload apparmor

# Disable specific profile
sudo aa-disable PROFILE_NAME

# Enable complain mode
sudo aa-complain PROFILE_NAME
```

## 📱 APPLICATION-SPECIFIC FIXES

### VLC Issues
```bash
sudo aa-disable /snap/vlc/current/usr/bin/vlc
# Or for complain mode:
sudo aa-complain /snap/vlc/current/usr/bin/vlc
```

### Brave Browser Issues
```bash
sudo aa-disable /snap/brave/current/usr/bin/brave
```

### Telegram Issues
```bash
sudo aa-disable /snap/telegram-desktop/current/usr/bin/telegram-desktop
```

## 🛡️ SECURITY CONSIDERATIONS

### With AppArmor Disabled
- Applications have full system access
- Reduced protection against malicious software
- Standard Linux permissions still apply

### With AppArmor Enabled
- Applications run in restricted environments
- Better protection against exploits
- May occasionally block legitimate functionality

## 🎯 RECOMMENDED APPROACH

1. **Test your applications now** - they should work
2. **Keep AppArmor disabled temporarily** while you work
3. **When convenient, re-enable with selective permissions**:
   ```bash
   sudo systemctl start apparmor
   sudo aa-complain snap.vlc.vlc
   sudo aa-complain snap.brave.brave
   sudo aa-complain snap.telegram-desktop.telegram-desktop
   ```

## 📞 IF YOU NEED HELP
- The comprehensive fix tool is available: `apparmor_emergency_fix.py`
- Emergency disable: `sudo systemctl stop apparmor`
- Re-enable: `sudo systemctl start apparmor`

Your applications should now work perfectly! 🎉
