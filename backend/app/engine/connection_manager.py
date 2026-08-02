"""
ConnectionManager (spec 2.3): a single class that multiplexes
connection modes (local shell, SSH, NIAM, NETCONF, and the API_*
family) behind one `.execute()` call, so the orchestrator loop never
needs to know which transport a task is using.

Status of each node_type in this build:
    local        -- fully implemented (real subprocess execution)
    ssh          -- fully implemented (real paramiko transport)
    niam         -- interface defined, not wired to a real transport yet
    netconf      -- interface defined, not wired to a real transport yet
    api_rest/    -- interface defined, not wired to a real transport yet
    api_restconf/
    api_graphql/
    api_soap/
    api_json_rpc/
    api_xml_rpc/
    api_redfish/
"""
import subprocess
import paramiko
from dataclasses import dataclass

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

IMPLEMENTED_NODE_TYPES = {"local", "ssh"}


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
        self._open_connections: list = []
        self._ssh_clients: dict = {}  # host key -> paramiko.SSHClient, reused across tasks in the same job

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        for conn in self._open_connections:
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass
        for client in self._ssh_clients.values():
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass
        self._open_connections = []
        self._ssh_clients = {}

    def execute(self, node_type: str, host: dict | None, command: str) -> ExecOutcome:
        if node_type == "local":
            return self._run_local(command)
        if node_type == "ssh":
            return self._run_ssh(host, command)
        if node_type in IMPLEMENTED_NODE_TYPES:
            raise AssertionError(f"'{node_type}' marked implemented but has no handler")
        return ExecOutcome(
            exit_code=None,
            stdout="",
            stderr=(
                f"node_type '{node_type}' is not wired up in this build yet -- only "
                f"'local' and 'ssh' have a real driver. See app/engine/connection_manager.py."
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
        except Exception as exc:  # noqa: BLE001
            return ExecOutcome(exit_code=None, stdout="", stderr=f"local execution error: {exc}")

    def _get_ssh_client(self, host: dict) -> paramiko.SSHClient:
        """host is expected to look like:
        {
          "ip": "1.2.3.4",
          "port": 22,
          "user_matrix": [{"username": "...", "password": "..."}]
        }
        Reuses one connection per host for the lifetime of this job,
        instead of reconnecting for every single task."""
        key = f"{host.get('ip')}:{host.get('port', 22)}"
        if key in self._ssh_clients:
            return self._ssh_clients[key]

        creds = (host.get("user_matrix") or [{}])[0]
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host.get("ip"),
            port=int(host.get("port", 22)),
            username=creds.get("username"),
            password=creds.get("password"),
            timeout=self.timeout,
        )
        self._ssh_clients[key] = client
        return client

    def _run_ssh(self, host: dict | None, command: str) -> ExecOutcome:
        if not host or not host.get("ip"):
            return ExecOutcome(exit_code=None, stdout="", stderr="ssh task has no host/ip resolved")
        try:
            client = self._get_ssh_client(host)
            stdin, stdout, stderr = client.exec_command(command, timeout=self.timeout)
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode(errors="replace")
            err = stderr.read().decode(errors="replace")
            return ExecOutcome(exit_code=exit_code, stdout=out, stderr=err)
        except paramiko.AuthenticationException:
            return ExecOutcome(exit_code=None, stdout="", stderr="ssh authentication failed")
        except Exception as exc:  # noqa: BLE001
            return ExecOutcome(exit_code=None, stdout="", stderr=f"ssh execution error: {exc}")        
