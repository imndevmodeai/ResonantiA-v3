# Restart Instructions for Query Enhancement Feature

## Quick Answer

**Yes, you need to restart the dashboard backend** to see the new "✨ Enhance Query" feature.

---

## Steps to Restart

### Option 1: If Dashboard is Running in Terminal

1. **Stop the current backend:**
   - Press `Ctrl+C` in the terminal where the dashboard is running
   - OR find and kill the process:
     ```bash
     pkill -f "python3 api.py"
     ```

2. **Restart the backend:**
   ```bash
   cd /mnt/3626C55326C514B1/Happier/arche_dashboard/backend
   source ../../arche_env/bin/activate
   python3 api.py
   ```

### Option 2: Using the Startup Script

```bash
cd /mnt/3626C55326C514B1/Happier/arche_dashboard
./start_dashboard.sh
```

---

## What Changed

### Backend Changes
- ✅ New API endpoint: `/api/query/enhance`
- ✅ New Pydantic model: `QueryEnhancementRequest`
- ✅ Integration with `query_enhancement_engine.py`

### Frontend Changes
- ✅ New "✨ Enhance Query" button
- ✅ Enhanced query display container
- ✅ Analysis display with capabilities and confidence

---

## After Restart

1. **Refresh your browser** (if the frontend HTML is already open)
   - Press `F5` or `Ctrl+R` (or `Cmd+R` on Mac)

2. **Look for the new button:**
   - You should see a "✨ Enhance Query" button next to "🚀 Submit Query"

3. **Test it:**
   - Enter a query like "How can I monetize ArchE?"
   - Click "✨ Enhance Query"
   - Review the enhanced query and analysis
   - Click "Use This Query" to apply it

---

## Verify It's Working

After restarting, you can verify the endpoint is available:

```bash
curl -X POST http://localhost:8000/api/query/enhance \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "enhancement_level": "auto"}'
```

You should get a JSON response with `status: "success"` and enhancement results.

---

## Troubleshooting

### If the button doesn't appear:
- Make sure you refreshed the browser after restarting the backend
- Check browser console for JavaScript errors (F12 → Console)
- Verify the frontend HTML file was updated

### If enhancement fails:
- Check backend logs for errors
- Verify `query_enhancement_engine.py` is in the correct location
- Check that SPR definitions file exists at `knowledge_graph/spr_definitions_tv.json`

---

## Note

The backend runs with `reload=False` to prevent port conflicts, so manual restart is required when code changes are made.

