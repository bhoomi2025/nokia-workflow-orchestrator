r"""
Windows-friendly test for the engine.

HOW TO RUN (Command Prompt or PowerShell):
    cd path\to\backend\backend      (the folder that contains the "app" folder)
    venv\Scripts\activate
    python test_engine_windows.py

This file should sit next to the "app" folder, NOT inside it.
"""

import os
import sys
import tempfile

sys.path.insert(0, ".")

from app.engine import run_workbook, RunOptions
from app.engine.reporting import generate_json_report, generate_text_report, generate_html_report

# A temp folder that works on both Windows and Linux/Mac.
workdir = os.path.join(tempfile.gettempdir(), "engine_test_workdir")
flag_file = os.path.join(tempfile.gettempdir(), "engine_test_flag.txt")
if os.path.exists(flag_file):
    os.remove(flag_file)

# The "flaky check" below uses a small python -c command instead of
# Linux-only "test"/"touch", so it runs the same way on Windows, Mac, and Linux.
flaky_check_command = (
    f'python -c "import os,sys; '
    f'p = r\'{flag_file}\'; '
    f'sys.exit(0) if os.path.exists(p) else (open(p, \'w\').close(), sys.exit(1))"'
)

workbook = {
    "workflows": [
        {
            "name": "deploy_check",
            "tags": ["deploy"],
            "on_error": "run_tag:rollback",
            "global_vars": {"greeting": "hello"},
            "tasks": [
                {
                    "task": "say hello",
                    "node_type": "local",
                    "command": "echo {{ greeting }} {{ target_user }}",
                    "register": "hello_result",
                    "mask": ["target_pass"],
                },
                {
                    "task": "flaky check with retries",
                    "node_type": "local",
                    "command": flaky_check_command,
                    "retries": 2,
                    "delay": 0.1,
                    "severity": "CRITICAL",
                },
                {
                    "task": "validated echo",
                    "node_type": "local",
                    "command": "echo build-success-123",
                    "validator": "output_contains",
                    "validation_arguments": {"value": "build-success-123"},
                },
                {
                    "task": "conditional skip",
                    "node_type": "local",
                    "command": "echo should not run",
                    "when": "false_flag",
                },
                {
                    "task": "block demo",
                    "block": [
                        {"task": "inner ok", "node_type": "local", "command": "echo inner-ok"},
                        {"task": "inner fail", "node_type": "local", "command": "python -c \"import sys; sys.exit(1)\""},
                    ],
                    "rescue": [
                        {"task": "rescue step", "node_type": "local", "command": "echo rescued"},
                    ],
                },
                {
                    "task": "intentional hard failure to trigger rollback",
                    "node_type": "local",
                    "command": "python -c \"import sys; sys.exit(1)\"",
                    "severity": "CRITICAL",
                },
                {
                    "task": "never reached",
                    "node_type": "local",
                    "command": "echo should-not-print",
                },
            ],
        },
        {
            "name": "rollback",
            "tags": ["rollback"],
            "tasks": [
                {"task": "rollback step", "node_type": "local", "command": "echo rolling-back"},
            ],
        },
    ]
}

inventory = {
    "hosts": {
        "target": {
            "ip": "10.0.0.5", "port": 22, "os_type": "linux", "mode": "ssh",
            "user_matrix": [{"username": "admin", "password": "supersecret123"}],
        }
    }
}

streamed_lines = []
options = RunOptions(
    workdir=workdir,
    extra_vars={"false_flag": False},
    on_output=lambda line: streamed_lines.append(line),
)

result = run_workbook(workbook, inventory, options)

print("=== RUN STATUS ===", result.status)
print("=== TASK RESULTS ===")
for t in result.task_results:
    print(f"[{t.status:8s}] {t.workflow:15s} / {t.task:45s} exit={t.exit_code} attempt={t.attempt}")
    if t.stdout.strip():
        print(f"          stdout: {t.stdout.strip()!r}")
    if t.stderr.strip():
        print(f"          stderr: {t.stderr.strip()!r}")

print("\n=== registered variable check (hello_result) ===")
print(result.variables.get("hello_result"))

print("\n=== masking check: is the ssh password anywhere in stdout/reports? ===")
json_report = generate_json_report(result)
assert "supersecret123" not in json_report, "LEAK: password found in JSON report!"
assert "supersecret123" not in "".join(streamed_lines), "LEAK: password found in streamed output!"
print("OK - password not present in JSON report or streamed output")

report_dir = os.path.join(tempfile.gettempdir(), "engine_reports")
os.makedirs(report_dir, exist_ok=True)
with open(os.path.join(report_dir, "report.json"), "w") as f:
    f.write(json_report)
with open(os.path.join(report_dir, "report.txt"), "w") as f:
    f.write(generate_text_report(result))
with open(os.path.join(report_dir, "report.html"), "w") as f:
    f.write(generate_html_report(result))

print(f"\nReports written to: {report_dir}")