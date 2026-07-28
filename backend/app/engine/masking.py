"""
Masking (spec 7.3): applied before any line leaves the engine, so
nothing unmasked ever reaches Redis, the database, or the browser.
"""

MASK_TOKEN = "*****"


def collect_secret_values(context: dict, mask_names: list[str]) -> list[str]:
    """Given task-level `mask: [names]` plus anything the inventory
    marked with a sibling '#encrypted' key, gather the actual secret
    strings that must be redacted from output."""
    secrets: list[str] = []
    for name in mask_names or []:
        value = context.get(name)
        if isinstance(value, str) and value:
            secrets.append(value)

    # Anything flattened as <host>_pass is always treated as sensitive,
    # regardless of whether the task explicitly listed it in `mask`.
    for key, value in context.items():
        if key.endswith("_pass") and isinstance(value, str) and value:
            secrets.append(value)

    # Deduplicate, longest first so overlapping secrets don't partially mask.
    return sorted(set(secrets), key=len, reverse=True)


def apply_masking(text: str, secret_values: list[str]) -> str:
    if not text:
        return text
    masked = text
    for secret in secret_values:
        if secret:
            masked = masked.replace(secret, MASK_TOKEN)
    return masked