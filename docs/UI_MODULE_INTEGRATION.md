# UI Module Integration Guide

How to build a visual workflow editor using Flyto2's module metadata system.

---

## Table of Contents

- [Overview](#overview)
- [Fetching Module Metadata](#fetching-module-metadata)
- [Rendering Module Blocks](#rendering-module-blocks)
- [Connection Compatibility](#connection-compatibility)
- [Form Generation](#form-generation)
- [Complete React Example](#complete-react-example)

---

## Overview

Flyto2's `@register_module` metadata is designed to power visual workflow editors like n8n, Node-RED, or Zapier.

### Key Concepts

1. **Module Metadata** → UI Block properties (label, icon, color)
2. **params_schema** → Form fields
3. **output_schema** → Output connection points
4. **input_types/output_types** → Connection compatibility
5. **can_connect_to/can_receive_from** → Explicit connection rules

---

## Fetching Module Metadata

### API Endpoint

```bash
GET /api/modules/metadata
```

**Response:**
```json
{
  "data.json.parse": {
    "module_id": "data.json.parse",
    "version": "1.0.0",
    "category": "data",
    "subcategory": "json",
    "label": "Parse JSON",
    "icon": "Braces",
    "color": "#F59E0B",
    "input_types": ["text", "string"],
    "output_types": ["json", "object"],
    "can_receive_from": ["file.read", "api.http.*"],
    "can_connect_to": ["data.*", "notification.*"],
    "params_schema": {
      "json_string": {
        "type": "string",
        "label": "JSON String",
        "description": "JSON string to parse",
        "required": true,
        "multiline": true
      }
    },
    "output_schema": {
      "data": {
        "type": "object",
        "description": "Parsed JSON object"
      }
    }
  },
  "notification.slack.send_message": {
    // ... more modules
  }
}
```

### JavaScript/TypeScript

```typescript
// Fetch all module metadata
async function fetchModules(): Promise<ModuleMetadata[]> {
    const response = await fetch('/api/modules/metadata');
    const data = await response.json();
    return Object.values(data);
}

interface ModuleMetadata {
    module_id: string;
    version: string;
    category: string;
    subcategory: string;
    label: string;
    icon: string;
    color: string;
    input_types: string[];
    output_types: string[];
    can_receive_from?: string[];
    can_connect_to?: string[];
    params_schema: Record<string, ParamDefinition>;
    output_schema: Record<string, OutputDefinition>;
}
```

---

## Rendering Module Blocks

### Visual Block Structure

```
┌─────────────────────────────────────┐
│ 🟣 Send Slack Message              │  ← Header (icon + label + color)
├─────────────────────────────────────┤
│ ◉ In: text, json                   │  ← Input types
├─────────────────────────────────────┤
│ Channel: [#general      ]          │  ← Form fields
│ Message: [____________  ]          │
│ Icon:    [:robot_face:  ]          │
├─────────────────────────────────────┤
│ ○ Out: message_ts, ok              │  ← Output schema
└─────────────────────────────────────┘
```

### React Component

```typescript
import { LucideIcon } from 'lucide-react';

interface ModuleBlockProps {
    module: ModuleMetadata;
    onConnect: (outputPort: string) => void;
}

function ModuleBlock({ module, onConnect }: ModuleBlockProps) {
    const Icon = getLucideIcon(module.icon); // Map icon name to component

    return (
        <div className="module-block" style={{ borderColor: module.color }}>
            {/* Header */}
            <div className="header" style={{ backgroundColor: module.color }}>
                <Icon size={20} color="white" />
                <span className="label">{module.label}</span>
            </div>

            {/* Input Types */}
            {module.input_types && module.input_types.length > 0 && (
                <div className="inputs">
                    <span className="port input-port">◉</span>
                    <span>In: {module.input_types.join(', ')}</span>
                </div>
            )}

            {/* Parameters Form */}
            <div className="params">
                {Object.entries(module.params_schema).map(([key, param]) => (
                    <FormField key={key} name={key} definition={param} />
                ))}
            </div>

            {/* Output Ports */}
            {module.output_schema && (
                <div className="outputs">
                    <span className="port output-port">○</span>
                    <span>Out: {Object.keys(module.output_schema).join(', ')}</span>
                </div>
            )}
        </div>
    );
}
```

---

## Connection Compatibility

### Checking if Two Modules Can Connect

```typescript
function canConnect(
    sourceModule: ModuleMetadata,
    targetModule: ModuleMetadata
): boolean {
    // 1. Check type compatibility
    const hasMatchingType = sourceModule.output_types.some(outType =>
        targetModule.input_types.includes(outType) ||
        targetModule.input_types.includes('any')
    );

    // 2. Check explicit allow list
    const isExplicitlyAllowed =
        sourceModule.can_connect_to?.some(pattern =>
            matchesPattern(targetModule.module_id, pattern)
        ) || false;

    // 3. Check explicit receive list
    const canReceive =
        targetModule.can_receive_from?.some(pattern =>
            matchesPattern(sourceModule.module_id, pattern)
        ) || false;

    return hasMatchingType || isExplicitlyAllowed || canReceive;
}

// Pattern matching with wildcards
function matchesPattern(moduleId: string, pattern: string): boolean {
    // Convert pattern to regex
    // 'browser.*' → '^browser\\..*$'
    // '*.json.*' → '^.*\\.json\\..*$'
    const regexPattern = pattern
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*');

    return new RegExp(`^${regexPattern}$`).test(moduleId);
}
```

### Visual Feedback

```typescript
function onDragConnection(
    sourceNode: Node,
    targetNode: Node,
    event: DragEvent
) {
    const source = sourceNode.module;
    const target = targetNode.module;

    if (canConnect(source, target)) {
        // Show green connection line
        setConnectionColor('green');
        setCanDrop(true);
    } else {
        // Show red X
        setConnectionColor('red');
        setCanDrop(false);
        showTooltip('Incompatible types');
    }
}
```

---

## Form Generation

### Auto-generate Forms from params_schema

```typescript
function FormField({ name, definition }: FormFieldProps) {
    const { type, label, description, required, default: defaultValue, multiline, options } = definition;

    switch (type) {
        case 'string':
            return multiline ? (
                <textarea
                    name={name}
                    placeholder={definition.placeholder}
                    required={required}
                    defaultValue={defaultValue}
                />
            ) : (
                <input
                    type="text"
                    name={name}
                    placeholder={definition.placeholder}
                    required={required}
                    defaultValue={defaultValue}
                />
            );

        case 'number':
            return (
                <input
                    type="number"
                    name={name}
                    required={required}
                    defaultValue={defaultValue}
                />
            );

        case 'boolean':
            return (
                <input
                    type="checkbox"
                    name={name}
                    defaultChecked={defaultValue}
                />
            );

        case 'select':
            return (
                <select name={name} required={required} defaultValue={defaultValue}>
                    {options?.map(opt => (
                        <option key={opt.value} value={opt.value}>
                            {opt.label}
                        </option>
                    ))}
                </select>
            );

        case 'array':
        case 'object':
            return <JSONEditor name={name} defaultValue={defaultValue} />;

        default:
            return <input type="text" name={name} />;
    }
}
```

### Example: Slack Module Form

Given this params_schema:
```json
{
  "channel": {
    "type": "string",
    "label": "Channel",
    "placeholder": "#general",
    "required": true
  },
  "text": {
    "type": "string",
    "label": "Message",
    "multiline": true,
    "required": true
  },
  "icon_emoji": {
    "type": "string",
    "label": "Icon",
    "default": ":robot_face:"
  }
}
```

Auto-generates:
```html
<form>
  <label>Channel *</label>
  <input type="text" name="channel" placeholder="#general" required />

  <label>Message *</label>
  <textarea name="text" required></textarea>

  <label>Icon</label>
  <input type="text" name="icon_emoji" value=":robot_face:" />
</form>
```

---

## Complete React Example

### Full Workflow Editor

```typescript
import React, { useState, useEffect } from 'react';
import ReactFlow, { Node, Edge, Connection } from 'reactflow';

function WorkflowEditor() {
    const [modules, setModules] = useState<ModuleMetadata[]>([]);
    const [nodes, setNodes] = useState<Node[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);

    // 1. Load modules
    useEffect(() => {
        fetch('/api/modules/metadata')
            .then(res => res.json())
            .then(data => setModules(Object.values(data)));
    }, []);

    // 2. Handle adding a module to canvas
    function onModuleDrop(module: ModuleMetadata, position: { x: number, y: number }) {
        const newNode: Node = {
            id: `node-${Date.now()}`,
            type: 'moduleBlock',
            position,
            data: { module },
        };
        setNodes([...nodes, newNode]);
    }

    // 3. Handle connection attempt
    function onConnect(connection: Connection) {
        const sourceNode = nodes.find(n => n.id === connection.source);
        const targetNode = nodes.find(n => n.id === connection.target);

        if (!sourceNode || !targetNode) return;

        // Check compatibility
        if (canConnect(sourceNode.data.module, targetNode.data.module)) {
            const newEdge: Edge = {
                id: `edge-${Date.now()}`,
                source: connection.source,
                target: connection.target,
                animated: true,
                style: { stroke: '#22c55e' } // Green
            };
            setEdges([...edges, newEdge]);
        } else {
            alert('Cannot connect: incompatible types');
        }
    }

    // 4. Generate YAML workflow
    function exportWorkflow(): string {
        const workflow = {
            name: 'My Workflow',
            steps: nodes.map(node => ({
                id: node.id,
                module: node.data.module.module_id,
                params: node.data.formValues || {}
            }))
        };
        return yaml.dump(workflow);
    }

    return (
        <div className="editor">
            {/* Module Palette */}
            <aside className="palette">
                <h3>Modules</h3>
                {modules.map(module => (
                    <ModulePaletteItem
                        key={module.module_id}
                        module={module}
                        onDragStart={(e) => onModuleDragStart(e, module)}
                    />
                ))}
            </aside>

            {/* Canvas */}
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onConnect={onConnect}
                onDrop={(e) => onCanvasDrop(e)}
                nodeTypes={{ moduleBlock: ModuleBlock }}
            />

            {/* Export Button */}
            <button onClick={() => {
                const yaml = exportWorkflow();
                downloadFile(yaml, 'workflow.yaml');
            }}>
                Export YAML
            </button>
        </div>
    );
}
```

---

## Connection Rules Examples

### Example 1: Browser Screenshot

```python
@register_module(
    module_id='browser.page.screenshot',
    input_types=['browser_instance'],
    output_types=['screenshot', 'image'],
    can_receive_from=['browser.instance.launch', 'browser.page.navigate'],
    can_connect_to=['file.write', 'cloud.s3.*', 'ai.vision.*'],
)
```

**UI Behavior:**
- ✅ Can connect FROM: `browser.instance.launch`, `browser.page.navigate`
- ✅ Can connect TO: `file.write`, `cloud.s3.upload`, `ai.vision.analyze`
- ❌ Cannot connect FROM: `data.json.parse` (incompatible type)
- ❌ Cannot connect TO: `notification.slack.*` (not in allow list)

### Example 2: Data Transform Chain

```python
# Module 1: Read File
@register_module(
    module_id='file.read',
    output_types=['text', 'string'],
    can_connect_to=['data.*', 'string.*'],
)

# Module 2: Parse JSON
@register_module(
    module_id='data.json.parse',
    input_types=['text', 'string'],
    output_types=['json', 'object'],
    can_receive_from=['file.read', 'api.http.*'],
    can_connect_to=['data.*', 'notification.*'],
)

# Module 3: Send Notification
@register_module(
    module_id='notification.slack.send_message',
    input_types=['text', 'json', 'any'],
    can_receive_from=['data.*', 'api.*'],
)
```

**Valid Flow:**
```
file.read → data.json.parse → notification.slack.send_message
   ✅          ✅                  ✅
```

---

## CSS Styling Example

```css
.module-block {
    width: 280px;
    border: 2px solid;
    border-radius: 8px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.module-block .header {
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: white;
    font-weight: 600;
    border-radius: 6px 6px 0 0;
}

.module-block .inputs,
.module-block .outputs {
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #666;
    background: #f9fafb;
}

.module-block .port {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
}

.input-port {
    background: #3b82f6; /* Blue */
}

.output-port {
    background: #22c55e; /* Green */
}

.module-block .params {
    padding: 12px;
}

.module-block input,
.module-block textarea,
.module-block select {
    width: 100%;
    padding: 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    margin-top: 4px;
}
```

---

## Best Practices

### 1. Cache Module Metadata
```typescript
// Load once on app init
const moduleCache = await fetchModules();
```

### 2. Validate Before Connecting
```typescript
// Always check compatibility
if (!canConnect(source, target)) {
    showError('Incompatible modules');
    return;
}
```

### 3. Show Visual Feedback
```typescript
// Change connection line color based on validity
const color = isValid ? 'green' : 'red';
```

### 4. Use Pattern Matching
```typescript
// Support wildcards in connection rules
'browser.*'  // Matches all browser modules
'*.json.*'   // Matches all JSON-related modules
```

### 5. Auto-complete Module Search
```typescript
// Filter modules by category, tags, or label
const filtered = modules.filter(m =>
    m.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.tags.some(tag => tag.includes(searchTerm))
);
```

---

## Summary

### Module Metadata Powers UI

```
@register_module metadata
        ↓
    UI reads
        ↓
┌─────────────────────┐
│ Visual Block        │  ← label, icon, color
│ Form Fields         │  ← params_schema
│ Connection Logic    │  ← input_types, can_connect_to
│ Output Ports        │  ← output_schema
└─────────────────────┘
```

### Key Points

✅ Use `input_types`/`output_types` for type checking
✅ Use `can_connect_to`/`can_receive_from` for explicit rules
✅ Auto-generate forms from `params_schema`
✅ Validate connections before creating edges
✅ Support wildcard patterns (`browser.*`, `*.json.*`)

---

**See Also:**
- [Module Specification](MODULE_SPECIFICATION.md)
- [Quick Reference](MODULE_QUICK_REFERENCE.md)
- [UI Builder Integration](UI_BUILDER_INTEGRATION.md)
