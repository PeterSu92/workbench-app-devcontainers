"""
Clinical Abstraction - OpenAI API Backend
Provides real-time AI extraction of clinical variables from medical notes using OpenAI GPT-4.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import json
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize OpenAI client
client = None

def init_openai_client(api_key=None):
    """Initialize the OpenAI client with API key."""
    global client
    if api_key:
        client = OpenAI(api_key=api_key)
    elif os.getenv('OPENAI_API_KEY'):
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    else:
        client = None
    return client is not None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'openai_configured': client is not None,
        'provider': 'openai'
    })

@app.route('/extract', methods=['POST'])
def extract_variables():
    """
    Extract clinical variables from a medical note using OpenAI GPT-4.

    Request body:
    {
        "text": "clinical note text...",
        "api_key": "optional API key if not set in environment",
        "variables": ["nyha_class", "ejection_fraction", ...],
        "model": "gpt-4o" (optional, default) or "gpt-4o-mini",
        "custom_prompt": "optional custom extraction instructions"
    }

    Response:
    {
        "extractions": [
            {
                "variable_name": "nyha_class",
                "value": "III",
                "value_type": "categorical",
                "confidence": 0.95,
                "evidence": {
                    "text": "NYHA Class III",
                    "start_offset": 123,
                    "end_offset": 137
                },
                "rationale": "Found explicit mention..."
            },
            ...
        ]
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        api_key = data.get('api_key')
        variables = data.get('variables', [
            'nyha_class', 'ejection_fraction', 'bp_systolic', 'bp_diastolic',
            'heart_rate', 'heart_failure_diagnosis', 'bnp'
        ])
        model = data.get('model', 'gpt-4o')
        custom_prompt = data.get('custom_prompt', None)  # Get custom prompt from settings

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Initialize client if API key provided
        if api_key:
            init_openai_client(api_key)

        if not client:
            return jsonify({
                'error': 'OpenAI API not configured. Please provide API key or set OPENAI_API_KEY environment variable.'
            }), 401

        # Create extraction prompt (use custom if provided)
        prompt = create_extraction_prompt(text, variables, custom_prompt)

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a clinical data extraction specialist. Extract variables from medical notes with high accuracy."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent extractions
            response_format={"type": "json_object"}
        )

        # Parse OpenAI's response
        response_text = response.choices[0].message.content
        extractions = parse_openai_response(response_text, text)

        return jsonify({
            'extractions': extractions,
            'model_used': model
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_extraction_prompt(text, variables, custom_prompt=None):
    """Create a structured prompt for OpenAI to extract variables."""

    variable_descriptions = {
        'nyha_class': 'NYHA Functional Class (I, II, III, or IV) - indicates heart failure severity',
        'ejection_fraction': 'Left ventricular ejection fraction (LVEF) as a percentage (e.g., 30, 35, 40)',
        'bp_systolic': 'Systolic blood pressure in mmHg',
        'bp_diastolic': 'Diastolic blood pressure in mmHg',
        'heart_rate': 'Heart rate in beats per minute',
        'heart_failure_diagnosis': 'Type of heart failure (HFrEF, HFpEF, HFmrEF, or general CHF)',
        'bnp': 'BNP or NT-proBNP value (pg/mL)'
    }

    var_list = '\n'.join([f"- {var}: {variable_descriptions.get(var, 'Clinical variable')}"
                          for var in variables])

    # Use custom prompt if provided, otherwise use default instructions
    if custom_prompt:
        instructions = custom_prompt
    else:
        instructions = """**IMPORTANT INSTRUCTIONS:**
1. For each variable found, provide:
   - The exact value extracted
   - The exact text span from the document (quote the relevant phrase)
   - Your confidence level (0.0 to 1.0)
   - Brief rationale for the extraction

2. Only extract values that are explicitly stated in the note
3. If a variable appears multiple times, extract the most clinically relevant instance (usually the most recent)
4. For LVEF/ejection fraction, prefer the most recent value mentioned"""

    return f"""Extract the following clinical variables from this medical note.

{instructions}

**Variables to extract:**
{var_list}

**Output format - Return a JSON object with this structure:**
{{
  "extractions": [
    {{
      "variable_name": "nyha_class",
      "value": "III",
      "confidence": 0.95,
      "evidence_text": "NYHA Class III",
      "rationale": "Explicitly stated NYHA functional class"
    }}
  ]
}}

**Clinical Note:**
{text}

Extract the variables now, returning ONLY the JSON object:"""

def parse_openai_response(response_text, original_text):
    """Parse OpenAI's JSON response and add text offsets."""

    try:
        data = json.loads(response_text)
        extractions_list = data.get('extractions', [])
    except json.JSONDecodeError:
        return []

    # Add offsets and format for demo
    result = []
    for ext in extractions_list:
        evidence_text = ext.get('evidence_text', '')

        # Find the text in the original document with fuzzy matching
        start_offset, end_offset = find_text_offset(original_text, evidence_text)

        # Determine value type
        value = str(ext.get('value', ''))
        value_type = determine_value_type(ext.get('variable_name', ''), value)

        result.append({
            'variable_name': ext.get('variable_name', ''),
            'value': value,
            'value_type': value_type,
            'confidence': ext.get('confidence', 0.8),
            'evidence': {
                'text': evidence_text,
                'start_offset': start_offset,
                'end_offset': end_offset
            },
            'rationale': ext.get('rationale', '')
        })

    return result

def find_text_offset(original_text, evidence_text):
    """
    Find the offset of evidence text in the original document.
    Uses multiple strategies for robust matching.
    """
    if not evidence_text:
        return -1, -1

    import re

    # Strategy 1: Exact match
    start = original_text.find(evidence_text)
    if start >= 0:
        return start, start + len(evidence_text)

    # Strategy 2: Case-insensitive match
    start = original_text.lower().find(evidence_text.lower())
    if start >= 0:
        return start, start + len(evidence_text)

    # Strategy 3: Try with stripped/normalized evidence
    # Remove extra spaces and try to find in original
    evidence_stripped = evidence_text.strip()
    if evidence_stripped != evidence_text:
        start = original_text.lower().find(evidence_stripped.lower())
        if start >= 0:
            return start, start + len(evidence_stripped)

    # Strategy 4: Find key phrases (try progressively shorter segments)
    words = evidence_text.split()
    if len(words) >= 2:
        # Try phrases from full length down to 2 words
        for length in range(len(words), 1, -1):
            phrase = ' '.join(words[:length])
            start = original_text.lower().find(phrase.lower())
            if start >= 0:
                return start, start + len(phrase)

    # Strategy 5: Find first significant word as fallback
    significant_words = [w for w in words if len(w) > 3]
    if significant_words:
        word = significant_words[0]
        start = original_text.lower().find(word.lower())
        if start >= 0:
            # Use just this word as the highlight
            return start, start + len(word)

    # No match found
    return -1, -1

def determine_value_type(variable_name, value):
    """Determine the type of a variable value."""
    categorical_vars = ['nyha_class', 'heart_failure_diagnosis']

    if variable_name in categorical_vars:
        return 'categorical'

    # Try to parse as number
    try:
        float(value.replace('%', '').replace(',', ''))
        return 'numeric'
    except ValueError:
        return 'text'

@app.route('/load-directory', methods=['POST'])
def load_directory():
    """
    Load all .txt files from a specified directory on the server.

    Request body:
    {
        "directory_path": "/path/to/clinical/notes"
    }
    """
    try:
        from pathlib import Path
        import uuid
        from datetime import datetime

        data = request.json
        directory_path = data.get('directory_path', '')

        if not directory_path:
            return jsonify({'error': 'directory_path is required'}), 400

        dir_path = Path(directory_path)

        if not dir_path.exists() or not dir_path.is_dir():
            return jsonify({'error': f'Directory not found: {directory_path}'}), 404

        # Find all .txt files
        txt_files = list(dir_path.glob('*.txt'))

        if not txt_files:
            return jsonify({'error': 'No .txt files found in directory'}), 404

        patients = []

        for txt_file in txt_files:
            text = txt_file.read_text()

            # Extract patient info from filename or content
            patient_info = extract_patient_info_from_text(txt_file.name, text)

            patient = {
                'patient_id': f'pat-{uuid.uuid4().hex[:8]}',
                'name': patient_info.get('name', 'Unknown Patient'),
                'birth_date': patient_info.get('dob', '1950-01-01'),
                'gender': patient_info.get('gender', 'unknown'),
                'mrn': patient_info.get('mrn', f'MRN{uuid.uuid4().hex[:6]}'),
                'documents': [{
                    'document_id': f'doc-{uuid.uuid4().hex[:8]}',
                    'patient_id': f'pat-{uuid.uuid4().hex[:8]}',
                    'document_type': 'clinical_note',
                    'document_subtype': detect_document_type_from_text(text),
                    'document_date': patient_info.get('visit_date', datetime.now().isoformat()),
                    'text_content': text,
                    'ground_truth': []
                }]
            }

            patients.append(patient)

        return jsonify({
            'patients': patients,
            'count': len(patients)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_patient_info_from_text(filename, text):
    """Extract patient information from text content."""
    import re

    info = {}

    # Extract MRN
    mrn_match = re.search(r'MRN:?\s*(\d+)', text, re.IGNORECASE)
    if mrn_match:
        info['mrn'] = mrn_match.group(1)

    # Extract patient name
    name_match = re.search(r'(?:Pt:|Patient:?)\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)', text)
    if name_match:
        info['name'] = name_match.group(1)
    else:
        # Try from filename
        name_from_file = filename.replace('.txt', '').replace('_', ' ').title()
        info['name'] = name_from_file

    # Extract DOB
    dob_match = re.search(r'DOB:?\s*(\d{1,2}\/\d{1,2}\/\d{4})', text, re.IGNORECASE)
    if dob_match:
        parts = dob_match.group(1).split('/')
        info['dob'] = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    # Extract gender
    gender_match = re.search(r'\b\d+\s*y\/o\s+(M|F|Male|Female)\b', text, re.IGNORECASE)
    if gender_match:
        info['gender'] = 'male' if gender_match.group(1).lower().startswith('m') else 'female'

    # Extract visit date
    visit_match = re.search(r'Visit Date:?\s*(\d{1,2}\/\d{1,2}\/\d{4})', text, re.IGNORECASE)
    if visit_match:
        parts = visit_match.group(1).split('/')
        info['visit_date'] = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}T00:00:00"

    return info

def detect_document_type_from_text(text):
    """Detect document type from content."""
    text_lower = text.lower()

    if 'cardiology' in text_lower or 'nyha' in text_lower or 'ejection fraction' in text_lower:
        return 'cardiology_note'
    if 'oncology' in text_lower or 'cancer' in text_lower:
        return 'oncology_note'
    if 'echo' in text_lower or 'echocardiogram' in text_lower:
        return 'echo_report'
    if 'pathology' in text_lower or 'biopsy' in text_lower:
        return 'pathology_report'
    if 'discharge' in text_lower:
        return 'discharge_summary'
    if 'lab' in text_lower:
        return 'lab_report'

    return 'progress_note'

if __name__ == '__main__':
    # Check for API key in environment
    if os.getenv('OPENAI_API_KEY'):
        init_openai_client()
        print("✓ OpenAI API configured from OPENAI_API_KEY environment variable")
    else:
        print("⚠ OPENAI_API_KEY not found. API key must be provided in requests.")

    print("\n" + "="*60)
    print("Clinical Abstraction Backend - OpenAI Version")
    print("="*60)
    print("Server: http://localhost:5000")
    print("Health: http://localhost:5000/health")
    print("\nEndpoints:")
    print("  POST /extract - Extract variables from clinical note")
    print("  POST /load-directory - Load .txt files from directory")
    print("\nSupported models:")
    print("  - gpt-4o (recommended, best quality)")
    print("  - gpt-4o-mini (faster, cheaper)")
    print("  - gpt-4-turbo")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
