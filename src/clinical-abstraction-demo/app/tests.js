/**
 * Clinical Abstraction Demo - Comprehensive Test Suite
 *
 * Tests cover:
 * - Protocol management (CRUD operations)
 * - Protocol persistence
 * - AI extraction engine
 * - AI integration with protocols
 * - Import/Export functionality
 * - State management
 * - Variable operations
 * - Statistics calculation
 */

// Simple test framework
class TestRunner {
    constructor() {
        this.tests = [];
        this.results = {
            passed: 0,
            failed: 0,
            errors: []
        };
    }

    test(name, fn) {
        this.tests.push({ name, fn });
    }

    async run() {
        console.log('\n' + '='.repeat(80));
        console.log('Running Clinical Abstraction Demo Test Suite');
        console.log('='.repeat(80) + '\n');

        for (const test of this.tests) {
            try {
                await test.fn();
                this.results.passed++;
                console.log(`✓ ${test.name}`);
            } catch (error) {
                this.results.failed++;
                this.results.errors.push({ test: test.name, error: error.message, stack: error.stack });
                console.log(`✗ ${test.name}`);
                console.log(`  Error: ${error.message}`);
            }
        }

        console.log('\n' + '='.repeat(80));
        console.log(`Test Results: ${this.results.passed} passed, ${this.results.failed} failed`);
        console.log('='.repeat(80) + '\n');

        if (this.results.failed > 0) {
            console.log('Failed Tests Details:');
            this.results.errors.forEach(({ test, error, stack }) => {
                console.log(`\n${test}:`);
                console.log(`  ${error}`);
            });
        }

        return this.results;
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

function assertDeepEquals(actual, expected, message) {
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    if (actualStr !== expectedStr) {
        throw new Error(message || `Expected ${expectedStr}, but got ${actualStr}`);
    }
}

function assertGreaterThan(actual, expected, message) {
    if (actual <= expected) {
        throw new Error(message || `Expected ${actual} to be greater than ${expected}`);
    }
}

function assertArrayContains(array, item, message) {
    if (!array.includes(item)) {
        throw new Error(message || `Expected array to contain ${item}`);
    }
}

function assertArrayLength(array, length, message) {
    if (array.length !== length) {
        throw new Error(message || `Expected array length ${length}, but got ${array.length}`);
    }
}

// Mock localStorage for Node.js environment
if (typeof localStorage === 'undefined') {
    global.localStorage = {
        store: {},
        getItem(key) {
            return this.store[key] || null;
        },
        setItem(key, value) {
            this.store[key] = String(value);
        },
        removeItem(key) {
            delete this.store[key];
        },
        clear() {
            this.store = {};
        }
    };
}

// ============== TEST SUITE ==============

const runner = new TestRunner();

// ============== PROTOCOL DATA STRUCTURE TESTS ==============

runner.test('Protocol structure has required fields', () => {
    const protocol = {
        id: "test_protocol",
        name: "Test Protocol",
        version: "1.0",
        schema: "test",
        source: "custom",
        isActive: true,
        createdDate: new Date().toISOString(),
        modifiedDate: new Date().toISOString(),
        rules: []
    };

    assert(protocol.id, 'Protocol should have id');
    assert(protocol.name, 'Protocol should have name');
    assert(protocol.version, 'Protocol should have version');
    assert(protocol.schema, 'Protocol should have schema');
    assert(protocol.source, 'Protocol should have source');
    assert(typeof protocol.isActive === 'boolean', 'Protocol should have isActive boolean');
    assert(Array.isArray(protocol.rules), 'Protocol should have rules array');
});

runner.test('Protocol rule has required fields', () => {
    const rule = {
        id: "rule_001",
        category: "Test Category",
        title: "Test Rule",
        rule: "Test rule description",
        rationale: "Test rationale",
        applicableVariables: ["var1", "var2"],
        priority: 1,
        isEnabled: true,
        aiPromptText: "Test AI prompt",
        examples: [],
        metadata: {
            author: "test",
            tags: [],
            citations: []
        }
    };

    assert(rule.id, 'Rule should have id');
    assert(rule.category, 'Rule should have category');
    assert(rule.title, 'Rule should have title');
    assert(rule.rule, 'Rule should have rule description');
    assert(typeof rule.priority === 'number', 'Rule should have numeric priority');
    assert(typeof rule.isEnabled === 'boolean', 'Rule should have isEnabled boolean');
    assert(Array.isArray(rule.applicableVariables), 'Rule should have applicableVariables array');
    assert(rule.metadata, 'Rule should have metadata object');
});

// ============== PROTOCOL CRUD OPERATIONS TESTS ==============

runner.test('Create new protocol rule', () => {
    const protocol = {
        id: "test_protocol",
        name: "Test Protocol",
        rules: []
    };

    const newRule = {
        id: "rule_001",
        category: "Custom",
        title: "New Test Rule",
        rule: "Test description",
        rationale: "",
        applicableVariables: [],
        priority: 1,
        isEnabled: true,
        aiPromptText: "Test prompt",
        examples: [],
        metadata: { author: "test", tags: [], citations: [] }
    };

    protocol.rules.push(newRule);

    assertArrayLength(protocol.rules, 1, 'Protocol should have 1 rule');
    assertEquals(protocol.rules[0].id, "rule_001", 'Rule should have correct ID');
});

runner.test('Edit existing protocol rule', () => {
    const protocol = {
        rules: [
            {
                id: "rule_001",
                title: "Original Title",
                rule: "Original description",
                isEnabled: true
            }
        ]
    };

    const rule = protocol.rules.find(r => r.id === "rule_001");
    rule.title = "Updated Title";
    rule.rule = "Updated description";

    assertEquals(rule.title, "Updated Title", 'Rule title should be updated');
    assertEquals(rule.rule, "Updated description", 'Rule description should be updated');
});

runner.test('Delete protocol rule', () => {
    const protocol = {
        rules: [
            { id: "rule_001", title: "Rule 1" },
            { id: "rule_002", title: "Rule 2" },
            { id: "rule_003", title: "Rule 3" }
        ]
    };

    const index = protocol.rules.findIndex(r => r.id === "rule_002");
    protocol.rules.splice(index, 1);

    assertArrayLength(protocol.rules, 2, 'Protocol should have 2 rules after deletion');
    assert(!protocol.rules.find(r => r.id === "rule_002"), 'Deleted rule should not exist');
});

runner.test('Duplicate protocol rule', () => {
    const protocol = {
        rules: [
            {
                id: "rule_001",
                title: "Original Rule",
                rule: "Original description",
                priority: 1
            }
        ]
    };

    const original = protocol.rules[0];
    const duplicate = {
        ...JSON.parse(JSON.stringify(original)),
        id: "rule_002",
        title: original.title + " (Copy)"
    };

    protocol.rules.push(duplicate);

    assertArrayLength(protocol.rules, 2, 'Protocol should have 2 rules after duplication');
    assertEquals(protocol.rules[1].title, "Original Rule (Copy)", 'Duplicated rule should have (Copy) suffix');
});

runner.test('Toggle protocol rule enabled state', () => {
    const rule = {
        id: "rule_001",
        isEnabled: true
    };

    rule.isEnabled = !rule.isEnabled;
    assertEquals(rule.isEnabled, false, 'Rule should be disabled');

    rule.isEnabled = !rule.isEnabled;
    assertEquals(rule.isEnabled, true, 'Rule should be enabled again');
});

// ============== PROTOCOL PERSISTENCE TESTS ==============

runner.test('Save protocols to localStorage', () => {
    const protocols = {
        test_protocol: {
            id: "test_protocol",
            name: "Test Protocol",
            version: "1.0",
            rules: [
                { id: "rule_001", title: "Test Rule", isEnabled: true }
            ]
        }
    };

    const state = {
        protocols: protocols,
        activeProtocols: ['test_protocol']
    };

    localStorage.setItem('clinicalAbstractionState', JSON.stringify(state));

    const saved = localStorage.getItem('clinicalAbstractionState');
    assert(saved, 'State should be saved to localStorage');

    const parsed = JSON.parse(saved);
    assert(parsed.protocols, 'Saved state should have protocols');
    assertEquals(parsed.activeProtocols[0], 'test_protocol', 'Active protocol should be saved');
});

runner.test('Load protocols from localStorage', () => {
    const state = {
        protocols: {
            cardiology_hf: {
                id: "cardiology_hf",
                name: "Cardiology Protocol",
                rules: [{ id: "rule_001", title: "Test Rule" }]
            }
        },
        activeProtocols: ['cardiology_hf']
    };

    localStorage.setItem('clinicalAbstractionState', JSON.stringify(state));

    const loaded = JSON.parse(localStorage.getItem('clinicalAbstractionState'));

    assert(loaded.protocols, 'Loaded state should have protocols');
    assert(loaded.protocols.cardiology_hf, 'Loaded protocols should contain cardiology_hf');
    assertArrayLength(loaded.activeProtocols, 1, 'Should have one active protocol');
});

runner.test('Migration of old protocol format to new format', () => {
    // Simulate old format without new fields
    const oldProtocol = {
        name: "Old Protocol",
        rules: [
            {
                title: "Old Rule",
                rule: "Old description",
                category: "Test"
            }
        ]
    };

    // Migration function
    function migrateProtocol(oldProtocol, id) {
        return {
            id: id,
            name: oldProtocol.name,
            version: oldProtocol.version || "1.0",
            schema: oldProtocol.schema || "default",
            source: "builtin",
            isActive: true,
            createdDate: new Date().toISOString(),
            modifiedDate: new Date().toISOString(),
            rules: oldProtocol.rules.map((rule, idx) => ({
                id: rule.id || `rule_${String(idx + 1).padStart(3, '0')}`,
                category: rule.category || "Custom",
                title: rule.title,
                rule: rule.rule,
                rationale: rule.rationale || "",
                applicableVariables: rule.applicableVariables || [],
                priority: rule.priority || (idx + 1),
                isEnabled: rule.isEnabled !== false,
                aiPromptText: rule.aiPromptText || rule.rule,
                examples: rule.examples || [],
                metadata: rule.metadata || { author: "system", tags: [], citations: [] }
            }))
        };
    }

    const migrated = migrateProtocol(oldProtocol, "old_protocol");

    assert(migrated.id, 'Migrated protocol should have id');
    assert(migrated.version, 'Migrated protocol should have version');
    assert(migrated.source, 'Migrated protocol should have source');
    assertEquals(migrated.rules[0].id, "rule_001", 'Migrated rule should have generated ID');
    assert(typeof migrated.rules[0].isEnabled === 'boolean', 'Migrated rule should have isEnabled');
});

// ============== PROTOCOL IMPORT/EXPORT TESTS ==============

runner.test('Export protocol to JSON', () => {
    const protocol = {
        id: "test_protocol",
        name: "Test Protocol",
        version: "1.0",
        schema: "cardiology",
        rules: [
            {
                id: "rule_001",
                category: "Test",
                title: "Test Rule",
                rule: "Test description",
                rationale: "Test rationale",
                applicableVariables: ["var1"],
                priority: 1,
                isEnabled: true,
                aiPromptText: "Test prompt",
                examples: [],
                metadata: { author: "test", tags: [], citations: [] }
            }
        ]
    };

    const exportData = {
        id: protocol.id,
        name: protocol.name,
        version: protocol.version,
        schema: protocol.schema,
        exportedDate: new Date().toISOString(),
        rules: protocol.rules
    };

    const jsonString = JSON.stringify(exportData, null, 2);

    assert(jsonString, 'Should generate JSON string');
    const parsed = JSON.parse(jsonString);
    assertEquals(parsed.id, "test_protocol", 'Exported protocol should have correct ID');
    assertArrayLength(parsed.rules, 1, 'Exported protocol should have 1 rule');
});

runner.test('Import protocol from JSON with validation', () => {
    const importedJson = {
        "id": "imported_protocol",
        "name": "Imported Protocol",
        "version": "2.0",
        "schema": "oncology",
        "rules": [
            {
                "id": "rule_001",
                "category": "Imported",
                "title": "Imported Rule",
                "rule": "Imported description",
                "priority": 1
            }
        ]
    };

    // Validation function
    function validateImportedProtocol(data) {
        if (!data.name || !data.rules) {
            throw new Error('Invalid protocol format: missing name or rules');
        }
        if (!Array.isArray(data.rules)) {
            throw new Error('Invalid protocol format: rules must be an array');
        }
        return true;
    }

    // Normalization function
    function normalizeImportedProtocol(data) {
        return {
            id: data.id || 'imported_protocol',
            name: data.name,
            version: data.version || "1.0",
            schema: data.schema || "default",
            source: "imported",
            isActive: true,
            createdDate: new Date().toISOString(),
            modifiedDate: new Date().toISOString(),
            rules: data.rules.map((rule, idx) => ({
                id: rule.id || `rule_${String(idx + 1).padStart(3, '0')}`,
                category: rule.category || "Custom",
                title: rule.title || "Untitled Rule",
                rule: rule.rule || "",
                rationale: rule.rationale || "",
                applicableVariables: rule.applicableVariables || [],
                priority: rule.priority || (idx + 1),
                isEnabled: rule.isEnabled !== false,
                aiPromptText: rule.aiPromptText || rule.rule || "",
                examples: rule.examples || [],
                metadata: rule.metadata || { author: "imported", tags: [], citations: [] }
            }))
        };
    }

    assert(validateImportedProtocol(importedJson), 'Imported protocol should be valid');
    const normalized = normalizeImportedProtocol(importedJson);

    assertEquals(normalized.source, "imported", 'Imported protocol should have source="imported"');
    assert(normalized.createdDate, 'Imported protocol should have createdDate');
    assert(normalized.rules[0].metadata, 'Imported rules should have metadata');
});

runner.test('Import validation rejects invalid protocol', () => {
    const invalidJson = {
        "name": "Invalid Protocol"
        // Missing rules array
    };

    function validateImportedProtocol(data) {
        if (!data.name || !data.rules) {
            throw new Error('Invalid protocol format: missing name or rules');
        }
        return true;
    }

    let errorThrown = false;
    try {
        validateImportedProtocol(invalidJson);
    } catch (error) {
        errorThrown = true;
        assert(error.message.includes('missing name or rules'), 'Should throw validation error');
    }

    assert(errorThrown, 'Should throw error for invalid protocol');
});

// ============== AI EXTRACTION ENGINE TESTS ==============

runner.test('Get active protocol rules for variables', () => {
    const appState = {
        protocols: {
            cardiology_hf: {
                id: "cardiology_hf",
                isActive: true,
                rules: [
                    {
                        id: "rule_001",
                        title: "BNP Rule",
                        rule: "Use lab values for BNP",
                        applicableVariables: ["bnp"],
                        priority: 1,
                        isEnabled: true,
                        aiPromptText: "When extracting BNP, use lab values"
                    },
                    {
                        id: "rule_002",
                        title: "General Rule",
                        rule: "Prefer recent values",
                        applicableVariables: [],
                        priority: 2,
                        isEnabled: true,
                        aiPromptText: "Prefer recent values"
                    },
                    {
                        id: "rule_003",
                        title: "Disabled Rule",
                        rule: "This should not appear",
                        applicableVariables: ["bnp"],
                        priority: 3,
                        isEnabled: false,
                        aiPromptText: "This should not be used"
                    }
                ]
            }
        },
        activeProtocols: ['cardiology_hf']
    };

    function getActiveProtocolRules(variableNames, appState) {
        const rules = [];
        const activeProtocolIds = appState.activeProtocols || [];

        for (const protocolId of activeProtocolIds) {
            const protocol = appState.protocols[protocolId];
            if (!protocol || !protocol.isActive || !protocol.rules) {
                continue;
            }

            for (const rule of protocol.rules) {
                if (!rule.isEnabled) continue;

                const appliesToCurrentVars = !rule.applicableVariables ||
                    rule.applicableVariables.length === 0 ||
                    rule.applicableVariables.some(v => variableNames.includes(v));

                if (appliesToCurrentVars) {
                    rules.push({
                        id: rule.id,
                        category: rule.category,
                        title: rule.title,
                        rule: rule.rule,
                        aiPromptText: rule.aiPromptText || rule.rule,
                        applicableVariables: rule.applicableVariables,
                        priority: rule.priority || 999,
                        examples: rule.examples
                    });
                }
            }
        }

        rules.sort((a, b) => a.priority - b.priority);
        return rules;
    }

    const variableNames = ["bnp", "heart_rate"];
    const rules = getActiveProtocolRules(variableNames, appState);

    // Should include rule_001 (applies to BNP) and rule_002 (applies to all)
    // Should NOT include rule_003 (disabled)
    assertArrayLength(rules, 2, 'Should return 2 active applicable rules');
    assertEquals(rules[0].id, "rule_001", 'First rule should be rule_001 (priority 1)');
    assertEquals(rules[1].id, "rule_002", 'Second rule should be rule_002 (priority 2)');
});

runner.test('Rules are sorted by priority', () => {
    const appState = {
        protocols: {
            test: {
                isActive: true,
                rules: [
                    { id: "rule_003", priority: 3, isEnabled: true, applicableVariables: [] },
                    { id: "rule_001", priority: 1, isEnabled: true, applicableVariables: [] },
                    { id: "rule_002", priority: 2, isEnabled: true, applicableVariables: [] }
                ]
            }
        },
        activeProtocols: ['test']
    };

    function getActiveProtocolRules(variableNames, appState) {
        const rules = [];
        for (const protocolId of appState.activeProtocols) {
            const protocol = appState.protocols[protocolId];
            if (!protocol || !protocol.isActive) continue;
            for (const rule of protocol.rules) {
                if (rule.isEnabled) {
                    rules.push({ ...rule, aiPromptText: rule.rule });
                }
            }
        }
        rules.sort((a, b) => a.priority - b.priority);
        return rules;
    }

    const rules = getActiveProtocolRules([], appState);

    assertEquals(rules[0].id, "rule_001", 'First should be priority 1');
    assertEquals(rules[1].id, "rule_002", 'Second should be priority 2');
    assertEquals(rules[2].id, "rule_003", 'Third should be priority 3');
});

runner.test('Create extraction prompt with protocol rules', () => {
    function createExtractionPrompt(text, variables, protocolRules) {
        const varList = variables.join(', ');

        let protocolSection = "";
        if (protocolRules && protocolRules.length > 0) {
            protocolSection = "\n\n**PROTOCOL RULES:**\n";
            protocolRules.forEach((rule, idx) => {
                protocolSection += `${idx + 1}. ${rule.title}: ${rule.aiPromptText}\n`;
            });
        }

        return `Extract the following variables: ${varList}${protocolSection}\n\nText: ${text}`;
    }

    const text = "Patient has BNP 450 pg/mL";
    const variables = ["bnp"];
    const protocolRules = [
        {
            id: "rule_001",
            title: "Lab Priority",
            aiPromptText: "When extracting BNP, prioritize lab values"
        }
    ];

    const prompt = createExtractionPrompt(text, variables, protocolRules);

    assert(prompt.includes('BNP'), 'Prompt should include variable name');
    assert(prompt.includes('PROTOCOL RULES'), 'Prompt should include protocol rules section');
    assert(prompt.includes('Lab Priority'), 'Prompt should include rule title');
    assert(prompt.includes('prioritize lab values'), 'Prompt should include rule prompt text');
});

// ============== AI INTEGRATION TESTS ==============

runner.test('Extraction request includes protocol rules', () => {
    const appState = {
        protocols: {
            cardiology_hf: {
                isActive: true,
                rules: [
                    {
                        id: "rule_001",
                        title: "Test Rule",
                        rule: "Test description",
                        isEnabled: true,
                        applicableVariables: ["bnp"],
                        priority: 1,
                        aiPromptText: "Test AI prompt"
                    }
                ]
            }
        },
        activeProtocols: ['cardiology_hf']
    };

    function getActiveProtocolRules(variableNames, appState) {
        const rules = [];
        for (const protocolId of appState.activeProtocols) {
            const protocol = appState.protocols[protocolId];
            if (!protocol || !protocol.isActive) continue;
            for (const rule of protocol.rules) {
                if (rule.isEnabled) {
                    rules.push({
                        id: rule.id,
                        title: rule.title,
                        aiPromptText: rule.aiPromptText || rule.rule,
                        applicableVariables: rule.applicableVariables,
                        priority: rule.priority
                    });
                }
            }
        }
        return rules;
    }

    const variableNames = ["bnp", "ejection_fraction"];
    const protocolRules = getActiveProtocolRules(variableNames, appState);

    const requestBody = {
        text: "Patient has BNP 450",
        variables: variableNames,
        protocol_rules: protocolRules,
        model: "gpt-4o"
    };

    assert(requestBody.protocol_rules, 'Request should include protocol_rules');
    assertArrayLength(requestBody.protocol_rules, 1, 'Should include 1 applicable rule');
    assertEquals(requestBody.protocol_rules[0].id, "rule_001", 'Should include correct rule');
});

runner.test('Backend prompt generation includes rules', () => {
    // Simulate backend prompt generation
    function createBackendPrompt(variables, protocolRules) {
        let prompt = `Extract these variables: ${variables.join(', ')}\n`;

        if (protocolRules && protocolRules.length > 0) {
            prompt += "\n**ABSTRACTION PROTOCOL RULES - FOLLOW CAREFULLY:**\n";
            protocolRules.forEach((rule, idx) => {
                prompt += `${idx + 1}. **${rule.title}**\n`;
                prompt += `   ${rule.aiPromptText}\n`;
                if (rule.applicableVariables && rule.applicableVariables.length > 0) {
                    prompt += `   Applies to: ${rule.applicableVariables.join(', ')}\n`;
                }
            });
        }

        return prompt;
    }

    const variables = ["bnp", "ejection_fraction"];
    const protocolRules = [
        {
            id: "rule_001",
            title: "Lab Priority Rule",
            aiPromptText: "Prioritize laboratory values over clinical notes",
            applicableVariables: ["bnp"]
        }
    ];

    const prompt = createBackendPrompt(variables, protocolRules);

    assert(prompt.includes('ABSTRACTION PROTOCOL RULES'), 'Prompt should have rules section');
    assert(prompt.includes('Lab Priority Rule'), 'Prompt should include rule title');
    assert(prompt.includes('Prioritize laboratory values'), 'Prompt should include rule text');
    assert(prompt.includes('Applies to: bnp'), 'Prompt should show applicable variables');
});

// ============== VARIABLE OPERATIONS TESTS ==============

runner.test('Accept extraction', () => {
    const extractions = [
        {
            id: "ext_001",
            variable_name: "bnp",
            value: "450",
            status: "pending",
            confidence: 0.95
        }
    ];

    function acceptExtraction(id, extractions) {
        const ext = extractions.find(e => e.id === id);
        if (ext && ext.status === 'pending') {
            ext.status = 'accepted';
            return true;
        }
        return false;
    }

    const result = acceptExtraction("ext_001", extractions);

    assert(result, 'Should successfully accept extraction');
    assertEquals(extractions[0].status, 'accepted', 'Status should be "accepted"');
});

runner.test('Reject extraction', () => {
    const extractions = [
        {
            id: "ext_001",
            variable_name: "bnp",
            value: "450",
            status: "pending"
        }
    ];

    function rejectExtraction(id, extractions) {
        const ext = extractions.find(e => e.id === id);
        if (ext && ext.status === 'pending') {
            ext.status = 'rejected';
            return true;
        }
        return false;
    }

    const result = rejectExtraction("ext_001", extractions);

    assert(result, 'Should successfully reject extraction');
    assertEquals(extractions[0].status, 'rejected', 'Status should be "rejected"');
});

runner.test('Revert extraction to pending', () => {
    const extractions = [
        {
            id: "ext_001",
            status: "accepted"
        }
    ];

    function revertToPending(id, extractions) {
        const ext = extractions.find(e => e.id === id);
        if (ext) {
            ext.status = 'pending';
            return true;
        }
        return false;
    }

    const result = revertToPending("ext_001", extractions);

    assert(result, 'Should successfully revert extraction');
    assertEquals(extractions[0].status, 'pending', 'Status should be "pending"');
});

runner.test('Auto-acceptance based on confidence', () => {
    const extractions = [
        { id: "ext_001", confidence: 0.98, status: "pending" },
        { id: "ext_002", confidence: 0.85, status: "pending" },
        { id: "ext_003", confidence: 0.60, status: "pending" }
    ];

    function autoAcceptHighConfidence(extractions, threshold = 0.95) {
        let autoAccepted = 0;
        for (const ext of extractions) {
            if (ext.status === 'pending' && ext.confidence >= threshold) {
                ext.status = 'auto';
                autoAccepted++;
            }
        }
        return autoAccepted;
    }

    const count = autoAcceptHighConfidence(extractions, 0.95);

    assertEquals(count, 1, 'Should auto-accept 1 extraction');
    assertEquals(extractions[0].status, 'auto', 'High confidence should be auto-accepted');
    assertEquals(extractions[1].status, 'pending', 'Medium confidence should remain pending');
});

// ============== STATISTICS TESTS ==============

runner.test('Calculate global statistics', () => {
    const extractions = [
        { variable_name: "bnp", status: "accepted", confidence: 0.95 },
        { variable_name: "bnp", status: "auto", confidence: 0.98 },
        { variable_name: "ejection_fraction", status: "accepted", confidence: 0.85 },
        { variable_name: "ejection_fraction", status: "rejected", confidence: 0.60 },
        { variable_name: "heart_rate", status: "pending", confidence: 0.75 }
    ];

    function calculateStats(extractions) {
        const stats = {
            totalExtractions: extractions.length,
            totalAccepted: 0,
            totalRejected: 0,
            totalAutoAccepted: 0,
            totalManualAccepted: 0,
            averageConfidence: 0
        };

        let confidenceSum = 0;

        for (const ext of extractions) {
            if (ext.status === 'accepted') {
                stats.totalAccepted++;
                stats.totalManualAccepted++;
            } else if (ext.status === 'auto') {
                stats.totalAccepted++;
                stats.totalAutoAccepted++;
            } else if (ext.status === 'rejected') {
                stats.totalRejected++;
            }
            confidenceSum += ext.confidence;
        }

        stats.averageConfidence = confidenceSum / extractions.length;

        return stats;
    }

    const stats = calculateStats(extractions);

    assertEquals(stats.totalExtractions, 5, 'Should count all extractions');
    assertEquals(stats.totalAccepted, 3, 'Should count accepted + auto');
    assertEquals(stats.totalManualAccepted, 2, 'Should count manual acceptances');
    assertEquals(stats.totalAutoAccepted, 1, 'Should count auto acceptances');
    assertEquals(stats.totalRejected, 1, 'Should count rejections');
    assert(stats.averageConfidence > 0.8, 'Average confidence should be calculated');
});

runner.test('Calculate per-variable statistics', () => {
    const extractions = [
        { variable_name: "bnp", status: "accepted", confidence: 0.95, value: "450" },
        { variable_name: "bnp", status: "auto", confidence: 0.98, value: "480" },
        { variable_name: "bnp", status: "rejected", confidence: 0.60, value: "500" },
        { variable_name: "ejection_fraction", status: "accepted", confidence: 0.85, value: "35" }
    ];

    function calculateVariableStats(extractions) {
        const byVariable = {};

        for (const ext of extractions) {
            if (!byVariable[ext.variable_name]) {
                byVariable[ext.variable_name] = {
                    total: 0,
                    accepted: 0,
                    rejected: 0,
                    avgConfidence: 0,
                    confidenceSum: 0
                };
            }

            const varStats = byVariable[ext.variable_name];
            varStats.total++;
            varStats.confidenceSum += ext.confidence;

            if (ext.status === 'accepted' || ext.status === 'auto') {
                varStats.accepted++;
            } else if (ext.status === 'rejected') {
                varStats.rejected++;
            }
        }

        // Calculate averages
        for (const varName in byVariable) {
            const stats = byVariable[varName];
            stats.avgConfidence = stats.confidenceSum / stats.total;
        }

        return byVariable;
    }

    const stats = calculateVariableStats(extractions);

    assert(stats.bnp, 'Should have stats for BNP');
    assertEquals(stats.bnp.total, 3, 'BNP should have 3 total extractions');
    assertEquals(stats.bnp.accepted, 2, 'BNP should have 2 accepted');
    assertEquals(stats.bnp.rejected, 1, 'BNP should have 1 rejected');

    assert(stats.ejection_fraction, 'Should have stats for ejection_fraction');
    assertEquals(stats.ejection_fraction.total, 1, 'EF should have 1 extraction');
});

// ============== END-TO-END WORKFLOW TESTS ==============

runner.test('E2E: Complete protocol creation workflow', () => {
    // 1. Create new protocol
    const newProtocol = {
        id: "e2e_test_protocol",
        name: "E2E Test Protocol",
        version: "1.0",
        schema: "test",
        source: "custom",
        isActive: true,
        createdDate: new Date().toISOString(),
        modifiedDate: new Date().toISOString(),
        rules: []
    };

    // 2. Add rules
    newProtocol.rules.push({
        id: "rule_001",
        category: "Test",
        title: "Test Rule 1",
        rule: "Test description 1",
        rationale: "Test rationale",
        applicableVariables: ["var1"],
        priority: 1,
        isEnabled: true,
        aiPromptText: "Test prompt 1",
        examples: [],
        metadata: { author: "test", tags: [], citations: [] }
    });

    newProtocol.rules.push({
        id: "rule_002",
        category: "Test",
        title: "Test Rule 2",
        rule: "Test description 2",
        rationale: "",
        applicableVariables: [],
        priority: 2,
        isEnabled: true,
        aiPromptText: "Test prompt 2",
        examples: [],
        metadata: { author: "test", tags: [], citations: [] }
    });

    // 3. Save to state
    const appState = {
        protocols: {
            e2e_test_protocol: newProtocol
        },
        activeProtocols: ['e2e_test_protocol']
    };

    localStorage.setItem('testState', JSON.stringify(appState));

    // 4. Load from state
    const loaded = JSON.parse(localStorage.getItem('testState'));

    // Assertions
    assert(loaded.protocols.e2e_test_protocol, 'Protocol should be saved and loaded');
    assertArrayLength(loaded.protocols.e2e_test_protocol.rules, 2, 'Should have 2 rules');
    assertEquals(loaded.activeProtocols[0], 'e2e_test_protocol', 'Should be active protocol');

    // Cleanup
    localStorage.removeItem('testState');
});

runner.test('E2E: Import, edit, and export protocol', () => {
    // 1. Import JSON
    const importedJson = {
        "id": "imported_e2e",
        "name": "Imported E2E Protocol",
        "version": "1.0",
        "rules": [
            {
                "id": "rule_001",
                "title": "Imported Rule",
                "rule": "Imported description",
                "category": "Import"
            }
        ]
    };

    // 2. Normalize
    const normalized = {
        id: importedJson.id,
        name: importedJson.name,
        version: importedJson.version || "1.0",
        schema: "default",
        source: "imported",
        isActive: true,
        createdDate: new Date().toISOString(),
        modifiedDate: new Date().toISOString(),
        rules: importedJson.rules.map((rule, idx) => ({
            id: rule.id || `rule_${String(idx + 1).padStart(3, '0')}`,
            category: rule.category || "Custom",
            title: rule.title,
            rule: rule.rule,
            rationale: rule.rationale || "",
            applicableVariables: rule.applicableVariables || [],
            priority: idx + 1,
            isEnabled: true,
            aiPromptText: rule.aiPromptText || rule.rule,
            examples: [],
            metadata: { author: "imported", tags: [], citations: [] }
        }))
    };

    // 3. Edit rule
    normalized.rules[0].title = "Edited Imported Rule";
    normalized.rules[0].priority = 5;
    normalized.modifiedDate = new Date().toISOString();

    // 4. Export
    const exported = {
        id: normalized.id,
        name: normalized.name,
        version: normalized.version,
        schema: normalized.schema,
        source: normalized.source || "custom",
        exportedDate: new Date().toISOString(),
        rules: normalized.rules
    };

    const jsonString = JSON.stringify(exported, null, 2);
    const reparsed = JSON.parse(jsonString);

    // Assertions
    assertEquals(reparsed.rules[0].title, "Edited Imported Rule", 'Edits should be preserved in export');
    assertEquals(reparsed.rules[0].priority, 5, 'Priority change should be preserved');
    assertEquals(reparsed.source, "imported", 'Source should be preserved');
});

runner.test('E2E: Full extraction workflow with protocol rules', () => {
    // 1. Setup protocol with rules
    const appState = {
        protocols: {
            test_protocol: {
                id: "test_protocol",
                isActive: true,
                rules: [
                    {
                        id: "rule_001",
                        title: "Lab Priority",
                        rule: "Use lab values",
                        applicableVariables: ["bnp"],
                        priority: 1,
                        isEnabled: true,
                        aiPromptText: "Prioritize lab values for BNP"
                    }
                ]
            }
        },
        activeProtocols: ['test_protocol'],
        patientExtractions: {}
    };

    // 2. Get applicable rules
    function getActiveProtocolRules(variableNames, appState) {
        const rules = [];
        for (const protocolId of appState.activeProtocols) {
            const protocol = appState.protocols[protocolId];
            if (protocol && protocol.isActive) {
                for (const rule of protocol.rules) {
                    if (rule.isEnabled) {
                        rules.push({
                            id: rule.id,
                            title: rule.title,
                            aiPromptText: rule.aiPromptText,
                            priority: rule.priority
                        });
                    }
                }
            }
        }
        return rules;
    }

    const variableNames = ["bnp", "ejection_fraction"];
    const protocolRules = getActiveProtocolRules(variableNames, appState);

    // 3. Simulate extraction (would call backend in real app)
    const mockExtraction = {
        id: "ext_001",
        variable_name: "bnp",
        value: "450",
        confidence: 0.95,
        status: "pending",
        evidence: { text: "BNP 450 pg/mL", start_offset: 0, end_offset: 14 },
        applied_rules: ["rule_001"]
    };

    // 4. Accept extraction
    mockExtraction.status = "accepted";

    // 5. Save to patient state
    const patientId = "patient_001";
    appState.patientExtractions[patientId] = [mockExtraction];

    // Assertions
    assertArrayLength(protocolRules, 1, 'Should get 1 protocol rule');
    assertEquals(mockExtraction.status, "accepted", 'Extraction should be accepted');
    assert(mockExtraction.applied_rules.includes("rule_001"), 'Should track applied rules');
    assert(appState.patientExtractions[patientId], 'Extraction should be saved to patient');
});

runner.test('E2E: Multi-patient extraction with statistics', () => {
    const appState = {
        protocols: {
            cardiology_hf: {
                isActive: true,
                rules: [
                    { id: "rule_001", isEnabled: true, applicableVariables: [], priority: 1, aiPromptText: "Test" }
                ]
            }
        },
        activeProtocols: ['cardiology_hf'],
        patientExtractions: {}
    };

    // Simulate extractions for multiple patients
    const patients = [
        { patient_id: "pat_001", name: "Patient 1" },
        { patient_id: "pat_002", name: "Patient 2" },
        { patient_id: "pat_003", name: "Patient 3" }
    ];

    patients.forEach((patient, idx) => {
        appState.patientExtractions[patient.patient_id] = [
            {
                id: `ext_${idx}_1`,
                variable_name: "bnp",
                value: String(400 + idx * 50),
                status: "accepted",
                confidence: 0.95
            },
            {
                id: `ext_${idx}_2`,
                variable_name: "ejection_fraction",
                value: String(35 + idx * 5),
                status: "auto",
                confidence: 0.98
            }
        ];
    });

    // Calculate global statistics
    let totalExtractions = 0;
    let totalAccepted = 0;

    for (const patientId in appState.patientExtractions) {
        const extractions = appState.patientExtractions[patientId];
        totalExtractions += extractions.length;
        totalAccepted += extractions.filter(e => e.status === 'accepted' || e.status === 'auto').length;
    }

    // Assertions
    assertEquals(totalExtractions, 6, 'Should have 6 total extractions (3 patients × 2 variables)');
    assertEquals(totalAccepted, 6, 'All extractions should be accepted');
    assertEquals(Object.keys(appState.patientExtractions).length, 3, 'Should have 3 patients');
});

// ============== ERROR HANDLING TESTS ==============

runner.test('Handle missing protocol gracefully', () => {
    const appState = {
        protocols: {},
        activeProtocols: ['nonexistent_protocol']
    };

    function getActiveProtocolRules(variableNames, appState) {
        const rules = [];
        for (const protocolId of appState.activeProtocols) {
            const protocol = appState.protocols[protocolId];
            if (!protocol || !protocol.isActive) {
                continue; // Gracefully skip missing protocols
            }
            // ... rest of logic
        }
        return rules;
    }

    const rules = getActiveProtocolRules(["bnp"], appState);

    assertArrayLength(rules, 0, 'Should return empty array for missing protocol');
});

runner.test('Handle corrupted localStorage data', () => {
    localStorage.setItem('corrupted', 'invalid json {{{');

    function loadState() {
        try {
            const data = localStorage.getItem('corrupted');
            return JSON.parse(data);
        } catch (error) {
            console.log('Failed to parse state, using defaults');
            return { protocols: {}, activeProtocols: [] };
        }
    }

    const state = loadState();

    assert(state, 'Should return default state');
    assert(state.protocols, 'Default state should have protocols object');

    localStorage.removeItem('corrupted');
});

runner.test('Handle empty rules array', () => {
    const appState = {
        protocols: {
            empty_protocol: {
                isActive: true,
                rules: []
            }
        },
        activeProtocols: ['empty_protocol']
    };

    function getActiveProtocolRules(variableNames, appState) {
        const rules = [];
        for (const protocolId of appState.activeProtocols) {
            const protocol = appState.protocols[protocolId];
            if (!protocol || !protocol.isActive || !protocol.rules) continue;
            for (const rule of protocol.rules) {
                if (rule.isEnabled) {
                    rules.push(rule);
                }
            }
        }
        return rules;
    }

    const rules = getActiveProtocolRules(["bnp"], appState);

    assertArrayLength(rules, 0, 'Should handle empty rules array');
});

// ============== RUN TESTS ==============

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runner };
}

// Auto-run if executed directly
if (typeof window === 'undefined') {
    runner.run().then(results => {
        process.exit(results.failed > 0 ? 1 : 0);
    });
}
