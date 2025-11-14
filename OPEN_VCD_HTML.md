# 🌐 How to Open the VCD Browser Client

## Method 1: Direct File Access (Easiest)

### In Your Browser:
1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Press `Ctrl+L` (or `Cmd+L` on Mac) to open the address bar
3. Type or paste:
   ```
   file:///mnt/3626C55326C514B1/Happier/vcd_browser_client.html
   ```
4. Press Enter

### Or Use File Manager:
1. Open your file manager
2. Navigate to: `/mnt/3626C55326C514B1/Happier/`
3. Double-click `vcd_browser_client.html`
4. It will open in your default browser

## Method 2: HTTP Server (Recommended)

I've started a simple HTTP server for you!

### Access:
1. Open your browser
2. Go to: **http://localhost:8080/vcd_browser_client.html**

### Or start your own:
```bash
cd /mnt/3626C55326C514B1/Happier
python3 -m http.server 8080
```
Then open: **http://localhost:8080/vcd_browser_client.html**

## Method 3: Command Line (Linux)

```bash
# Using xdg-open (most Linux systems)
xdg-open /mnt/3626C55326C514B1/Happier/vcd_browser_client.html

# Or using specific browser
firefox /mnt/3626C55326C514B1/Happier/vcd_browser_client.html
# or
google-chrome /mnt/3626C55326C514B1/Happier/vcd_browser_client.html
# or
chromium /mnt/3626C55326C514B1/Happier/vcd_browser_client.html
```

## Method 4: From Cursor/VS Code

If you're using Cursor or VS Code:
1. Right-click on `vcd_browser_client.html` in the file explorer
2. Select "Open with Live Server" (if extension installed)
3. Or "Reveal in File Manager" then double-click

## ✅ Quick Access

**Simplest way:**
1. Open browser
2. Type: `file:///mnt/3626C55326C514B1/Happier/vcd_browser_client.html`
3. Press Enter

**Or use HTTP server:**
1. Open browser  
2. Go to: `http://localhost:8080/vcd_browser_client.html`

## 🎯 What Happens Next

Once the HTML file opens:
1. It will **automatically try to connect** to `ws://localhost:8765`
2. You'll see the connection status (green = connected)
3. The cognitive stream will start showing real-time data
4. You can click buttons to interact with the VCD

## 📊 If Connection Fails

Make sure the VCD Bridge is running:
```bash
# Check if running
ps aux | grep vcd_bridge

# If not running, start it:
python3 vcd_bridge.py &
```

The HTML file is ready to open! 🚀


