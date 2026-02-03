# Pre-Flight Checklist ✓

Use this checklist to ensure everything is set up correctly.

## Before You Start

- [ ] Python 3.9 or higher installed (`python --version`)
- [ ] OpenAI API key obtained from https://platform.openai.com/api-keys
- [ ] OpenAI account has available credits
- [ ] Extracted `clinical-abstraction-demo.tar.gz`

## Installation

- [ ] Navigated to `clinical-abstraction-demo` directory
- [ ] Ran `pip install -r requirements.txt`
- [ ] Verified Flask installed: `python -c "import flask; print(flask.__version__)"`
- [ ] Verified OpenAI installed: `python -c "import openai; print(openai.__version__)"`

## API Key Configuration

Choose ONE of these options:

**Option A: Environment Variable**
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Verified: `echo $OPENAI_API_KEY` shows your key

**Option B: Web UI**
- [ ] Will enter API key in the web interface settings panel

## Server Startup

**If using start_demo.sh:**
- [ ] Made script executable: `chmod +x start_demo.sh`
- [ ] Ran `./start_demo.sh`
- [ ] Saw "✓ Demo is running!" message

**If starting manually:**
- [ ] Opened Terminal 1
- [ ] Started Flask backend: `python extraction_backend_openai.py`
- [ ] Saw "✓ OpenAI API configured" message (or warning if key not set)
- [ ] Saw "Running on http://127.0.0.1:5000"
- [ ] Opened Terminal 2
- [ ] Started HTTP server: `python -m http.server 8000`
- [ ] Saw "Serving HTTP on 0.0.0.0 port 8000"
- [ ] Both terminals are still running

## Verification

- [ ] Opened browser to `http://localhost:8000/index_ai_clean.html`
- [ ] Page loaded successfully (dark theme interface visible)
- [ ] Checked backend health: `http://localhost:5000/health` shows `"openai_configured": true`
- [ ] If using Workbench, verified proxy URL works

## First Test

- [ ] Clicked "📂 Upload Files" in the web interface
- [ ] Selected all 3 files from `sample_notes/` folder
- [ ] Saw "✓ Loaded 3 clinical notes" message
- [ ] Selected first patient from dropdown
- [ ] Clicked "🤖 Extract with AI" button
- [ ] Button changed to "🤖 Extracting..."
- [ ] After 5-10 seconds, saw extracted variables appear
- [ ] Variables show evidence text highlighted in the document

## Success Indicators

You should see:
- ✓ Green toast message: "✓ Extracted X variables"
- ✓ Variables panel on right shows extracted data
- ✓ Confidence badges (High/Medium/Low)
- ✓ Evidence text highlighted in the document
- ✓ Model badge showing which GPT model was used

## If Something Failed

Check which step failed and refer to:
- **SETUP_GUIDE.md** - Detailed troubleshooting
- **README.md** - Full documentation
- **QUICKSTART.txt** - Quick reference

## Common Failure Points

**No variables extracted?**
- Check Flask terminal for error messages
- Verify API key is valid and has credits
- Check browser console (F12) for JavaScript errors

**"OpenAI API not configured" error?**
- Set environment variable OR enter key in UI settings
- Restart Flask server after setting environment variable

**Page won't load?**
- Verify HTTP server is running on port 8000
- Check the URL is correct

**Backend unreachable?**
- Verify Flask server is running on port 5000
- Check firewall isn't blocking localhost connections

---

## You're All Set! ✅

If all checkboxes are checked, the demo is fully functional and ready to use.

You can now:
- Upload your own clinical notes (.txt files)
- Experiment with different AI models
- Customize extraction prompts in settings
- Export extracted data

Enjoy the demo!
