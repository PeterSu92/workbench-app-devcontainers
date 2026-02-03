# Clinical Abstraction Demo - Package Contents

## What's Included

This package contains a complete clinical data abstraction system with AI-powered extraction and protocol management.

### Core Application Files

- **`index_ai_clean.html`** - Main web interface (single-file application)
  - Complete frontend with all features
  - Protocol management UI
  - Variable extraction and review interface
  - Statistics dashboard
  - No build process required - just open in a browser

- **`extraction_backend_openai.py`** - Flask backend API server
  - OpenAI GPT-4 integration
  - Protocol rules processing
  - Clinical note parsing
  - Runs on port 5000

### Sample Data

- **`sample_notes/`** - Three example clinical notes
  - `patient_001_cardiology.txt` - Cardiology consultation
  - `patient_002_hf_clinic.txt` - Heart failure clinic note
  - `patient_003_acute_hf.txt` - Acute heart failure admission
  - Use these to test the system

### Testing

- **`tests.js`** - Unit test suite (31 tests)
  - Run with: `node tests.js`
  - Tests protocol CRUD, persistence, AI integration
  - All tests should pass

- **`integration_tests.js`** - Integration test suite (14 tests)
  - Run with: `node integration_tests.js`
  - Tests backend API and AI extraction
  - Requires backend running and OpenAI API key

### Documentation

- **`README.md`** - Project overview and features
- **`SETUP_GUIDE.md`** - Step-by-step setup instructions
- **`QUICKSTART.txt`** - Quick start commands
- **`CHECKLIST.md`** - Pre-distribution checklist
- **`DISTRIBUTION_GUIDE.md`** - How to package and distribute

### Helper Scripts

- **`start_demo.sh`** - Automated startup script (Linux/Mac)
  - Starts both backend and frontend servers
  - Press Ctrl+C to stop

- **`requirements.txt`** - Python dependencies
  - flask
  - flask-cors
  - openai

## Quick Start

### 1. Extract the Package
```bash
unzip clinical-abstraction-demo.zip
cd clinical-abstraction-demo
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set OpenAI API Key
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"
```

Get your API key from: https://platform.openai.com/api-keys

### 4. Start the Application

**Option A: Automated (Linux/Mac)**
```bash
chmod +x start_demo.sh
./start_demo.sh
```

**Option B: Manual (All Platforms)**

Terminal 1 - Backend:
```bash
python extraction_backend_openai.py
```

Terminal 2 - Frontend:
```bash
python -m http.server 8000
```

### 5. Open in Browser
```
http://localhost:8000/index_ai_clean.html
```

### 6. Test the System

1. Click "📂 Upload Files"
2. Select all files from `sample_notes/` directory
3. Select a patient from the dropdown
4. Click "🤖 Extract with AI"
5. Review and accept/reject extractions
6. Click "📖 Protocol" to view/edit abstraction rules

## Key Features Implemented

### Protocol Management
- Create, edit, duplicate, and delete protocol rules
- Enable/disable rules with toggle switches
- Set rule priorities (lower = higher priority)
- Import/export protocols as JSON

### AI Integration
- Protocol rules sent to OpenAI during extraction
- Rules guide AI decision-making (e.g., "prefer lab values")
- Visual indicators show which rules were applied

### Variable Statistics Dashboard
- Per-variable metrics (acceptance rate, confidence, value distribution)
- Overall statistics across all patients
- Identify variables needing review

### Enhanced UX
- "📖 Rules" button on every variable shows applicable protocol rules
- Purple badge shows count of rules applied to each extraction
- Click badge to see exactly which rules influenced AI decisions
- Contextual help throughout interface

## System Requirements

- Python 3.9 or higher
- Node.js (for running tests)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- OpenAI API account with credits
- Internet connection for API calls

## File Sizes

- Total package: ~70 KB (compressed)
- Main HTML file: ~202 KB (uncompressed)
- All files: ~300 KB (uncompressed)

## Architecture

```
┌─────────────────────────────────────┐
│  Web Browser (Port 8000)            │
│  index_ai_clean.html                │
│  - Protocol Management UI           │
│  - Extraction Review Interface      │
│  - Statistics Dashboard             │
└─────────────┬───────────────────────┘
              │
              │ HTTP POST /extract
              │ (with protocol_rules)
              ▼
┌─────────────────────────────────────┐
│  Flask Backend (Port 5000)          │
│  extraction_backend_openai.py       │
│  - Receives protocol rules          │
│  - Creates AI prompt                │
└─────────────┬───────────────────────┘
              │
              │ API Call
              ▼
┌─────────────────────────────────────┐
│  OpenAI API                         │
│  GPT-4 / GPT-4o / GPT-4o-mini       │
│  - Follows protocol rules           │
│  - Extracts clinical variables      │
└─────────────────────────────────────┘
```

## Support

For issues or questions:
1. Check `SETUP_GUIDE.md` for detailed instructions
2. Review `README.md` for feature documentation
3. Run tests to verify installation: `node tests.js`
4. Check browser console (F12) for frontend errors
5. Check Flask terminal output for backend errors

## License

See project documentation for license information.

## Version

Package created: 2026-01-31
Includes all features from 5-phase protocol enhancement implementation.
