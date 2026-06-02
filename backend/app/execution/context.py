from typing import Any


def resolve_path(payload: dict[str, Any], path: str) -> Any:
    if path == "$":
        return payload
    if not path.startswith("$."):
        return path
    current: Any = payload
    for part in path[2:].split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def render_template(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        rendered = value
        for key, item in context.items():
            token = "{{ " + key + " }}"
            rendered = rendered.replace(token, str(item))
        return rendered
    if isinstance(value, list):
        return [render_template(item, context) for item in value]
    if isinstance(value, dict):
        return {key: render_template(item, context) for key, item in value.items()}
    return value
