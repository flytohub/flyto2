"""
Database Manager for Metrics Collection

Manages PostgreSQL connection using cloud database (Neon).
Zero coupling - pure function design with dependency injection.
"""

from __future__ import annotations
import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
import json


class DatabaseManager:
    """
    Manages PostgreSQL database connections and operations

    Pure, stateless component with zero coupling.
    All dependencies injected through constructor or method parameters.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize database manager

        Args:
            host: PostgreSQL host (defaults to POSTGRES_HOST env var)
            port: PostgreSQL port (defaults to POSTGRES_PORT env var)
            database: Database name (defaults to POSTGRES_DB env var)
            user: Database user (defaults to POSTGRES_USER env var)
            password: Database password (defaults to POSTGRES_PASSWORD env var)
        """
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = port or int(os.getenv("POSTGRES_PORT", "5432"))
        self.database = database or os.getenv("POSTGRES_DB", "neondb")
        self.user = user or os.getenv("POSTGRES_USER", "postgres")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "")

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections

        Yields:
            psycopg2 connection object

        Example:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode="require"
            )
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def execute_schema(self, schema_file: str) -> None:
        """
        Execute SQL schema file

        Args:
            schema_file: Path to SQL schema file
        """
        with open(schema_file, "r") as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(schema_sql)

    def insert_module_metric(
        self,
        module_name: str,
        task_description: str,
        initial_score: float,
        final_score: float,
        attempts: int,
        success: bool,
        model_used: str,
        total_time_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Insert module generation metric

        Args:
            module_name: Name of the module
            task_description: Task description
            initial_score: Initial quality score
            final_score: Final quality score
            attempts: Number of attempts
            success: Whether generation succeeded
            model_used: Model name used
            total_time_seconds: Total time taken
            metadata: Additional metadata

        Returns:
            ID of inserted record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO module_metrics (
                    module_name, task_description, initial_score, final_score,
                    attempts, success, model_used, total_time_seconds, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    module_name,
                    task_description,
                    initial_score,
                    final_score,
                    attempts,
                    success,
                    model_used,
                    total_time_seconds,
                    json.dumps(metadata) if metadata else None
                )
            )
            return cursor.fetchone()[0]

    def insert_refine_iteration(
        self,
        module_metrics_id: int,
        iteration_number: int,
        score_before: float,
        score_after: float,
        issues_before: List[Dict[str, Any]],
        issues_after: List[Dict[str, Any]],
        strategy_used: str,
        code_similarity: Optional[float] = None
    ) -> int:
        """
        Insert refine iteration metric

        Args:
            module_metrics_id: Foreign key to module_metrics
            iteration_number: Iteration number
            score_before: Score before iteration
            score_after: Score after iteration
            issues_before: Issues before iteration
            issues_after: Issues after iteration
            strategy_used: Strategy used for refinement
            code_similarity: Code similarity ratio

        Returns:
            ID of inserted record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO refine_iterations (
                    module_metrics_id, iteration_number, score_before, score_after,
                    issues_before, issues_after, strategy_used, code_similarity
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    module_metrics_id,
                    iteration_number,
                    score_before,
                    score_after,
                    json.dumps(issues_before),
                    json.dumps(issues_after),
                    strategy_used,
                    code_similarity
                )
            )
            return cursor.fetchone()[0]

    def query(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results as dictionaries

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(sql, params or ())
            return [dict(row) for row in cursor.fetchall()]

    def insert_e2e_execution(
        self,
        execution_id: str,
        task_id: str,
        task_name: str,
        status: str,
        success: bool,
        execution_time_seconds: float,
        checks_total: int,
        checks_passed: int,
        checks_failed: int,
        failed_checks: Optional[List[str]] = None,
        modules_used: Optional[List[str]] = None,
        workflow_steps: Optional[int] = None,
        error_message: Optional[str] = None,
        error_traceback: Optional[str] = None,
        agent_mode: str = "autonomous",
        llm_model: str = "gpt-4o"
    ) -> None:
        """
        Insert E2E execution metric

        Args:
            execution_id: Unique execution ID (UUID)
            task_id: Task identifier
            task_name: Task name
            status: Execution status (success/failed/error)
            success: Whether execution succeeded
            execution_time_seconds: Execution time
            checks_total: Total number of checks
            checks_passed: Number of passed checks
            checks_failed: Number of failed checks
            failed_checks: List of failed check IDs
            modules_used: List of modules used
            workflow_steps: Number of workflow steps
            error_message: Error message if failed
            error_traceback: Error traceback if failed
            agent_mode: Agent mode (autonomous/guided)
            llm_model: LLM model used
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO e2e_executions (
                    id, task_id, task_name, status, success,
                    execution_time_seconds, checks_total, checks_passed, checks_failed,
                    failed_checks, modules_used, workflow_steps,
                    error_message, error_traceback, agent_mode, llm_model
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    execution_id,
                    task_id,
                    task_name,
                    status,
                    success,
                    execution_time_seconds,
                    checks_total,
                    checks_passed,
                    checks_failed,
                    json.dumps(failed_checks) if failed_checks else None,
                    json.dumps(modules_used) if modules_used else None,
                    workflow_steps,
                    error_message,
                    error_traceback,
                    agent_mode,
                    llm_model
                )
            )

    def execute(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> int:
        """
        Execute INSERT/UPDATE/DELETE query

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            Number of rows affected
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            return cursor.rowcount
