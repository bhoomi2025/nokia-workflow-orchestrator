"""
Workbook validation (spec section 8.2 / 7.2).

Pure Python with no framework imports, so it can be unit-tested on its own.
validate_workbook(content) -> (errors, warnings)
  errors   : problems that would break a run -> the workbook is rejected
  warnings : suspicious but allowed (e.g. a custom node_type)
"""
import json
import re

BUILTIN_NODE_TYPES = {
    "local", "ssh", "niam", "netconf",
    "api_rest", "api_restconf", "api_graphql", "api_soap",
    "api_json_rpc", "api_xml_rpc", "api_redfish",
}
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_workbook(content):
    errors: list[str] = []
    warnings: list[str] = []

    if isinstance(content, str):
        if not content.strip():
            return ["Workbook content is empty"], warnings
        try:
            content = json.loads(content)
        except json.JSONDecodeError as exc:
            return [f"Not valid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})"], warnings

    if not isinstance(content, dict):
        return ["Workbook must be a JSON object like {\"workflows\": [...]}"], warnings

    workflows = content.get("workflows")
    if not isinstance(workflows, list):
        return ["Workbook needs a \"workflows\" list"], warnings
    if not workflows:
        warnings.append("Workbook has no workflows yet")

    names: list[str] = []
    all_tags: set[str] = set()
    for wf in workflows:
        if isinstance(wf, dict):
            if isinstance(wf.get("name"), str):
                names.append(wf["name"])
            if isinstance(wf.get("tags"), list):
                all_tags.update(t for t in wf["tags"] if isinstance(t, str))

    seen: set[str] = set()
    for i, wf in enumerate(workflows):
        p = f"workflows[{i}]"
        if not isinstance(wf, dict):
            errors.append(f"{p}: must be an object")
            continue

        name = wf.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{p}: \"name\" is required")
        elif name in seen:
            errors.append(f"{p}: duplicate workflow name '{name}'")
        else:
            seen.add(name)

        tags = wf.get("tags")
        if tags is not None and (not isinstance(tags, list) or not all(isinstance(t, str) for t in tags)):
            errors.append(f"{p}: \"tags\" must be a list of text values")

        on_error = wf.get("on_error", "stop")
        if not isinstance(on_error, str):
            errors.append(f"{p}: \"on_error\" must be text")
        elif on_error in ("stop", "continue"):
            pass
        elif on_error.startswith("run_tag:"):
            tag = on_error.split(":", 1)[1].strip()
            if not tag:
                errors.append(f"{p}: on_error 'run_tag:' needs a tag name after the colon")
            elif tag not in all_tags:
                errors.append(f"{p}: on_error points to tag '{tag}' but no workflow has that tag")
        else:
            errors.append(f"{p}: on_error must be 'stop', 'continue' or 'run_tag:<tag>' (got '{on_error}')")

        deps = wf.get("depends_on")
        if deps is not None:
            if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
                errors.append(f"{p}: \"depends_on\" must be a list of workflow names")
            else:
                for d in deps:
                    if d not in names:
                        errors.append(f"{p}: depends_on '{d}' is not a workflow in this workbook")
                    elif d == name:
                        errors.append(f"{p}: a workflow cannot depend on itself")

        gv = wf.get("global_vars")
        if gv is not None and not isinstance(gv, dict):
            errors.append(f"{p}: \"global_vars\" must be an object of key/value pairs")

        tasks = wf.get("tasks", [])
        if not isinstance(tasks, list):
            errors.append(f"{p}: \"tasks\" must be a list")
            continue
        if not tasks:
            warnings.append(f"{p}: workflow has no tasks")
        _check_tasks(tasks, f"{p}.tasks", errors, warnings)

    return errors, warnings


def _check_tasks(tasks, path, errors, warnings):
    for j, task in enumerate(tasks):
        p = f"{path}[{j}]"
        if not isinstance(task, dict):
            errors.append(f"{p}: must be an object")
            continue

        has_body = any(k in task for k in ("command", "action", "block", "skip"))
        if not has_body:
            errors.append(f"{p}: needs a \"command\" or \"action\" (or a \"block\")")

        if not (task.get("task") or task.get("name")):
            warnings.append(f"{p}: no \"task\" label, reports will show 'unnamed task'")

        nt = task.get("node_type", "local")
        if not isinstance(nt, str):
            errors.append(f"{p}: \"node_type\" must be text")
        elif nt not in BUILTIN_NODE_TYPES:
            warnings.append(f"{p}: node_type '{nt}' is not built in (fine if your inventory defines it)")

        for key in ("command", "action"):
            if key in task and not isinstance(task[key], (str, dict)):
                errors.append(f"{p}: \"{key}\" must be text or an object")

        reg = task.get("register")
        if reg is not None and (not isinstance(reg, str) or not _NAME_RE.match(reg)):
            errors.append(f"{p}: \"register\" must be a simple variable name (letters, digits, underscore)")

        retries = task.get("retries")
        if retries is not None and (isinstance(retries, bool) or not isinstance(retries, int) or retries < 0):
            errors.append(f"{p}: \"retries\" must be a whole number, 0 or more")

        delay = task.get("delay")
        if delay is not None and (isinstance(delay, bool) or not isinstance(delay, (int, float)) or delay < 0):
            errors.append(f"{p}: \"delay\" must be a number of seconds, 0 or more")

        mask = task.get("mask")
        if mask is not None and (not isinstance(mask, list) or not all(isinstance(m, str) for m in mask)):
            errors.append(f"{p}: \"mask\" must be a list of variable names")

        validator = task.get("validator")
        if validator is not None and not isinstance(validator, str):
            errors.append(f"{p}: \"validator\" must be a function name (text)")

        for group in ("block", "rescue", "always"):
            if group in task:
                sub = task[group]
                if not isinstance(sub, list):
                    errors.append(f"{p}: \"{group}\" must be a list of tasks")
                else:
                    _check_tasks(sub, f"{p}.{group}", errors, warnings)
        if ("rescue" in task or "always" in task) and "block" not in task:
            errors.append(f"{p}: \"rescue\"/\"always\" only work together with a \"block\"")
