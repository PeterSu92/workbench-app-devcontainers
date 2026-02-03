# Distribution Guide

## For You (The Distributor)

Share the `clinical-abstraction-demo.tar.gz` file with your colleagues via:
- Email attachment
- Shared drive (Google Drive, Box, etc.)
- Internal file sharing system
- Git repository

## For Your Colleagues (The Recipients)

### Step 1: Extract the Archive

```bash
tar -xzf clinical-abstraction-demo.tar.gz
cd clinical-abstraction-demo
```

### Step 2: Quick Start

Read `QUICKSTART.txt` for the fastest setup, or follow these steps:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get an OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Either:
     - Set it: `export OPENAI_API_KEY="sk-..."`
     - Or enter it in the web UI when prompted

3. **Start the demo:**
   ```bash
   ./start_demo.sh
   ```

4. **Open your browser:**
   - Local: `http://localhost:8000/index_ai_clean.html`
   - Verily Workbench: `https://workbench.verily.com/app/YOUR-WORKSPACE-ID/proxy/8000/index_ai_clean.html`

### Step 3: Explore

- Load sample patient data
- Try extracting clinical variables from the 3 included sample notes
- Upload your own clinical notes (.txt files)

## What They'll Get

- Complete working demo (no additional downloads needed except pip packages)
- 3 sample clinical notes to test with
- Full documentation in README.md
- One-command startup script
- Flask API backend source code (Python)
- Web interface (HTML/JavaScript)

## System Requirements

- Python 3.9 or higher
- Internet connection (for OpenAI API calls)
- OpenAI API key with available credits
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Support

Direct your colleagues to:
1. `QUICKSTART.txt` - 5-minute setup guide
2. `README.md` - Full documentation with troubleshooting
3. Or to you for questions!
