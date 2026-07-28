"""
ConnectionManager (spec 2.3): a single class that multiplexes
connection modes (local shell, SSH, NIAM, NETCONF, and the API_*
family) behind one `.execute()` call, so the orchestrator loop never
needs to know which transport a task is using.

Status of each node_type in this build:
    local        -- fully implemented (real subprocess execution)
    ssh          -- interface defined, not wired to a real transport yet
    niam         -- interface defined, not wired to a real transport yet
    netconf      -- interface defined, not wired to a real transport yet
    api_rest/    -- interface defined, not wired to a real transport yet
    api_restconf/
    api_graphql/
    api_soap/
    api_json_rpc/
    api_xml_rpc/
    api_redfish/

Unimplemented types return a clean, structured "not implemented" result
(exit_code=None, status="error") rather than raising, so the rest of
the task pipeline (retries, validators, masking, rollback) can still
be exercised and demoed end-to-end while a given driver is stubbed.
This is the seam where a real driver (paramiko/ncclient/requests/...)
gets dropped in later -- see _run_local for the pattern to follow.
"""

import subprocess
from dataclasses import dataclass

# node_type -> connection defaults, exposed later via GET /meta/node-types (spec 8.6).
CONNECTION_DEFAULTS = {
    "local": {"timeout": 30},
    "ssh": {"port": 22, "timeout": 30},
    "niam": {"timeout": 30},
    "netconf": {"port": 830, "timeout": 30},
    "api_rest": {"timeout": 30},
    "api_restconf": {"timeout": 30},
    "api_graphql": {"timeout": 30},
    "api_soap": {"timeout": 30},
    "api_json_rpc": {"timeout": 30},
    "api_xml_rpc": {"timeout": 30},
    "api_redfish": {"timeout": 30},
}

IMPLEMENTED_NODE_TYPES = {"local"}


@dataclass
class ExecOutcome:
    exit_code: int | None
    stdout: str
    stderr: str


class ConnectionManager:
    """Scoped to a single job's execution. Call `.execute()` per task;
    call `.close()` (or use as a context manager) when the job ends so
    any connections opened along the way are always closed, mirroring
    spec 7.4's isolation guarantee."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._open_connections: list = []  # placeholder for future ssh/netconf session objects

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        for conn in self._open_connections:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 -- best-effort cleanup
                pass
        self._open_connections = []

    def execute(self, node_type: str, host: dict | None, command: str) -> ExecOutcome:
        if node_type == "local":
            return self._run_local(command)
        if node_type in IMPLEMENTED_NODE_TYPES:
            raise AssertionError(f"'{node_type}' marked implemented but has no handler")
        return ExecOutcome(
            exit_code=None,
            stdout="",
            stderr=(
                f"node_type '{node_type}' is not wired up in this build yet -- only "
                f"'local' has a real driver. See app/engine/connection_manager.py."
            ),
        )

    def _run_local(self, command: str) -> ExecOutcome:
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return ExecOutcome(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        except subprocess.TimeoutExpired:
            return ExecOutcome(exit_code=None, stdout="", stderr=f"command timed out after {self.timeout}s")
        except Exception as exc:  # noqa: BLE001 -- surfaced as a task failure, not a crash
            return ExecOutcome(exit_code=None, stdout="", stderr=f"local execution error: {exc}")