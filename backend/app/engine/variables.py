"""
Variable interpolation and inventory flattening (spec section 2.2).

Supports:
    {{ var }}
    {{ repo.servers[0].host }}   -- dotted / bracket path resolution
    {{ some_expr + 1 }}          -- restricted eval fallback

And flattens a structured inventory (hosts + groups + user_matrix)
into <host>_ip, <host>_user, <host>_pass, etc. for backward-compatible
flat variable references.
"""

import ast
import operator
import re
from typing import Any

_VAR_PATTERN = re.compile(r"\{\{\s*(.*?)\s*\}\}")

# Deliberately tiny set of operators for the "restricted eval fallback" --
# this is NOT a general-purpose eval. No calls, no attribute access beyond
# plain dict/list indexing, no imports, no builtins.
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}
_ALLOWED_COMPARE = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class VariableResolutionError(Exception):
    pass


def resolve_path(context: dict, path: str) -> Any:
    """Resolve 'repo.servers[0].host' style dotted/bracket paths against context."""
    tokens = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    current: Any = context
    for tok in tokens:
        if tok.startswith("[") and tok.endswith("]"):
            idx = int(tok[1:-1])
            if not isinstance(current, (list, tuple)):
                raise VariableResolutionError(f"cannot index non-list at '{tok}' in '{path}'")
            current = current[idx]
        else:
            if isinstance(current, dict):
                if tok not in current:
                    raise VariableResolutionError(f"'{tok}' not found while resolving '{path}'")
                current = current[tok]
            else:
                raise VariableResolutionError(f"cannot resolve '{tok}' on non-dict while resolving '{path}'")
    return current


def _restricted_eval(expr: str, context: dict) -> Any:
    """Evaluate a small arithmetic/comparison expression against context,
    without ever calling eval()/exec() on user input."""

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in context:
                raise VariableResolutionError(f"unknown variable '{node.id}' in expression '{expr}'")
            return context[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in _ALLOWED_COMPARE:
            return _ALLOWED_COMPARE[type(node.ops[0])](_eval(node.left), _eval(node.comparators[0]))
        if isinstance(node, ast.Attribute):
            base = _eval(node.value)
            if isinstance(base, dict) and node.attr in base:
                return base[node.attr]
            raise VariableResolutionError(f"cannot access attribute '{node.attr}' in expression '{expr}'")
        if isinstance(node, ast.Subscript):
            base = _eval(node.value)
            key = _eval(node.slice) if not isinstance(node.slice, ast.Constant) else node.slice.value
            return base[key]
        raise VariableResolutionError(f"unsupported expression syntax in '{expr}'")

    parsed = ast.parse(expr, mode="eval")
    return _eval(parsed)


def resolve_expression(expr: str, context: dict) -> Any:
    """Resolve a single {{ ... }} expression: try a plain dotted/bracket
    path first (the common case), fall back to restricted eval for
    arithmetic/comparisons."""
    try:
        return resolve_path(context, expr)
    except VariableResolutionError:
        pass
    return _restricted_eval(expr, context)


def interpolate(value: Any, context: dict) -> Any:
    """Recursively interpolate {{ var }} expressions inside strings,
    lists, and dicts. Non-string scalars pass through unchanged."""
    if isinstance(value, str):
        matches = list(_VAR_PATTERN.finditer(value))
        if not matches:
            return value
        # Whole-string single expression -> preserve the resolved type
        # (e.g. {{ count }} where count is an int, not "5").
        if len(matches) == 1 and matches[0].span() == (0, len(value)):
            return resolve_expression(matches[0].group(1), context)

        def _sub(m):
            resolved = resolve_expression(m.group(1), context)
            return str(resolved)

        return _VAR_PATTERN.sub(_sub, value)
    if isinstance(value, list):
        return [interpolate(v, context) for v in value]
    if isinstance(value, dict):
        return {k: interpolate(v, context) for k, v in value.items()}
    return value


def flatten_inventory(inventory: dict) -> dict:
    """Turn a structured inventory (Appendix A.3) into a flat variable
    dict, generating <host>_ip / _port / _os_type / _mode / _user /
    _pass / _login_interactions for every host, on top of the raw
    hosts/groups structure."""
    flat: dict = {"hosts": inventory.get("hosts", {}), "groups": inventory.get("groups", {})}

    for host_name, host in (inventory.get("hosts") or {}).items():
        prefix = host_name
        flat[f"{prefix}_ip"] = host.get("ip")
        flat[f"{prefix}_port"] = host.get("port")
        flat[f"{prefix}_os_type"] = host.get("os_type")
        flat[f"{prefix}_mode"] = host.get("mode")
        flat[f"{prefix}_login_interactions"] = host.get("login_interactions")

        user_matrix = host.get("user_matrix") or []
        if user_matrix:
            first = user_matrix[0]
            flat[f"{prefix}_user"] = first.get("username")
            flat[f"{prefix}_pass"] = first.get("password")

    return flat