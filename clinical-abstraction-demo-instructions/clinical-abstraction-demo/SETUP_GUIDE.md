# Step-by-Step Setup Guide

This guide walks you through setting up the Clinical Abstraction Demo from scratch.

## What You Need to Run

This demo requires **TWO servers** running simultaneously:

1. **Flask Backend Server (Port 5000)** - Makes OpenAI API calls
2. **HTTP Server (Port 8000)** - Serves the web interface

Both servers must be running for the demo to work.

---

## Setup Steps

### Step 1: Extract the Demo Package

```bash
tar -xzf clinical-abstraction-demo.tar.gz
cd clinical-abstraction-demo
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `flask` - Web framework for the backend API
- `flask-cors` - Allows the frontend to call the backend API
- `openai` - OpenAI API client library

### Step 3: Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...` or `sk-...`)
5. Make sure you have credits available in your account

### Step 4: Provide Your API Key

You have **TWO options** for providing your API key:

#### Option A: Set Environment Variable (Recommended)

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"
```

#### Option B: Enter in Web UI

Skip setting the environment variable and enter your API key in the settings panel when you open the web interface.

---

## Step 5: Start the Servers

### Option 1: Use the Startup Script (Easiest)

**Linux/Mac:**
```bash
chmod +x start_demo.sh
./start_demo.sh
```

This will:
- ✓ Check dependencies
- ✓ Start Flask backend on port 5000
- ✓ Start HTTP server on port 8000
- ✓ Show you the URLs to access

Press `Ctrl+C` when you want to stop both servers.

### Option 2: Manual Startup (Windows or Advanced Users)

You need to open **TWO terminal windows**.

**Terminal 1 - Flask Backend:**
```bash
cd clinical-abstraction-demo
python extraction_backend_openai.py
```

You should see:
```
============================================================
Clinical Abstraction Backend - OpenAI Version
============================================================
Server: http://localhost:5000
✓ OpenAI API configured from OPENAI_API_KEY environment variable
 * Running on http://127.0.0.1:5000
```

**Terminal 2 - HTTP Server:**
```bash
cd clinical-abstraction-demo
python -m http.server 8000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

**Keep both terminals running!**

---

## Step 6: Open the Application

Open your web browser and go to:

**Local Development:**
```
http://localhost:8000/index_ai_clean.html
```

**Verily Workbench Users:**
```
https://workbench.verily.com/app/YOUR-WORKSPACE-ID/proxy/8000/index_ai_clean.html
```

Replace `YOUR-WORKSPACE-ID` with your actual workspace ID from the URL.

---

## Step 7: Verify Everything is Working

### Check 1: Backend Status

Open this URL in a new browser tab:
```
http://localhost:5000/health
```

You should see:
```json
{
  "status": "ok",
  "openai_configured": true,
  "provider": "openai"
}
```

If `openai_configured` is `false`, your API key is not set correctly.

### Check 2: Load Sample Data

1. In the web interface, click "📂 Upload Files"
2. Navigate to the `sample_notes/` folder in the demo directory
3. Select all 3 `.txt` files and upload them
4. You should see 3 patients loaded

### Check 3: Test AI Extraction

1. Select a patient from the dropdown
2. Click "🤖 Extract with AI"
3. Wait 5-10 seconds
4. You should see extracted variables appear on the right panel

If this works, **everything is set up correctly!** ✅

---

## Understanding the Architecture

```
┌─────────────────────────────────────────────────┐
│  Your Web Browser                               │
│  http://localhost:8000/index_ai_clean.html      │
└────────┬───────────────────────────┬────────────┘
         │                           │
         │ Loads HTML/JS             │ Sends clinical text
         │ from HTTP server          │ for extraction
         │                           │
         ▼                           ▼
┌──────────────────────┐    ┌────────────────────┐
│  HTTP Server         │    │  Flask Backend     │
│  Port 8000           │    │  Port 5000         │
│                      │    │                    │
│  Serves static files │    │  extraction_       │
│  (HTML, JS)          │    │  backend_openai.py │
└──────────────────────┘    └──────────┬─────────┘
                                       │
                                       │ Makes API calls
                                       │ with your API key
                                       ▼
                            ┌─────────────────────┐
                            │  OpenAI API         │
                            │  (GPT-4)            │
                            │                     │
                            │  Returns extracted  │
                            │  clinical variables │
                            └─────────────────────┘
```

**Key Points:**
- The **HTTP server** just serves the HTML/JavaScript files
- The **Flask backend** is what actually calls OpenAI's API
- Your **API key** is only used by the Flask backend
- Both servers must be running for the demo to work

---

## Common Issues & Solutions

### Issue: "Port 5000 already in use"

**Solution:** Kill the process using port 5000:
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows (PowerShell as Admin)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
```

### Issue: "Port 8000 already in use"

**Solution:** Use a different port:
```bash
python -m http.server 8888
```

Then access: `http://localhost:8888/index_ai_clean.html`

### Issue: "OpenAI API not configured" error

**Solution:**
1. Check your environment variable: `echo $OPENAI_API_KEY`
2. Make sure you exported it in the same terminal where you run the Flask server
3. Or enter the API key directly in the web UI settings

### Issue: "Invalid API key" or authentication errors

**Solutions:**
1. Verify your key at https://platform.openai.com/api-keys
2. Make sure the key is not expired
3. Check you have credits available in your OpenAI account
4. Ensure you copied the entire key (including `sk-proj-...`)

### Issue: Backend returns 500 error

**Solution:** Check the Flask terminal output for error messages. Common causes:
- API rate limits exceeded
- Insufficient credits in OpenAI account
- Network connectivity issues

### Issue: "Extract with AI" button does nothing

**Solutions:**
1. Open browser console (F12) and check for errors
2. Verify Flask backend is running on port 5000
3. Check the `/health` endpoint: `http://localhost:5000/health`
4. Make sure both servers are running

---

## Next Steps

Once everything is working:

1. **Try the sample notes** - Upload all 3 files from `sample_notes/`
2. **Experiment with extraction** - See how AI identifies clinical variables
3. **Test with your own data** - Upload your own clinical notes (.txt format)
4. **Adjust settings** - Try different models (gpt-4o vs gpt-4o-mini)
5. **Customize prompts** - Use the settings to modify extraction instructions

---

## Stopping the Demo

**If using start_demo.sh:**
- Press `Ctrl+C` in the terminal

**If running manually:**
- Press `Ctrl+C` in both terminal windows

**To verify servers stopped:**
```bash
lsof -ti:5000,8000
# Should return nothing
```

---

## Getting Help

If you're still having issues:

1. Check `README.md` for detailed documentation
2. Look at the Flask terminal output for error messages
3. Check browser console (F12) for JavaScript errors
4. Verify your OpenAI API key is valid and has credits
5. Make sure you have Python 3.9+ installed: `python --version`

The most common issue is forgetting to start BOTH servers or not providing a valid API key.
