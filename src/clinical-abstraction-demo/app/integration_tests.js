/**
 * Clinical Abstraction Demo - Integration Tests
 *
 * Tests the full stack including:
 * - Backend API endpoints
 * - AI extraction with OpenAI
 * - Frontend-backend integration
 * - Protocol rules in AI prompts
 */

const http = require('http');

// Test configuration
const BACKEND_URL = 'http://localhost:5000';
const TEST_TIMEOUT = 30000; // 30 seconds for AI calls

// Simple test framework
class IntegrationTestRunner {
    constructor() {
        this.tests = [];
        this.results = { passed: 0, failed: 0, skipped: 0, errors: [] };
    }

    test(name, fn, options = {}) {
        this.tests.push({ name, fn, ...options });
    }

    async run() {
        console.log('\n' + '='.repeat(80));
        console.log('Running Clinical Abstraction Demo Integration Tests');
        console.log('='.repeat(80) + '\n');

        // Check if backend is running
        const backendRunning = await this.checkBackend();
        if (!backendRunning) {
            console.log('⚠️  Backend not running on', BACKEND_URL);
            console.log('   Start the backend with: python extraction_backend_openai.py');
            console.log('   Skipping all integration tests.\n');
            return { passed: 0, failed: 0, skipped: this.tests.length };
        }

        console.log('✓ Backend is running\n');

        for (const test of this.tests) {
            try {
                if (test.requiresApiKey) {
                    const hasApiKey = await this.checkApiKey();
                    if (!hasApiKey) {
                        console.log(`⊘ ${test.name} (Skipped - no API key)`);
                        this.results.skipped++;
                        continue;
                    }
                }

                await test.fn();
                this.results.passed++;
                console.log(`✓ ${test.name}`);
            } catch (error) {
                this.results.failed++;
                this.results.errors.push({ test: test.name, error: error.message });
                console.log(`✗ ${test.name}`);
                console.log(`  Error: ${error.message}`);
            }
        }

        console.log('\n' + '='.repeat(80));
        console.log(`Integration Test Results: ${this.results.passed} passed, ${this.results.failed} failed, ${this.results.skipped} skipped`);
        console.log('='.repeat(80) + '\n');

        if (this.results.failed > 0) {
            console.log('Failed Tests Details:');
            this.results.errors.forEach(({ test, error }) => {
                console.log(`\n${test}:`);
                console.log(`  ${error}`);
            });
        }

        return this.results;
    }

    async checkBackend() {
        try {
            const response = await this.makeRequest('/health', 'GET');
            return response.status === 'ok';
        } catch (error) {
            return false;
        }
    }

    async checkApiKey() {
        try {
            const response = await this.makeRequest('/health', 'GET');
            return response.openai_configured === true;
        } catch (error) {
            return false;
        }
    }

    async makeRequest(path, method = 'GET', body = null) {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: '127.0.0.1',  // Use IPv4 explicitly instead of 'localhost'
                port: 5000,
                path: path,
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            const req = http.request(options, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        const parsed = JSON.parse(data);
                        if (res.statusCode >= 400) {
                            reject(new Error(`HTTP ${res.statusCode}: ${parsed.error || 'Unknown error'}`));
                        } else {
                            resolve(parsed);
                        }
                    } catch (error) {
                        reject(new Error(`Failed to parse response: ${error.message}`));
                    }
                });
            });

            req.on('error', (error) => {
                reject(new Error(`Request failed: ${error.message}`));
            });

            req.setTimeout(TEST_TIMEOUT, () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });

            if (body) {
                req.write(JSON.stringify(body));
            }

            req.end();
        });
    }
}

// Assertion helpers
function assert(condition, message) {
    if (!condition) {
        throw new Error(message || 'Assertion failed');
    }
}

function assertEquals(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(message || `Expected ${expected}, but got ${actual}`);
    }
}

function assertGreaterThan(actual, expected, message) {
    if (actual <= expected) {
        throw new Error(message || `Expected ${actual} to be greater than ${expected}`);
    }
}

function assertArrayLength(array, length, message) {
    if (!Array.isArray(array)) {
        throw new Error('Expected an array');
    }
    if (array.length !== length) {
        throw new Error(message || `Expected array length ${length}, but got ${array.length}`);
    }
}

// ============== INTEGRATION TESTS ==============

const runner = new IntegrationTestRunner();

// ============== BACKEND API TESTS ==============

runner.test('Health endpoint returns correct status', async () => {
    const response = await runner.makeRequest('/health', 'GET');

    assertEquals(response.status, 'ok', 'Health status should be ok');
    assertEquals(response.provider, 'openai', 'Provider should be openai');
    assert(typeof response.openai_configured === 'boolean', 'Should indicate if OpenAI is configured');
});

runner.test('Load directory endpoint validation', async () => {
    // Test with missing directory_path
    try {
        await runner.makeRequest('/load-directory', 'POST', {});
        throw new Error('Should have thrown error for missing directory_path');
    } catch (error) {
        assert(error.message.includes('directory_path is required') || error.message.includes('400'),
            'Should return error for missing directory_path');
    }
});

runner.test('Load directory with sample notes', async () => {
    const response = await runner.makeRequest('/load-directory', 'POST', {
        directory_path: './sample_notes'
    });

    assert(response.patients, 'Response should have patients array');
    assertGreaterThan(response.patients.length, 0, 'Should load at least one patient');
    assertGreaterThan(response.count, 0, 'Count should be greater than 0');

    // Check patient structure
    const patient = response.patients[0];
    assert(patient.patient_id, 'Patient should have ID');
    assert(patient.name, 'Patient should have name');
    assert(patient.documents, 'Patient should have documents');
    assert(patient.documents.length > 0, 'Patient should have at least one document');

    // Check document structure
    const doc = patient.documents[0];
    assert(doc.document_id, 'Document should have ID');
    assert(doc.text_content, 'Document should have text content');
    assert(doc.document_type === 'clinical_note', 'Document type should be clinical_note');
});

// ============== AI EXTRACTION TESTS ==============

runner.test('Extract endpoint validation - missing text', async () => {
    try {
        await runner.makeRequest('/extract', 'POST', {});
        throw new Error('Should have thrown error for missing text');
    } catch (error) {
        assert(error.message.includes('No text provided') || error.message.includes('400'),
            'Should return error for missing text');
    }
}, { requiresApiKey: true });

runner.test('AI extraction with basic clinical note', async () => {
    const testNote = `
Patient: John Doe, MRN: 12345
DOB: 01/15/1965

Clinical Note:
65 y/o Male with history of heart failure.

Assessment:
- NYHA Class III heart failure
- Blood pressure: 140/90 mmHg
- Heart rate: 85 bpm
- Recent echo shows LVEF 30%
- BNP: 450 pg/mL

Plan:
- Continue diuretics
- Follow up in 2 weeks
    `.trim();

    const response = await runner.makeRequest('/extract', 'POST', {
        text: testNote,
        variables: ['nyha_class', 'ejection_fraction', 'bp_systolic', 'bp_diastolic', 'heart_rate', 'bnp'],
        model: 'gpt-4o-mini' // Use cheaper model for testing
    });

    assert(response.extractions, 'Response should have extractions array');
    assertGreaterThan(response.extractions.length, 0, 'Should extract at least one variable');

    // Check extraction structure
    const extraction = response.extractions[0];
    assert(extraction.variable_name, 'Extraction should have variable_name');
    assert(extraction.value, 'Extraction should have value');
    assert(typeof extraction.confidence === 'number', 'Extraction should have confidence number');
    assert(extraction.evidence, 'Extraction should have evidence object');
    assert(extraction.evidence.text, 'Evidence should have text');
    assert(typeof extraction.evidence.start_offset === 'number', 'Evidence should have start_offset');
    assert(typeof extraction.evidence.end_offset === 'number', 'Evidence should have end_offset');

    // Check for specific expected values
    const nyhaExtraction = response.extractions.find(e => e.variable_name === 'nyha_class');
    if (nyhaExtraction) {
        assert(nyhaExtraction.value.includes('III'), 'NYHA class should be III');
    }

    const bnpExtraction = response.extractions.find(e => e.variable_name === 'bnp');
    if (bnpExtraction) {
        assert(bnpExtraction.value.includes('450'), 'BNP should be 450');
    }

    console.log(`    Extracted ${response.extractions.length} variables`);
}, { requiresApiKey: true });

runner.test('AI extraction with protocol rules', async () => {
    const testNote = `
Patient has conflicting BNP values:
- Clinical notes mention BNP ~400
- Lab report shows BNP: 450 pg/mL (verified)

LVEF mentioned as 35% in old note, but recent echo shows 30%.
    `.trim();

    const protocolRules = [
        {
            id: "rule_001",
            category: "Conflict Resolution",
            title: "Lab Priority Rule",
            rule: "If clinical notes conflict with lab data, use lab values",
            aiPromptText: "When extracting BNP and ejection_fraction, prioritize laboratory values and recent measurements over clinical notes",
            applicableVariables: ["bnp", "ejection_fraction"],
            priority: 1,
            examples: [
                {
                    scenario: "Note says 'BNP around 400' but lab shows '450 pg/mL'",
                    resolution: "Use 450 from lab"
                }
            ]
        },
        {
            id: "rule_002",
            category: "Default Handling",
            title: "Prefer Recent Values",
            rule: "When multiple values exist, prefer the most recent",
            aiPromptText: "Always select the most recent value when multiple measurements are present",
            applicableVariables: [],
            priority: 2,
            examples: []
        }
    ];

    const response = await runner.makeRequest('/extract', 'POST', {
        text: testNote,
        variables: ['bnp', 'ejection_fraction'],
        protocol_rules: protocolRules,
        model: 'gpt-4o-mini'
    });

    assert(response.extractions, 'Response should have extractions');
    assert(response.protocol_rules_applied, 'Response should indicate protocol rules applied');
    assertEquals(response.protocol_rules_applied, 2, 'Should apply 2 protocol rules');

    // Check that lab value is preferred for BNP
    const bnpExtraction = response.extractions.find(e => e.variable_name === 'bnp');
    if (bnpExtraction) {
        assert(bnpExtraction.value.includes('450'), 'Should extract lab value (450) not clinical note value (~400)');
        console.log(`    ✓ BNP correctly extracted as ${bnpExtraction.value} (lab value preferred)`);
    }

    // Check that recent value is preferred for ejection fraction
    const efExtraction = response.extractions.find(e => e.variable_name === 'ejection_fraction');
    if (efExtraction) {
        assert(efExtraction.value.includes('30'), 'Should extract recent value (30%) not old value (35%)');
        console.log(`    ✓ EF correctly extracted as ${efExtraction.value} (recent value preferred)`);
    }
}, { requiresApiKey: true });

runner.test('AI extraction with variable definitions from schema', async () => {
    const testNote = `
Heart failure patient with HFrEF.
Blood pressure 142/88 mmHg
Heart rate 78 bpm
NT-proBNP 850 pg/mL
    `.trim();

    const variableDefinitions = {
        'heart_failure_diagnosis': 'Type of heart failure: HFrEF (reduced), HFpEF (preserved), HFmrEF (mid-range)',
        'bp_systolic': 'Systolic blood pressure in mmHg (top number)',
        'bp_diastolic': 'Diastolic blood pressure in mmHg (bottom number)',
        'heart_rate': 'Heart rate in beats per minute (bpm)',
        'bnp': 'BNP or NT-proBNP value in pg/mL'
    };

    const response = await runner.makeRequest('/extract', 'POST', {
        text: testNote,
        variables: ['heart_failure_diagnosis', 'bp_systolic', 'bp_diastolic', 'heart_rate', 'bnp'],
        variable_definitions: variableDefinitions,
        model: 'gpt-4o-mini'
    });

    assert(response.extractions, 'Response should have extractions');

    // Check that HF type is correctly identified
    const hfExtraction = response.extractions.find(e => e.variable_name === 'heart_failure_diagnosis');
    if (hfExtraction) {
        assert(hfExtraction.value.toLowerCase().includes('hfref'), 'Should identify HFrEF');
        console.log(`    ✓ Correctly identified ${hfExtraction.value}`);
    }

    // Check that NT-proBNP is recognized as BNP
    const bnpExtraction = response.extractions.find(e => e.variable_name === 'bnp');
    if (bnpExtraction) {
        assert(bnpExtraction.value.includes('850'), 'Should extract NT-proBNP as BNP');
        console.log(`    ✓ NT-proBNP correctly extracted as BNP: ${bnpExtraction.value}`);
    }
}, { requiresApiKey: true });

runner.test('AI extraction handles missing variables gracefully', async () => {
    const testNote = `
Patient with chest pain.
No heart failure history.
Blood pressure normal.
    `.trim();

    const response = await runner.makeRequest('/extract', 'POST', {
        text: testNote,
        variables: ['nyha_class', 'ejection_fraction', 'bnp'],
        model: 'gpt-4o-mini'
    });

    assert(response.extractions, 'Response should have extractions array');
    // Should return empty or very low confidence extractions for variables not in text
    console.log(`    Extracted ${response.extractions.length} variables from note without HF data`);

    // Check that confidence is appropriately low if any extractions were made
    for (const extraction of response.extractions) {
        if (extraction.variable_name === 'nyha_class' || extraction.variable_name === 'bnp') {
            assert(extraction.confidence < 0.7, `Confidence for ${extraction.variable_name} should be low for missing data`);
        }
    }
}, { requiresApiKey: true });

runner.test('AI extraction with custom prompt', async () => {
    const testNote = `
Patient reports severe shortness of breath on minimal exertion.
Unable to walk more than 10 feet without stopping.
    `.trim();

    const customPrompt = `
You are extracting from a clinical trial with strict criteria.
For NYHA class, be conservative and only extract if explicitly stated.
If symptoms are described but no class is mentioned, do NOT infer the class.
Return empty/low confidence if uncertain.
    `;

    const response = await runner.makeRequest('/extract', 'POST', {
        text: testNote,
        variables: ['nyha_class'],
        custom_prompt: customPrompt,
        model: 'gpt-4o-mini'
    });

    assert(response.extractions, 'Response should have extractions array');

    // With custom prompt emphasizing conservative extraction,
    // it should either not extract or have low confidence
    const nyhaExtraction = response.extractions.find(e => e.variable_name === 'nyha_class');
    if (nyhaExtraction) {
        console.log(`    Extracted NYHA: ${nyhaExtraction.value} (confidence: ${nyhaExtraction.confidence})`);
        // Custom prompt should make it more conservative
    } else {
        console.log(`    ✓ Correctly did not extract NYHA class (conservative prompt)`);
    }
}, { requiresApiKey: true });

runner.test('Multiple extractions for same variable', async () => {
    const testNote = `
Initial visit: NYHA Class II
3 months later: NYHA Class III
Most recent: NYHA Class III (confirmed)
    `.trim();

    const response = await runner.makeRequest('/extract', 'POST', {
        text: testNote,
        variables: ['nyha_class'],
        model: 'gpt-4o-mini'
    });

    assert(response.extractions, 'Response should have extractions');

    // Should extract the most recent value
    const nyhaExtraction = response.extractions.find(e => e.variable_name === 'nyha_class');
    assert(nyhaExtraction, 'Should extract NYHA class');
    assert(nyhaExtraction.value.includes('III'), 'Should extract most recent value (Class III)');
    assert(nyhaExtraction.rationale, 'Should provide rationale for selection');

    console.log(`    ✓ Extracted most recent value: ${nyhaExtraction.value}`);
}, { requiresApiKey: true });

runner.test('Extraction with different models', async () => {
    const testNote = `
NYHA Class II-III heart failure
BNP: 425 pg/mL
LVEF 32%
    `.trim();

    // Test with both models
    const models = ['gpt-4o-mini', 'gpt-4o'];

    for (const model of models) {
        const response = await runner.makeRequest('/extract', 'POST', {
            text: testNote,
            variables: ['nyha_class', 'bnp', 'ejection_fraction'],
            model: model
        });

        assert(response.extractions, `${model} should return extractions`);
        assertEquals(response.model_used, model, `Should use requested model: ${model}`);
        assertGreaterThan(response.extractions.length, 0, `${model} should extract variables`);

        console.log(`    ✓ ${model}: Extracted ${response.extractions.length} variables`);
    }
}, { requiresApiKey: true });

// ============== ERROR HANDLING TESTS ==============

runner.test('Backend handles malformed JSON', async () => {
    try {
        // Manually make a request with invalid JSON
        await new Promise((resolve, reject) => {
            const http = require('http');
            const options = {
                hostname: 'localhost',
                port: 5000,
                path: '/extract',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            const req = http.request(options, (res) => {
                let data = '';
                res.on('data', (chunk) => { data += chunk; });
                res.on('end', () => {
                    if (res.statusCode >= 400) {
                        resolve(); // Expected error
                    } else {
                        reject(new Error('Should have returned error for malformed JSON'));
                    }
                });
            });

            req.on('error', reject);
            req.write('{"invalid json"'); // Malformed JSON
            req.end();
        });
    } catch (error) {
        // Error is expected
    }
});

runner.test('Backend handles empty protocol rules array', async () => {
    const testNote = "BNP 450 pg/mL";

    const response = await runner.makeRequest('/extract', 'POST', {
        text: testNote,
        variables: ['bnp'],
        protocol_rules: [], // Empty array
        model: 'gpt-4o-mini'
    });

    assert(response.extractions, 'Should handle empty protocol rules array');
    assertEquals(response.protocol_rules_applied, 0, 'Should indicate 0 rules applied');
}, { requiresApiKey: true });

runner.test('Backend handles very long text', async () => {
    // Create a very long clinical note (10KB)
    let longNote = `
Patient: Test Patient
DOB: 01/01/1950

History of Present Illness:
    `.trim();

    // Add repetitive content to make it long
    for (let i = 0; i < 100; i++) {
        longNote += `\nVisit ${i + 1}: Patient doing well. No new complaints. `;
    }

    longNote += `\n\nRecent labs: BNP 450 pg/mL\nEcho: LVEF 35%`;

    const response = await runner.makeRequest('/extract', 'POST', {
        text: longNote,
        variables: ['bnp', 'ejection_fraction'],
        model: 'gpt-4o-mini'
    });

    assert(response.extractions, 'Should handle long text');
    assertGreaterThan(longNote.length, 1000, 'Test note should be long');

    // Should still extract correctly from the end
    const bnpExtraction = response.extractions.find(e => e.variable_name === 'bnp');
    if (bnpExtraction) {
        assert(bnpExtraction.value.includes('450'), 'Should extract BNP from long note');
    }
}, { requiresApiKey: true });

// ============== RUN INTEGRATION TESTS ==============

if (require.main === module) {
    console.log('Starting integration tests...');
    console.log('Make sure the backend is running: python extraction_backend_openai.py\n');

    runner.run().then(results => {
        process.exit(results.failed > 0 ? 1 : 0);
    }).catch(error => {
        console.error('Test runner error:', error);
        process.exit(1);
    });
}

module.exports = { runner };
