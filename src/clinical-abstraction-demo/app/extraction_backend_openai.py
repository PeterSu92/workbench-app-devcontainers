"""
Clinical Abstraction - OpenAI API Backend
Provides real-time AI extraction of clinical variables from medical notes using OpenAI GPT-4.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import json
import logging
from datetime import datetime
from openai import OpenAI
from openai import APIError, RateLimitError, APIConnectionError

# Optional imports for enhanced features
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("tiktoken not available - using token estimation fallback")

try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("tenacity not available - retry logic disabled")
    # Create no-op decorator if tenacity not available
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Serve static files from the same directory as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, static_url_path='/static')

# Enable CORS with specific configuration for Workbench
CORS(app)

@app.route('/')
def serve_index():
    """Serve the main web UI."""
    return app.send_static_file('index.html')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = None

# Token limits for smart truncation
MAX_NOTE_TOKENS = 5000  # Maximum tokens for clinical note section
MAX_TOTAL_TOKENS = 10000  # Maximum total tokens for entire prompt

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

def count_tokens(text, model="gpt-4"):
    """Count tokens in text using tiktoken (or estimation if unavailable)."""
    if TIKTOKEN_AVAILABLE:
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed, using estimation: {e}")

    # Fallback to estimation (~4 chars per token)
    return len(text) // 4

def truncate_clinical_note(text, max_tokens=MAX_NOTE_TOKENS, model="gpt-4"):
    """
    Smart truncation of clinical notes to fit within token budget.

    Strategy:
    1. Try to identify key sections (History, Assessment, Plan)
    2. Keep sections with likely variable mentions
    3. Summarize or remove boilerplate sections
    4. Preserve beginning and end of note
    """
    current_tokens = count_tokens(text, model)

    if current_tokens <= max_tokens:
        return text, current_tokens, False  # No truncation needed

    logger.info(f"Note has {current_tokens} tokens, truncating to {max_tokens}")

    # Strategy 1: Split by common section headers and prioritize
    section_patterns = [
        (r'(?i)(chief complaint|cc):', 'Chief Complaint'),
        (r'(?i)(history of present illness|hpi):', 'HPI'),
        (r'(?i)(past medical history|pmh):', 'PMH'),
        (r'(?i)(assessment|impression):', 'Assessment'),
        (r'(?i)(plan):', 'Plan'),
        (r'(?i)(physical exam|examination):', 'Physical Exam'),
        (r'(?i)(labs?|laboratory):', 'Labs'),
    ]

    sections = []
    last_end = 0

    for pattern, name in section_patterns:
        match = re.search(pattern, text)
        if match:
            sections.append({
                'name': name,
                'start': match.start(),
                'priority': 1 if name in ['Assessment', 'Plan', 'Labs'] else 2
            })

    # If we found sections, extract high-priority ones
    if sections:
        sections.sort(key=lambda x: x['start'])

        # Build truncated note with high-priority sections
        truncated = text[:min(500, len(text))]  # Keep first 500 chars (context)

        high_priority_sections = [s for s in sections if s['priority'] == 1]
        for section in high_priority_sections:
            next_section = next((s for s in sections if s['start'] > section['start']), None)
            end = next_section['start'] if next_section else len(text)
            section_text = text[section['start']:end]

            if count_tokens(truncated + section_text, model) <= max_tokens:
                truncated += "\n\n" + section_text
            else:
                break

        # Add final portion if space allows
        final_portion = text[-500:]
        if count_tokens(truncated + final_portion, model) <= max_tokens:
            truncated += "\n\n[...]\n\n" + final_portion

        return truncated, count_tokens(truncated, model), True

    # Strategy 2: Simple head + tail truncation if no sections found
    # Keep first 60% and last 40% of available token budget
    head_tokens = int(max_tokens * 0.6)
    tail_tokens = int(max_tokens * 0.4)

    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    head = encoding.decode(tokens[:head_tokens])
    tail = encoding.decode(tokens[-tail_tokens:])

    truncated = head + "\n\n[... middle section truncated ...]\n\n" + tail

    return truncated, count_tokens(truncated, model), True

if TENACITY_AVAILABLE:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
        reraise=True
    )
    def call_openai_with_retry(client, model, messages, temperature, response_format):
        """Call OpenAI API with automatic retry on rate limits and connection errors."""
        logger.info(f"Calling OpenAI API with model: {model}")
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format
        )
else:
    def call_openai_with_retry(client, model, messages, temperature, response_format):
        """Call OpenAI API without retry (tenacity not available)."""
        logger.info(f"Calling OpenAI API with model: {model} (no retry)")
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format
        )

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
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"[{request_id}] Extraction request started")

    try:
        data = request.json
        text = data.get('text', '')
        api_key = data.get('api_key')
        variables = data.get('variables', [
            'nyha_class', 'ejection_fraction', 'bp_systolic', 'bp_diastolic',
            'heart_rate', 'heart_failure_diagnosis', 'bnp'
        ])
        variable_definitions = data.get('variable_definitions', None)
        protocol_rules = data.get('protocol_rules', None)
        model = data.get('model', 'gpt-4o')
        custom_prompt = data.get('custom_prompt', None)
        temperature = data.get('temperature', 0.1)  # Default 0.1 for deterministic extraction
        prompt_mode = data.get('prompt_mode', 'replace')  # 'replace', 'prepend', or 'append'

        if not text:
            logger.warning(f"[{request_id}] No text provided")
            return jsonify({'error': 'No text provided'}), 400

        # Initialize client if API key provided
        if api_key:
            init_openai_client(api_key)

        if not client:
            logger.error(f"[{request_id}] OpenAI client not configured")
            return jsonify({
                'error': 'OpenAI API not configured. Please provide API key or set OPENAI_API_KEY environment variable.'
            }), 401

        # Token counting and truncation
        original_note_tokens = count_tokens(text, model)
        logger.info(f"[{request_id}] Original note: {original_note_tokens} tokens")

        truncated_text = text
        was_truncated = False

        if original_note_tokens > MAX_NOTE_TOKENS:
            truncated_text, final_tokens, was_truncated = truncate_clinical_note(text, MAX_NOTE_TOKENS, model)
            logger.warning(f"[{request_id}] Note truncated: {original_note_tokens} → {final_tokens} tokens")

        # Create extraction prompt with prompt_mode support
        prompt = create_extraction_prompt(truncated_text, variables, custom_prompt, variable_definitions, protocol_rules, prompt_mode)

        # Count total prompt tokens
        system_message = "You are a clinical data extraction specialist. Extract variables from medical notes with high accuracy. Follow all provided abstraction protocol rules carefully."
        total_input_tokens = count_tokens(system_message + prompt, model)
        logger.info(f"[{request_id}] Total prompt tokens: {total_input_tokens}")

        # Log prompt for debugging (first 500 chars)
        logger.debug(f"[{request_id}] Prompt preview: {prompt[:500]}...")

        # Call OpenAI API with retry logic
        try:
            response = call_openai_with_retry(
                client=client,
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )

            # Count output tokens
            output_tokens = count_tokens(response.choices[0].message.content, model)
            logger.info(f"[{request_id}] Output tokens: {output_tokens}")
            logger.info(f"[{request_id}] Total tokens: {total_input_tokens + output_tokens}")

            # Parse OpenAI's response
            response_text = response.choices[0].message.content
            extractions = parse_openai_response(response_text, text if not was_truncated else truncated_text)

            logger.info(f"[{request_id}] Extraction successful: {len(extractions)} variables extracted")

            return jsonify({
                'extractions': extractions,
                'model_used': model,
                'protocol_rules_applied': len(protocol_rules) if protocol_rules else 0,
                'token_usage': {
                    'input_tokens': total_input_tokens,
                    'output_tokens': output_tokens,
                    'total_tokens': total_input_tokens + output_tokens,
                    'note_was_truncated': was_truncated,
                    'original_note_tokens': original_note_tokens
                }
            })

        except RateLimitError as e:
            logger.error(f"[{request_id}] Rate limit exceeded: {e}")
            return jsonify({
                'error': 'Rate limit exceeded. Please try again in a few moments.',
                'error_type': 'rate_limit',
                'retry_after': 60
            }), 429

        except APIConnectionError as e:
            logger.error(f"[{request_id}] API connection error: {e}")
            return jsonify({
                'error': 'Failed to connect to OpenAI API. Please check your internet connection and try again.',
                'error_type': 'connection_error'
            }), 503

        except APIError as e:
            logger.error(f"[{request_id}] OpenAI API error: {e}")
            return jsonify({
                'error': f'OpenAI API error: {str(e)}',
                'error_type': 'api_error'
            }), 500

    except json.JSONDecodeError as e:
        logger.error(f"[{request_id}] JSON decode error: {e}")
        return jsonify({
            'error': 'Invalid JSON in request body',
            'error_type': 'invalid_json'
        }), 400

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'error_type': 'unknown'
        }), 500

def create_extraction_prompt(text, variables, custom_prompt=None, variable_definitions=None, protocol_rules=None, prompt_mode='replace'):
    """Create a structured prompt for OpenAI to extract variables, including abstraction protocol rules.

    Args:
        text: Clinical note text
        variables: List of variable names to extract
        custom_prompt: Optional custom instructions
        variable_definitions: List of dicts with 'name' and 'description'
        protocol_rules: List of protocol rules to apply
        prompt_mode: How to handle custom_prompt - 'replace', 'prepend', or 'append' (default: 'replace')
    """

    # Default variable descriptions (fallback if schema doesn't provide them)
    default_descriptions = {
        'nyha_class': 'NYHA Functional Class (I, II, III, or IV) - indicates heart failure severity',
        'ejection_fraction': 'Left ventricular ejection fraction (LVEF) as a percentage (e.g., 30, 35, 40)',
        'bp_systolic': 'Systolic blood pressure in mmHg',
        'bp_diastolic': 'Diastolic blood pressure in mmHg',
        'heart_rate': 'Heart rate in beats per minute',
        'heart_failure_diagnosis': 'Type of heart failure (HFrEF, HFpEF, HFmrEF, or general CHF)',
        'bnp': 'BNP or NT-proBNP value (pg/mL)'
    }

    # Convert variable_definitions list to dict if provided, otherwise use defaults
    if variable_definitions:
        # variable_definitions is a list of dicts with 'name' and 'description' keys
        variable_descriptions = {var['name']: var['description'] for var in variable_definitions}
    else:
        variable_descriptions = default_descriptions

    var_list = '\n'.join([f"- {var}: {variable_descriptions.get(var, 'Clinical variable')}"
                          for var in variables])

    # Default instructions
    default_instructions = """**IMPORTANT INSTRUCTIONS:**
1. For each variable found, provide:
   - The exact value extracted
   - The exact text span from the document (quote the relevant phrase)
   - Your confidence level (0.0 to 1.0)
   - Brief rationale for the extraction

2. Only extract values that are explicitly stated in the note
3. If a variable appears multiple times, extract the most clinically relevant instance (usually the most recent)
4. For LVEF/ejection fraction, prefer the most recent value mentioned"""

    # Handle custom prompt with different modes
    if custom_prompt:
        if prompt_mode == 'prepend':
            instructions = custom_prompt + "\n\n" + default_instructions
        elif prompt_mode == 'append':
            instructions = default_instructions + "\n\n" + custom_prompt
        else:  # 'replace' (default for backward compatibility)
            instructions = custom_prompt
    else:
        instructions = default_instructions

    # Few-shot examples to guide AI behavior
    few_shot_examples = """
**EXAMPLE EXTRACTIONS:**

Example 1 - NYHA Class:
Note: "Patient with NYHA Class III symptoms, short of breath with minimal exertion."
Extraction:
{
  "variable_name": "nyha_class",
  "value": "III",
  "confidence": 0.98,
  "evidence_text": "NYHA Class III symptoms",
  "rationale": "Explicitly stated NYHA functional class"
}

Example 2 - Ejection Fraction:
Note: "Echo shows LVEF 35%. Previous echo from last month showed EF of 40%."
Extraction:
{
  "variable_name": "ejection_fraction",
  "value": "35",
  "confidence": 0.95,
  "evidence_text": "LVEF 35%",
  "rationale": "Most recent ejection fraction measurement from current echo"
}

Example 3 - Lab Value with Protocol:
Note: "Clinical notes suggest BNP around 500. Lab results show BNP: 612 pg/mL."
Extraction:
{
  "variable_name": "bnp",
  "value": "612",
  "confidence": 0.99,
  "evidence_text": "Lab results show BNP: 612 pg/mL",
  "rationale": "Used lab value over clinical estimate per protocol"
}
"""

    # Organize protocol rules hierarchically by category
    protocol_section = ""
    if protocol_rules and len(protocol_rules) > 0:
        protocol_section = "\n\n**ABSTRACTION PROTOCOL RULES - FOLLOW THESE CAREFULLY:**\n"
        protocol_section += "You must apply these clinical abstraction rules when extracting data:\n\n"

        # Group rules by category for better organization
        rules_by_category = {}
        for rule in protocol_rules:
            category = rule.get('category', 'General')
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(rule)

        # Priority order for categories
        category_order = ['Conflict Resolution', 'Data Source Priority', 'Default Handling',
                         'Quality Control', 'General']

        rule_num = 1
        for category in category_order:
            if category in rules_by_category:
                protocol_section += f"\n{category} Rules:\n"
                for rule in rules_by_category[category]:
                    protocol_section += f"{rule_num}. **{rule['title']}**\n"
                    protocol_section += f"   {rule['aiPromptText']}\n"

                    if rule.get('applicableVariables'):
                        protocol_section += f"   Applies to: {', '.join(rule['applicableVariables'])}\n"

                    if rule.get('examples') and len(rule['examples']) > 0:
                        ex = rule['examples'][0]
                        protocol_section += f"   Example: {ex.get('scenario')} → {ex.get('resolution')}\n"

                    protocol_section += "\n"
                    rule_num += 1

        # Add any remaining categories not in priority order
        for category, rules in rules_by_category.items():
            if category not in category_order:
                protocol_section += f"\n{category} Rules:\n"
                for rule in rules:
                    protocol_section += f"{rule_num}. **{rule['title']}**\n"
                    protocol_section += f"   {rule['aiPromptText']}\n"

                    if rule.get('applicableVariables'):
                        protocol_section += f"   Applies to: {', '.join(rule['applicableVariables'])}\n"

                    if rule.get('examples') and len(rule['examples']) > 0:
                        ex = rule['examples'][0]
                        protocol_section += f"   Example: {ex.get('scenario')} → {ex.get('resolution')}\n"

                    protocol_section += "\n"
                    rule_num += 1

    return f"""Extract the following clinical variables from this medical note.

{instructions}

**Variables to extract:**
{var_list}
{few_shot_examples}
{protocol_section}
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
    print("Clinical Abstraction Demo")
    print("="*60)
    print("Web UI:  http://localhost:8080/")
    print("Health:  http://localhost:8080/health")
    print("API:     http://localhost:8080/extract")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
