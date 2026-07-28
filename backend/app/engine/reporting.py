"""
Report generators (spec 2.3): every executed job produces three report
formats from the same RunResult -- json, text, html.
"""

import json
from html import escape

from app.engine.models import RunResult, TaskResult


def _task_to_dict(t: TaskResult) -> dict:
    return {
        "workflow": t.workflow,
        "task": t.task,
        "node_type": t.node_type,
        "status": t.status,
        "exit_code": t.exit_code,
        "stdout": t.stdout,
        "stderr": t.stderr,
        "started_at": t.started_at.isoformat(),
        "finished_at": t.finished_at.isoformat(),
        "validation_result": t.validation_result,
        "registered_variable": t.registered_variable,
        "severity": t.severity,
        "attempt": t.attempt,
    }


def generate_json_report(result: RunResult) -> str:
    payload = {
        "status": result.status,
        "started_at": result.started_at.isoformat(),
        "finished_at": result.finished_at.isoformat(),
        "error": result.error,
        "task_results": [_task_to_dict(t) for t in result.task_results],
    }
    return json.dumps(payload, indent=2)


def generate_text_report(result: RunResult) -> str:
    lines = [
        f"Run status: {result.status}",
        f"Started:    {result.started_at.isoformat()}",
        f"Finished:   {result.finished_at.isoformat()}",
        "",
    ]
    for t in result.task_results:
        lines.append(f"[{t.status.upper()}] {t.workflow} / {t.task} ({t.node_type}) - attempt {t.attempt}")
        if t.exit_code is not None:
            lines.append(f"    exit_code: {t.exit_code}")
        if t.validation_result:
            lines.append(f"    validation: {t.validation_result['passed']} - {t.validation_result['message']}")
        if t.stdout:
            lines.append(f"    stdout: {t.stdout.strip()[:500]}")
        if t.stderr:
            lines.append(f"    stderr: {t.stderr.strip()[:500]}")
        lines.append("")
    if result.error:
        lines.append(f"Run error: {result.error}")
    return "\n".join(lines)


def generate_html_report(result: RunResult) -> str:
    status_color = {"success": "#16a34a", "failed": "#dc2626", "cancelled": "#d97706", "error": "#dc2626"}.get(
        result.status, "#6b7280"
    )
    rows = []
    for t in result.task_results:
        row_color = {"success": "#16a34a", "failed": "#dc2626", "skipped": "#6b7280"}.get(t.status, "#6b7280")
        rows.append(
            f"<tr>"
            f"<td>{escape(t.workflow)}</td>"
            f"<td>{escape(t.task)}</td>"
            f"<td>{escape(t.node_type)}</td>"
            f"<td style='color:{row_color};font-weight:600'>{escape(t.status)}</td>"
            f"<td>{t.exit_code if t.exit_code is not None else '-'}</td>"
            f"<td><pre style='white-space:pre-wrap;margin:0'>{escape((t.stdout or '')[:1000])}</pre></td>"
            f"<td><pre style='white-space:pre-wrap;margin:0'>{escape((t.stderr or '')[:1000])}</pre></td>"
            f"</tr>"
        )
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Job report</title>
<style>
  body {{ font-family: -apple-system, Arial, sans-serif; margin: 2rem; color: #111827; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; font-size: 13px; }}
  th {{ background: #f9fafb; }}
</style>
</head>
<body>
  <h1>Job Report</h1>
  <p>Status: <strong style="color:{status_color}">{escape(result.status)}</strong></p>
  <p>Started: {result.started_at.isoformat()}<br>Finished: {result.finished_at.isoformat()}</p>
  <table>
    <thead>
      <tr><th>Workflow</th><th>Task</th><th>Node type</th><th>Status</th><th>Exit code</th><th>stdout</th><th>stderr</th></tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>"""