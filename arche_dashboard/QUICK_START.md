# Quick Start - Complete Dashboard

## One Command to Rule Them All

```bash
cd /mnt/3626C55326C514B1/Happier/arche_dashboard && ./start_complete.sh
```

That's it! This single command will:
1. ✅ Kill any existing dashboard instances
2. ✅ Start the backend API server
3. ✅ Start the frontend HTTP server
4. ✅ Open the dashboard in your browser

## What It Does

### Step 1: Cleanup
- Kills all existing backend processes (api.py, uvicorn)
- Kills all existing frontend HTTP servers
- Clears ports for fresh start

### Step 2: Prerequisites
- Checks for virtual environment
- Activates `arche_env`
- Installs missing packages if needed

### Step 3: Backend
- Starts backend API on port 8000 (or next available)
- Waits for backend to be ready
- Verifies health endpoint

### Step 4: Frontend
- Starts HTTP server on port 3000 (or next available)
- Serves the dashboard interface

### Step 5: Browser
- Automatically opens dashboard in your default browser
- Falls back to manual instructions if auto-open fails

## Access Points

After running the script, you'll see:
- **Frontend**: http://localhost:3000 (or detected port)
- **Backend API**: http://localhost:8000 (or detected port)
- **API Docs**: http://localhost:8000/docs

## Stop the Dashboard

```bash
cd /mnt/3626C55326C514B1/Happier/arche_dashboard && ./stop_dashboard.sh
```

Or manually:
```bash
# Kill by PID files
kill $(cat arche_dashboard/backend.pid) $(cat arche_dashboard/frontend.pid)

# Or kill all processes
pkill -f "python3.*api.py"
pkill -f "python3 -m http.server"
```

## Logs

- **Backend logs**: `arche_dashboard/backend.log`
- **Frontend logs**: `arche_dashboard/frontend.log`

## Troubleshooting

### Port Already in Use
The script automatically finds available ports. If you see port conflicts:
1. Check what's using the port: `lsof -i :8000`
2. Kill the process: `kill -9 <PID>`
3. Run the script again

### Backend Won't Start
1. Check logs: `tail -f arche_dashboard/backend.log`
2. Verify virtual environment: `source arche_env/bin/activate`
3. Check dependencies: `pip list | grep fastapi`

### Frontend Won't Start
1. Check logs: `tail -f arche_dashboard/frontend.log`
2. Try a different port manually:
   ```bash
   cd arche_dashboard/frontend
   python3 -m http.server 8080
   ```

### Browser Won't Open
Just manually open: http://localhost:3000 (or the port shown in output)

## Process Management

The script saves PIDs to:
- `arche_dashboard/backend.pid`
- `arche_dashboard/frontend.pid`

You can use these to check if processes are running:
```bash
# Check backend
kill -0 $(cat arche_dashboard/backend.pid) && echo "Running" || echo "Stopped"

# Check frontend
kill -0 $(cat arche_dashboard/frontend.pid) && echo "Running" || echo "Stopped"
```

## Background Mode

To run in background and continue using terminal:
```bash
cd /mnt/3626C55326C514B1/Happier/arche_dashboard
nohup ./start_complete.sh > startup.log 2>&1 &
```

Then check status:
```bash
tail -f startup.log
```

---

**That's it! One command, complete dashboard! 🚀**

