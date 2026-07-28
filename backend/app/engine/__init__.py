"""
Workflow Orchestrator execution engine.

This package is the refactored, importable core described in spec
section 7.3: a pure function `run_workbook(workbook, inventory, options)`
with no process-global state, no sys.exit(), and no hard-coded file
paths. Celery workers import `run_workbook` directly instead of
shelling out to a CLI.

Public API:
    run_workbook(workbook: dict, inventory: dict, options: RunOptions) -> RunResult
"""

from app.engine.orchestrator import run_workbook
from app.engine.models import RunOptions, RunResult, TaskResult

__all__ = ["run_workbook", "RunOptions", "RunResult", "TaskResult"]