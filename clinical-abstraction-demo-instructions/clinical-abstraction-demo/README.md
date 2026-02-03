# Clinical Abstraction Demo - AI Extraction

This demo showcases real-time AI extraction of clinical variables from medical notes using OpenAI GPT-4.

## What's Included

- `index.html` - Web-based clinical abstraction workstation
- `extraction_backend_openai.py` - Flask API backend for OpenAI integration
- `requirements.txt` - Python dependencies
- `start_demo.sh` - Convenience script to start both servers
- `sample_notes/` - Sample clinical notes for testing
- `synthetic_data/` - Synthetic clinical note generator

## Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option B: In the Web UI**
- You can also enter your API key directly in the app's settings

### 3. Start the Demo

**Using the startup script (easiest):**
```bash
chmod +x start_demo.sh
./start_demo.sh
```

**Or manually:**

Terminal 1 - Start Flask Backend:
```bash
python extraction_backend_openai.py
```

Terminal 2 - Start Web Server:
```bash
python -m http.server 8000
```

### 4. Access the Application

Open your browser and navigate to:
- **Local:** `http://localhost:8000/` or `http://localhost:8000/index.html`

## How to Use

1. **Load Patient Data:**
   - Click "Load Sample Data" to see example patients
   - Or load your own clinical notes (.txt files)

2. **Extract Variables:**
   - Select a patient and document
   - Click "Extract with AI" to automatically extract clinical variables
   - Review the extracted values and their evidence

3. **Supported Variables:**
   - NYHA Functional Class
   - Ejection Fraction (LVEF)
   - Blood Pressure (Systolic/Diastolic)
   - Heart Rate
   - Heart Failure Diagnosis Type
   - BNP/NT-proBNP

4. **Model Selection:**
   - `gpt-4o` - Best quality, recommended
   - `gpt-4o-mini` - Faster, more cost-effective

## API Endpoints

### Flask Backend (Port 5000)

- `GET /health` - Health check and configuration status
- `POST /extract` - Extract clinical variables from text
- `POST /load-directory` - Load .txt files from a directory

### Example API Request

```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient has NYHA Class III heart failure with LVEF of 30%.",
    "api_key": "your-api-key",
    "model": "gpt-4o",
    "variables": ["nyha_class", "ejection_fraction"]
  }'
```

## Troubleshooting

### Port Already in Use
If port 5000 or 8000 is already in use:
```bash
# Find and kill process using the port
lsof -ti:5000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### API Key Not Working
- Verify your API key is valid at https://platform.openai.com/api-keys
- Check that you have credits available in your OpenAI account
- Ensure the key starts with `sk-proj-` or `sk-`

### CORS Errors
If you see CORS errors in the browser console, ensure:
- The Flask backend is running on port 5000
- Flask-CORS is installed (`pip install flask-cors`)

## Architecture

```
┌─────────────────┐      HTTP      ┌──────────────────┐
│   Web Browser   │ ←────────────→ │   Flask Backend  │
│  (index.html)   │                │   (port 5000)    │
└─────────────────┘                └──────────────────┘
         ↑                                   ↓
         │                                   │
         │                          ┌────────────────┐
         └──────────────────────────│  OpenAI API    │
           Served via HTTP Server   │   (GPT-4)      │
              (port 8000)            └────────────────┘
```

## Customization

### Adding New Variables
Edit the `variable_descriptions` dictionary in `extraction_backend_openai.py`:

```python
variable_descriptions = {
    'your_variable': 'Description of what to extract',
    ...
}
```

### Custom Extraction Prompts
You can pass a custom prompt in the API request:

```json
{
  "text": "...",
  "custom_prompt": "Your custom extraction instructions here"
}
```

## Support

For issues or questions:
- Check the Flask backend logs for error messages
- Verify your OpenAI API key has sufficient credits
- Ensure all dependencies are installed correctly

## License

This is a demonstration application for educational purposes.
