"""
Data structures passed into and out of run_workbook().

Kept as plain dataclasses (not Pydantic) so the engine has zero
dependency on the web framework layer -- it only knows about dicts,
dataclasses, and stdlib. The API layer is responsible for translating
to/from its own Pydantic schemas (app/schemas/*).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional


@dataclass
class RunOptions:
    """
    Explicit, per-call configuration. Everything the old CLI read from
    argparse/env now arrives here instead, so run_workbook() can be
    called many times concurrently from different worker processes
    with no shared state.
    """

    # Working directory unique to this job -- e.g. workspace/{job_id}/.
    # The engine writes nothing outside this directory.
    workdir: str

    # Which workflows (by name) to run, in order. Empty list = all
    # workflows in the workbook, in file order.
    workflows: list[str] = field(default_factory=list)

    # Tag filters, mirroring --tags / --skip-tags.
    tags: list[str] = field(default_factory=list)
    skip_tags: list[str] = field(default_factory=list)

    # Ad-hoc key=value overrides, mirroring --var.
    extra_vars: dict[str, Any] = field(default_factory=dict)

    # Per-job timeout in seconds for any single task's connection, mirroring --timeout.
    timeout: int = 30

    # Who triggered this run (mirrors --execution-user); recorded in reports, not used for auth here.
    execution_user: Optional[str] = None

    # If set, restrict this run to only these (workflow_name, task_name) pairs
    # -- used by "retry failed tasks".
    only_tasks: Optional[list[tuple[str, str]]] = None

    # Called with each new line of (already-masked) output as it is produced,
    # so a caller (e.g. the Celery task) can publish it to Redis pub/sub for
    # the live WebSocket view. No-op by default.
    on_output: Optional[Callable[[str], None]] = None

    # Polled between tasks (and, where a driver supports it, mid-task).
    # Return True to stop the run and mark it cancelled. No-op by default.
    should_cancel: Optional[Callable[[], bool]] = None


@dataclass
class TaskResult:
    """One row of what the spec calls `job_results`: the structured
    record produced by every executed task."""

    workflow: str
    task: str
    node_type: str
    status: str  # success | failed | skipped | cancelled | error
    exit_code: Optional[int]
    stdout: str
    stderr: str
    started_at: datetime
    finished_at: datetime
    validation_result: Optional[dict] = None
    registered_variable: Optional[dict] = None  # {name: value}, post-masking
    severity: Optional[str] = None
    attempt: int = 1


@dataclass
class RunResult:
    """Everything produced by one call to run_workbook()."""

    status: str  # success | failed | cancelled | error
    started_at: datetime
    finished_at: datetime
    task_results: list[TaskResult] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)  # final variable state (masked)
    error: Optional[str] = None