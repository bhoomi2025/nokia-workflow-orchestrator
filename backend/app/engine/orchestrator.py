"""
The refactored orchestrator core (spec 7.3).

run_workbook(workbook, inventory, options) -> RunResult is a pure
function: no sys.exit(), no module-level state, no hard-coded paths.
Everything it needs arrives as an argument, so it is safe to call
concurrently from multiple worker processes.

Not yet implemented (left as clearly-marked follow-up work, not silently
skipped):
    - context_switch / interactive_responses / login_interactions
      (interactive CLI session handling) -- only meaningful once a real
      ssh/niam driver exists.
    - depends_on cross-workflow dependency ordering -- currently
      workflows run in the order given/selected; a workflow whose
      dependency failed is not automatically skipped yet.
    - True real-time line-by-line streaming for `local` -- output is
      captured by subprocess.run() and replayed line-by-line through
      on_output() after the command finishes, not as it runs. Swapping
      _run_local() to Popen + incremental readline would close this gap
      without changing any caller.
"""

import os
import re
import time
from datetime import datetime, timezone

from app.engine.comparators import run_comparator
from app.engine.connection_manager import ConnectionManager
from app.engine.masking import apply_masking, collect_secret_values
from app.engine.models import RunOptions, RunResult, TaskResult
from app.engine.validators import run_validator
from app.engine.variables import flatten_inventory, interpolate, resolve_expression


def run_workbook(workbook: dict, inventory: dict, options: RunOptions) -> RunResult:
    started_at = datetime.now(timezone.utc)
    os.makedirs(options.workdir, exist_ok=True)

    context: dict = {}
    context.update(flatten_inventory(inventory or {}))
    context.update(options.extra_vars or {})

    task_results: list[TaskResult] = []
    run_status = "success"
    run_error = None

    workflows = workbook.get("workflows", [])
    selected = _select_workflows(workflows, options)
    tasks_by_tag = _index_workflows_by_tag(workflows)

    with ConnectionManager(timeout=options.timeout) as conn_mgr:
        for workflow in selected:
            if options.should_cancel and options.should_cancel():
                run_status = "cancelled"
                break

            if workflow.get("when") and not _truthy(resolve_expression(workflow["when"], context)):
                continue

            context.update(interpolate(workflow.get("global_vars", {}) or {}, context))

            outcome = _run_workflow_tasks(workflow, context, conn_mgr, options, task_results)

            if outcome == "cancelled":
                run_status = "cancelled"
                break

            if outcome == "failed":
                on_error = workflow.get("on_error", "stop")
                if on_error == "continue":
                    continue
                if isinstance(on_error, str) and on_error.startswith("run_tag:"):
                    tag = on_error.split(":", 1)[1]
                    rollback_workflow = tasks_by_tag.get(tag)
                    if rollback_workflow:
                        _run_workflow_tasks(rollback_workflow, context, conn_mgr, options, task_results)
                    run_status = "failed"
                    break
                # default: "stop"
                run_status = "failed"
                break

    finished_at = datetime.now(timezone.utc)
    secret_values = collect_secret_values(context, mask_names=[])
    safe_vars = {
        k: (apply_masking(v, secret_values) if isinstance(v, str) else v)
        for k, v in context.items()
        if not k.endswith("_pass")
    }

    return RunResult(
        status=run_status,
        started_at=started_at,
        finished_at=finished_at,
        task_results=task_results,
        variables=safe_vars,
        error=run_error,
    )


def _select_workflows(workflows: list[dict], options: RunOptions) -> list[dict]:
    selected = workflows
    if options.workflows:
        wanted = set(options.workflows)
        selected = [w for w in selected if w.get("name") in wanted]
    if options.tags:
        wanted_tags = set(options.tags)
        selected = [w for w in selected if wanted_tags.intersection(w.get("tags", []) or [])]
    if options.skip_tags:
        skip_tags = set(options.skip_tags)
        selected = [w for w in selected if not skip_tags.intersection(w.get("tags", []) or [])]
    return selected


def _index_workflows_by_tag(workflows: list[dict]) -> dict:
    by_tag = {}
    for w in workflows:
        for tag in w.get("tags", []) or []:
            by_tag.setdefault(tag, w)
    return by_tag


def _run_workflow_tasks(workflow: dict, context: dict, conn_mgr, options: RunOptions, task_results: list) -> str:
    """Runs one workflow's task list. Returns 'success' | 'failed' | 'cancelled'."""
    workflow_name = workflow.get("name", "unnamed")
    for task in workflow.get("tasks", []) or []:
        if options.should_cancel and options.should_cancel():
            return "cancelled"

        if options.only_tasks is not None:
            if (workflow_name, task.get("task", "")) not in options.only_tasks:
                continue

        result = _execute_task(workflow_name, task, context, conn_mgr, options)
        task_results.append(result)

        if result.status == "success" and result.registered_variable:
            context.update(result.registered_variable)

        if result.status == "failed":
            severity = task.get("severity", "CRITICAL")
            if task.get("on_failure_continue"):
                continue
            if severity != "CRITICAL":
                continue
            return "failed"
    return "success"


def _execute_task(workflow_name: str, task: dict, context: dict, conn_mgr, options: RunOptions) -> TaskResult:
    task_label = task.get("task", task.get("name", "unnamed task"))
    node_type = task.get("node_type", "local")

    if task.get("skip"):
        now = datetime.now(timezone.utc)
        return TaskResult(workflow_name, task_label, node_type, "skipped", None, "", "", now, now)

    if task.get("when") and not _truthy(resolve_expression(task["when"], context)):
        now = datetime.now(timezone.utc)
        return TaskResult(workflow_name, task_label, node_type, "skipped", None, "", "", now, now)

    # block / rescue / always: nested task groups (Ansible-style).
    if task.get("block"):
        return _execute_block(workflow_name, task, context, conn_mgr, options)

    command_template = task.get("command", task.get("action", ""))
    mask_names = task.get("mask", []) or []

    retries = int(task.get("retries", 0))
    delay = float(task.get("delay", 0))
    attempts_allowed = retries + 1

    started_at = datetime.now(timezone.utc)
    last_exit_code, last_stdout, last_stderr = None, "", ""
    attempt = 0
    validation_result = None

    for attempt in range(1, attempts_allowed + 1):
        command = interpolate(command_template, context)
        host = None  # host resolution for non-local drivers is a follow-up (see connection_manager.py)
        outcome = conn_mgr.execute(node_type, host, command)
        last_exit_code, last_stdout, last_stderr = outcome.exit_code, outcome.stdout, outcome.stderr

        success = _determine_success(task, last_exit_code, last_stdout, last_stderr)

        if task.get("validator"):
            validation_result = run_validator(
                task["validator"], last_stdout, last_stderr, last_exit_code, task.get("validation_arguments", {})
            )
            success = success and validation_result["passed"]

        secret_values = collect_secret_values(context, mask_names)
        masked_stdout = apply_masking(last_stdout, secret_values)
        masked_stderr = apply_masking(last_stderr, secret_values)
        _stream(options, masked_stdout)
        _stream(options, masked_stderr)

        if success:
            break

        if task.get("break_when") and _truthy(resolve_expression(task["break_when"], {**context, "stdout": last_stdout, "stderr": last_stderr, "exit_code": last_exit_code})):
            break

        if task.get("until") and _truthy(resolve_expression(task["until"], {**context, "stdout": last_stdout, "stderr": last_stderr, "exit_code": last_exit_code})):
            break

        if attempt < attempts_allowed:
            time.sleep(delay)

    finished_at = datetime.now(timezone.utc)
    final_success = _determine_success(task, last_exit_code, last_stdout, last_stderr)
    if task.get("validator") and validation_result is not None:
        final_success = final_success and validation_result["passed"]

    registered_variable = None
    if task.get("register"):
        secret_values = collect_secret_values(context, mask_names)
        registered_variable = {
            task["register"]: {
                "stdout": apply_masking(last_stdout, secret_values),
                "stderr": apply_masking(last_stderr, secret_values),
                "exit_code": last_exit_code,
                "success": final_success,
            }
        }

    secret_values = collect_secret_values(context, mask_names)
    return TaskResult(
        workflow=workflow_name,
        task=task_label,
        node_type=node_type,
        status="success" if final_success else "failed",
        exit_code=last_exit_code,
        stdout=apply_masking(last_stdout, secret_values),
        stderr=apply_masking(last_stderr, secret_values),
        started_at=started_at,
        finished_at=finished_at,
        validation_result=validation_result,
        registered_variable=registered_variable,
        severity=task.get("severity", "CRITICAL"),
        attempt=attempt,
    )


def _execute_block(workflow_name: str, task: dict, context: dict, conn_mgr, options: RunOptions) -> TaskResult:
    """block runs normally; rescue runs on block failure; always always runs."""
    started_at = datetime.now(timezone.utc)
    block_results: list[TaskResult] = []
    block_outcome = _run_task_list(workflow_name, task.get("block", []), context, conn_mgr, options, block_results)

    if block_outcome == "failed" and task.get("rescue"):
        _run_task_list(workflow_name, task["rescue"], context, conn_mgr, options, block_results)
        block_outcome = "success"  # rescue "handled" it, mirroring Ansible semantics

    if task.get("always"):
        _run_task_list(workflow_name, task["always"], context, conn_mgr, options, block_results)

    finished_at = datetime.now(timezone.utc)
    combined_stdout = "\n".join(r.stdout for r in block_results if r.stdout)
    combined_stderr = "\n".join(r.stderr for r in block_results if r.stderr)
    return TaskResult(
        workflow=workflow_name,
        task=task.get("task", "block"),
        node_type="block",
        status="success" if block_outcome != "failed" else "failed",
        exit_code=None,
        stdout=combined_stdout,
        stderr=combined_stderr,
        started_at=started_at,
        finished_at=finished_at,
    )


def _run_task_list(workflow_name: str, tasks: list[dict], context: dict, conn_mgr, options: RunOptions, out: list) -> str:
    for t in tasks:
        result = _execute_task(workflow_name, t, context, conn_mgr, options)
        out.append(result)
        if result.status == "success" and result.registered_variable:
            context.update(result.registered_variable)
        if result.status == "failed" and not t.get("on_failure_continue"):
            return "failed"
    return "success"


def _determine_success(task: dict, exit_code, stdout: str, stderr: str) -> bool:
    error_patterns = task.get("error_patterns")
    ignore_error_patterns = task.get("ignore_error_patterns")
    success_patterns = task.get("success_patterns")
    failed_when = task.get("failed_when")

    if ignore_error_patterns and any(re.search(p, stdout or "") for p in ignore_error_patterns):
        return True
    if error_patterns and any(re.search(p, stdout or "") for p in error_patterns):
        return False
    if success_patterns:
        return any(re.search(p, stdout or "") for p in success_patterns)
    if failed_when is not None:
        return not _truthy(failed_when)
    return exit_code == 0


def _truthy(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "no")
    return bool(value)


def _stream(options: RunOptions, text: str) -> None:
    if not text or not options.on_output:
        return
    for line in text.splitlines():
        options.on_output(line)