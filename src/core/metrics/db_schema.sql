-- Metrics Dashboard PostgreSQL Schema
-- Tables for tracking module generation quality and performance

-- Module Generation Metrics Table
CREATE TABLE IF NOT EXISTS module_metrics (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(255) NOT NULL,
    task_description TEXT NOT NULL,
    initial_score FLOAT NOT NULL,
    final_score FLOAT NOT NULL,
    attempts INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(50) NOT NULL,
    total_time_seconds FLOAT,
    metadata JSONB
);

-- Auto-Refine Iteration Metrics Table
CREATE TABLE IF NOT EXISTS refine_iterations (
    id SERIAL PRIMARY KEY,
    module_metrics_id INTEGER REFERENCES module_metrics(id) ON DELETE CASCADE,
    iteration_number INTEGER NOT NULL,
    score_before FLOAT NOT NULL,
    score_after FLOAT NOT NULL,
    issues_before JSONB NOT NULL,
    issues_after JSONB NOT NULL,
    strategy_used VARCHAR(50) NOT NULL,
    code_similarity FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Issue Statistics Table
CREATE TABLE IF NOT EXISTS issue_stats (
    id SERIAL PRIMARY KEY,
    issue_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    total_deduction FLOAT DEFAULT 0.0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model Performance Comparison Table
CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    total_runs INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    avg_initial_score FLOAT DEFAULT 0.0,
    avg_final_score FLOAT DEFAULT 0.0,
    avg_attempts FLOAT DEFAULT 0.0,
    avg_time_seconds FLOAT DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Convergence Events Table
CREATE TABLE IF NOT EXISTS convergence_events (
    id SERIAL PRIMARY KEY,
    module_metrics_id INTEGER REFERENCES module_metrics(id) ON DELETE CASCADE,
    convergence_reason VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    attempt_number INTEGER NOT NULL,
    score_at_convergence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- E2E Task Execution Metrics Table
CREATE TABLE IF NOT EXISTS e2e_executions (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    success BOOLEAN NOT NULL,
    execution_time_seconds FLOAT NOT NULL,
    checks_total INTEGER NOT NULL,
    checks_passed INTEGER NOT NULL,
    checks_failed INTEGER NOT NULL,
    failed_checks JSONB,
    modules_used JSONB,
    workflow_steps INTEGER,
    error_message TEXT,
    error_traceback TEXT,
    agent_mode VARCHAR(50),
    llm_model VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_module_metrics_created_at ON module_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_module_metrics_model ON module_metrics(model_used);
CREATE INDEX IF NOT EXISTS idx_module_metrics_success ON module_metrics(success);
CREATE INDEX IF NOT EXISTS idx_refine_iterations_module_id ON refine_iterations(module_metrics_id);
CREATE INDEX IF NOT EXISTS idx_issue_stats_type ON issue_stats(issue_type);
CREATE INDEX IF NOT EXISTS idx_convergence_events_module_id ON convergence_events(module_metrics_id);
CREATE INDEX IF NOT EXISTS idx_e2e_executions_task_id ON e2e_executions(task_id);
CREATE INDEX IF NOT EXISTS idx_e2e_executions_status ON e2e_executions(status);
CREATE INDEX IF NOT EXISTS idx_e2e_executions_created_at ON e2e_executions(created_at);
