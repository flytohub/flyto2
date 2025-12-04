"""
Metrics Dashboard API Server

FastAPI server for metrics visualization and analysis.
Zero coupling - pure function design with dependency injection.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .collector import MetricsCollector
from .db_manager import DatabaseManager


app = FastAPI(
    title="Flyto2 Metrics Dashboard API",
    description="API for module generation and auto-refine metrics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModuleMetricResponse(BaseModel):
    """Response model for module metrics"""
    id: int
    module_name: str
    task_description: str
    initial_score: float
    final_score: float
    attempts: int
    success: bool
    model_used: str
    total_time_seconds: Optional[float]
    created_at: str


class SummaryStatsResponse(BaseModel):
    """Response model for summary statistics"""
    total_runs: int
    successful_runs: int
    success_rate: float
    avg_final_score: float
    avg_attempts: float
    avg_time_seconds: float
    min_score: float
    max_score: float


class ModelComparisonResponse(BaseModel):
    """Response model for model comparison"""
    model_used: str
    total_runs: int
    successful_runs: int
    success_rate: float
    avg_score: float
    avg_attempts: float
    avg_time_seconds: float


collector = MetricsCollector()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Flyto2 Metrics Dashboard API",
        "version": "1.0.0",
        "endpoints": [
            "/api/metrics/modules",
            "/api/metrics/summary",
            "/api/metrics/models"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/metrics/modules")
async def get_modules(
    limit: int = Query(100, ge=1, le=1000),
    min_score: Optional[float] = Query(None, ge=0.0, le=10.0)
) -> Dict[str, Any]:
    """
    Get recent module metrics

    Args:
        limit: Maximum number of records to return (1-1000)
        min_score: Minimum score filter (0.0-10.0, optional)

    Returns:
        Dictionary with total count and list of modules
    """
    try:
        modules = collector.get_recent_modules(
            limit=limit,
            min_score=min_score
        )

        return {
            "total": len(modules),
            "modules": modules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/modules/{module_metrics_id}/iterations")
async def get_module_iterations(
    module_metrics_id: int
) -> Dict[str, Any]:
    """
    Get all refine iterations for a module

    Args:
        module_metrics_id: Module metrics ID

    Returns:
        Dictionary with module ID and list of iterations
    """
    try:
        iterations = collector.get_module_iterations(module_metrics_id)

        return {
            "module_metrics_id": module_metrics_id,
            "total_iterations": len(iterations),
            "iterations": iterations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/summary")
async def get_summary(
    days: int = Query(30, ge=1, le=365)
) -> SummaryStatsResponse:
    """
    Get summary statistics

    Args:
        days: Number of days to look back (1-365)

    Returns:
        Summary statistics
    """
    try:
        stats = collector.get_summary_stats(days=days)
        return SummaryStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/models")
async def get_model_comparison() -> Dict[str, Any]:
    """
    Get performance comparison across different models

    Returns:
        Dictionary with list of model performance statistics
    """
    try:
        models = collector.get_model_comparison()

        return {
            "total_models": len(models),
            "models": models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/metrics/modules")
async def record_module_metric(
    module_name: str,
    task_description: str,
    initial_score: float,
    final_score: float,
    attempts: int,
    success: bool,
    model_used: str,
    total_time_seconds: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Record a new module metric

    Args:
        module_name: Name of the module
        task_description: Task description
        initial_score: Initial quality score
        final_score: Final quality score
        attempts: Number of attempts
        success: Whether generation succeeded
        model_used: Model name used
        total_time_seconds: Total time taken (optional)
        metadata: Additional metadata (optional)

    Returns:
        Dictionary with created record ID
    """
    try:
        record_id = collector.record_module_metric(
            module_name=module_name,
            task_description=task_description,
            initial_score=initial_score,
            final_score=final_score,
            attempts=attempts,
            success=success,
            model_used=model_used,
            total_time_seconds=total_time_seconds,
            metadata=metadata
        )

        return {
            "id": record_id,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RefineIterationRequest(BaseModel):
    """Request model for refine iteration"""
    module_metrics_id: int
    iteration_number: int
    score_before: float
    score_after: float
    issues_before: List[Dict[str, Any]]
    issues_after: List[Dict[str, Any]]
    strategy_used: str
    code_similarity: Optional[float] = None


@app.post("/api/metrics/iterations")
async def record_refine_iteration(
    request: RefineIterationRequest
) -> Dict[str, Any]:
    """
    Record a refine iteration

    Args:
        module_metrics_id: Foreign key to module_metrics
        iteration_number: Iteration number
        score_before: Score before iteration
        score_after: Score after iteration
        issues_before: Issues before iteration
        issues_after: Issues after iteration
        strategy_used: Strategy used for refinement
        code_similarity: Code similarity ratio (optional)

    Returns:
        Dictionary with created record ID
    """
    try:
        record_id = collector.record_refine_iteration(
            module_metrics_id=request.module_metrics_id,
            iteration_number=request.iteration_number,
            score_before=request.score_before,
            score_after=request.score_after,
            issues_before=request.issues_before,
            issues_after=request.issues_after,
            strategy_used=request.strategy_used,
            code_similarity=request.code_similarity
        )

        return {
            "id": record_id,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9002)
