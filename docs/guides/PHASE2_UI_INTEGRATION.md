# Phase 2 UI Integration Guide

This guide shows how to integrate Phase 2 module metadata into the Flyto2 frontend UI.

---

## Overview

Phase 2 adds execution control and security metadata to all modules. The UI can use this metadata to:

- Display visual indicators (icons, badges)
- Show warnings and recommendations
- Provide better user experience
- Enable security compliance features

---

## Available Phase 2 Metadata

Each module now includes these Phase 2 fields:

```typescript
interface ModuleMetadata {
  // ... existing fields ...

  // Phase 2: Execution settings
  timeout?: number;              // Max execution time in seconds
  retryable?: boolean;           // Can auto-retry on failure
  max_retries?: number;          // Number of retry attempts
  concurrent_safe?: boolean;     // Safe for parallel execution

  // Phase 2: Security settings
  requires_credentials?: boolean;        // Needs API keys
  handles_sensitive_data?: boolean;      // Processes sensitive info
  required_permissions?: string[];       // Required permissions
}
```

---

## UI Components

### 1. Module Palette - Visual Indicators

Display icons/badges on module tiles to indicate Phase 2 characteristics.

#### Implementation

```tsx
interface ModuleTileProps {
  module: ModuleMetadata;
}

function ModuleTile({ module }: ModuleTileProps) {
  return (
    <div className="module-tile">
      <div className="module-header">
        <Icon name={module.icon} color={module.color} />
        <span>{module.label}</span>

        {/* Phase 2 badges */}
        <div className="phase2-badges">
          {module.requires_credentials && (
            <Badge
              icon="Key"
              tooltip="Requires API credentials"
              color="orange"
            />
          )}

          {module.handles_sensitive_data && (
            <Badge
              icon="Shield"
              tooltip="Handles sensitive data"
              color="red"
            />
          )}

          {module.timeout && (
            <Badge
              icon="Clock"
              tooltip={`Timeout: ${module.timeout}s`}
              color="blue"
            />
          )}

          {module.retryable && (
            <Badge
              icon="RotateCw"
              tooltip={`Auto-retry: ${module.max_retries} times`}
              color="green"
            />
          )}

          {!module.concurrent_safe && (
            <Badge
              icon="AlertTriangle"
              tooltip="Not safe for parallel execution"
              color="yellow"
            />
          )}
        </div>
      </div>
    </div>
  );
}
```

#### Visual Example

```
┌─────────────────────────────────────┐
│ 🧠 Claude Chat              🔑 🛡️  │
│ AI / Anthropic                      │
│ Send message to Claude AI           │
└─────────────────────────────────────┘
  🔑 = requires_credentials
  🛡️ = handles_sensitive_data

┌─────────────────────────────────────┐
│ 🌐 HTTP GET                  🔄 ⏱️  │
│ API / Network                       │
│ Make HTTP GET request               │
└─────────────────────────────────────┘
  🔄 = retryable
  ⏱️ = has timeout

┌─────────────────────────────────────┐
│ 🎨 Launch Browser            ⚠️     │
│ Browser / Automation                │
│ Start a new browser instance        │
└─────────────────────────────────────┘
  ⚠️ = not concurrent_safe
```

---

### 2. Module Configuration Panel

Show Phase 2 information when configuring a module.

#### Implementation

```tsx
function ModuleConfigPanel({ module }: { module: ModuleMetadata }) {
  return (
    <div className="config-panel">
      <h3>{module.label}</h3>

      {/* Phase 2 warnings */}
      <div className="phase2-warnings">
        {module.requires_credentials && !hasCredentials(module) && (
          <Alert type="warning">
            <Icon name="Key" />
            <div>
              <strong>API Credentials Required</strong>
              <p>This module needs {getCredentialName(module)}.</p>
              <button onClick={() => openCredentialsDialog(module)}>
                Configure Credentials
              </button>
            </div>
          </Alert>
        )}

        {module.handles_sensitive_data && (
          <Alert type="info">
            <Icon name="Shield" />
            <div>
              <strong>Sensitive Data Handling</strong>
              <p>This module processes sensitive information. Output may be masked in logs.</p>
            </div>
          </Alert>
        )}

        {!module.concurrent_safe && isInParallelBlock() && (
          <Alert type="error">
            <Icon name="AlertTriangle" />
            <div>
              <strong>Concurrency Warning</strong>
              <p>This module is not safe for parallel execution. Remove from parallel block.</p>
            </div>
          </Alert>
        )}
      </div>

      {/* Execution settings display */}
      {(module.timeout || module.retryable) && (
        <div className="execution-settings">
          <h4>Execution Settings</h4>

          {module.timeout && (
            <div className="setting-row">
              <Icon name="Clock" />
              <span>Timeout: {module.timeout}s</span>
              <Tooltip>
                Module will fail if execution exceeds {module.timeout} seconds
              </Tooltip>
            </div>
          )}

          {module.retryable && (
            <div className="setting-row">
              <Icon name="RotateCw" />
              <span>Auto-retry: {module.max_retries} times</span>
              <Tooltip>
                Module will automatically retry {module.max_retries} times on failure
                with exponential backoff
              </Tooltip>
            </div>
          )}
        </div>
      )}

      {/* Parameters form */}
      <ModuleParamsForm module={module} />
    </div>
  );
}
```

---

### 3. Workflow Canvas - Connection Validation

Use `concurrent_safe` to prevent invalid parallel connections.

#### Implementation

```tsx
function validateParallelBlock(modules: ModuleMetadata[]): ValidationResult {
  const unsafeModules = modules.filter(m => !m.concurrent_safe);

  if (unsafeModules.length > 0) {
    return {
      valid: false,
      error: `Cannot run in parallel: ${unsafeModules.map(m => m.label).join(', ')}`,
      suggestion: 'These modules must run sequentially due to resource conflicts'
    };
  }

  return { valid: true };
}

function ParallelBlock({ children }: { children: Module[] }) {
  const validation = validateParallelBlock(children.map(c => c.metadata));

  return (
    <div className={`parallel-block ${!validation.valid ? 'error' : ''}`}>
      {!validation.valid && (
        <Alert type="error">
          <Icon name="AlertTriangle" />
          {validation.error}
          <p className="suggestion">{validation.suggestion}</p>
        </Alert>
      )}

      <div className="parallel-lanes">
        {children}
      </div>
    </div>
  );
}
```

---

### 4. Execution Monitor - Real-time Feedback

Show Phase 2 execution behavior during workflow runs.

#### Implementation

```tsx
interface ModuleExecutionState {
  module: ModuleMetadata;
  status: 'pending' | 'running' | 'retrying' | 'success' | 'failed' | 'timeout';
  currentAttempt?: number;
  elapsedTime?: number;
}

function ExecutionMonitor({ state }: { state: ModuleExecutionState }) {
  const { module, status, currentAttempt, elapsedTime } = state;

  return (
    <div className={`execution-card status-${status}`}>
      <div className="module-info">
        <Icon name={module.icon} />
        <span>{module.label}</span>
      </div>

      <div className="execution-status">
        {status === 'running' && module.timeout && (
          <Progress
            value={elapsedTime}
            max={module.timeout}
            label={`${elapsedTime}s / ${module.timeout}s`}
            color={elapsedTime > module.timeout * 0.8 ? 'red' : 'blue'}
          />
        )}

        {status === 'retrying' && module.retryable && (
          <div className="retry-indicator">
            <Icon name="RotateCw" className="spin" />
            <span>Retrying ({currentAttempt}/{module.max_retries})</span>
          </div>
        )}

        {status === 'timeout' && (
          <Alert type="error">
            <Icon name="Clock" />
            <span>Timeout after {module.timeout}s</span>
          </Alert>
        )}

        {status === 'failed' && module.retryable && currentAttempt === module.max_retries && (
          <Alert type="error">
            <Icon name="XCircle" />
            <span>Failed after {module.max_retries} retries</span>
          </Alert>
        )}

        {status === 'success' && currentAttempt && currentAttempt > 1 && (
          <Alert type="success">
            <Icon name="CheckCircle" />
            <span>Succeeded on retry #{currentAttempt}</span>
          </Alert>
        )}
      </div>
    </div>
  );
}
```

---

### 5. Security & Compliance Dashboard

Show modules that handle sensitive data for compliance purposes.

#### Implementation

```tsx
function SecurityDashboard({ workflow }: { workflow: Workflow }) {
  const sensitiveModules = workflow.modules.filter(
    m => m.metadata.handles_sensitive_data
  );

  const credentialModules = workflow.modules.filter(
    m => m.metadata.requires_credentials
  );

  const permissions = new Set(
    workflow.modules.flatMap(m => m.metadata.required_permissions || [])
  );

  return (
    <div className="security-dashboard">
      <h2>Security Overview</h2>

      <div className="security-section">
        <h3>
          <Icon name="Shield" />
          Sensitive Data Handling ({sensitiveModules.length})
        </h3>
        <ul>
          {sensitiveModules.map(m => (
            <li key={m.id}>
              <Icon name={m.metadata.icon} />
              <span>{m.metadata.label}</span>
              <Badge color="red">Sensitive</Badge>
            </li>
          ))}
        </ul>
        {sensitiveModules.length > 0 && (
          <Alert type="warning">
            <Icon name="Info" />
            Workflow output logs will be masked for compliance
          </Alert>
        )}
      </div>

      <div className="security-section">
        <h3>
          <Icon name="Key" />
          Required Credentials ({credentialModules.length})
        </h3>
        <ul>
          {credentialModules.map(m => (
            <li key={m.id}>
              <Icon name={m.metadata.icon} />
              <span>{m.metadata.label}</span>
              {hasCredentials(m) ? (
                <Badge color="green">✓ Configured</Badge>
              ) : (
                <Badge color="red">⚠ Missing</Badge>
              )}
            </li>
          ))}
        </ul>
      </div>

      <div className="security-section">
        <h3>
          <Icon name="Lock" />
          Required Permissions ({permissions.size})
        </h3>
        <ul>
          {Array.from(permissions).map(perm => (
            <li key={perm}>
              <code>{perm}</code>
              {hasPermission(perm) ? (
                <Badge color="green">Granted</Badge>
              ) : (
                <Badge color="red">Denied</Badge>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

## API Integration

### Fetching Module Metadata

```typescript
interface ModuleMetadataResponse {
  modules: {
    [moduleId: string]: ModuleMetadata;
  };
}

async function fetchModuleMetadata(): Promise<ModuleMetadataResponse> {
  const response = await fetch('/api/modules/metadata');
  return response.json();
}

// Example response
{
  "modules": {
    "api.anthropic.chat": {
      "module_id": "api.anthropic.chat",
      "label": "Claude Chat",
      "icon": "Brain",
      "color": "#D97757",
      "timeout": 60,
      "retryable": true,
      "max_retries": 3,
      "concurrent_safe": true,
      "requires_credentials": true,
      "handles_sensitive_data": true,
      "required_permissions": ["network.access", "ai.api"]
    }
  }
}
```

---

## Icon Mapping

Recommended icons for Phase 2 indicators:

| Field | Icon | Color | Tooltip |
|-------|------|-------|---------|
| `requires_credentials` | Key | Orange | "Requires API credentials" |
| `handles_sensitive_data` | Shield | Red | "Handles sensitive data" |
| `timeout` | Clock | Blue | "Timeout: {n}s" |
| `retryable` | RotateCw | Green | "Auto-retry: {n} times" |
| `!concurrent_safe` | AlertTriangle | Yellow | "Not safe for parallel execution" |

---

## Best Practices

### 1. Credentials Management

```tsx
// Show credential status prominently
function CredentialIndicator({ module }: { module: ModuleMetadata }) {
  if (!module.requires_credentials) return null;

  const hasKey = checkCredentials(module);

  return (
    <div className={`credential-status ${hasKey ? 'configured' : 'missing'}`}>
      <Icon name="Key" />
      {hasKey ? (
        <span className="text-green">✓ Configured</span>
      ) : (
        <>
          <span className="text-red">⚠ Not Configured</span>
          <button onClick={() => openCredentialsDialog(module)}>
            Add API Key
          </button>
        </>
      )}
    </div>
  );
}
```

### 2. Timeout Visualization

```tsx
// Show timeout progress during execution
function TimeoutProgress({ module, elapsedTime }: Props) {
  if (!module.timeout) return null;

  const percentage = (elapsedTime / module.timeout) * 100;
  const isWarning = percentage > 80;
  const isDanger = percentage > 95;

  return (
    <div className="timeout-progress">
      <ProgressBar
        value={percentage}
        color={isDanger ? 'red' : isWarning ? 'orange' : 'blue'}
      />
      <span className={isDanger ? 'text-red' : ''}>
        {elapsedTime}s / {module.timeout}s
      </span>
    </div>
  );
}
```

### 3. Retry Feedback

```tsx
// Show retry attempts clearly
function RetryStatus({ module, attempt }: Props) {
  if (!module.retryable) return null;

  return (
    <div className="retry-status">
      <Icon name="RotateCw" className="animate-spin" />
      <span>
        Retry {attempt} of {module.max_retries}
      </span>
      <span className="retry-delay">
        Next attempt in {Math.pow(2, attempt)}s...
      </span>
    </div>
  );
}
```

### 4. Sensitive Data Masking

```tsx
// Mask sensitive output in logs
function LogOutput({ module, data }: Props) {
  const shouldMask = module.handles_sensitive_data && isComplianceMode();

  return (
    <div className="log-output">
      {shouldMask ? (
        <>
          <div className="masked-indicator">
            <Icon name="EyeOff" />
            <span>Output masked (sensitive data)</span>
          </div>
          <code>****** [Data Hidden for Compliance] ******</code>
        </>
      ) : (
        <code>{JSON.stringify(data, null, 2)}</code>
      )}
    </div>
  );
}
```

---

## Testing Recommendations

### Unit Tests

```typescript
describe('Phase 2 UI Integration', () => {
  it('should display credential badge for modules requiring credentials', () => {
    const module = {
      module_id: 'api.anthropic.chat',
      requires_credentials: true
    };

    const { getByTestId } = render(<ModuleTile module={module} />);
    expect(getByTestId('credential-badge')).toBeInTheDocument();
  });

  it('should show warning for non-concurrent-safe modules in parallel blocks', () => {
    const module = {
      module_id: 'browser.launch',
      concurrent_safe: false
    };

    const { getByText } = render(
      <ParallelBlock>
        <ModuleNode module={module} />
      </ParallelBlock>
    );

    expect(getByText(/not safe for parallel execution/i)).toBeInTheDocument();
  });
});
```

---

## Summary

Phase 2 metadata enables rich UI features:

✅ **Visual indicators** - Show credentials, timeout, retry status at a glance
✅ **Smart warnings** - Prevent invalid configurations before execution
✅ **Real-time feedback** - Display retry attempts, timeout progress
✅ **Security compliance** - Mask sensitive data, track permissions
✅ **Better UX** - Users understand module behavior upfront

**Next Steps:**
1. Implement badge components for module palette
2. Add Phase 2 fields to module configuration panels
3. Create security dashboard for compliance tracking
4. Test with real workflows

---

## Resources

- [MODULE_PHASE2_FEATURES.md](./MODULE_PHASE2_FEATURES.md) - Complete Phase 2 specification
- [MODULE_SPECIFICATION.md](./MODULE_SPECIFICATION.md) - Full module specification
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
