import json


def wrap_list(value):
    return json.dumps(value if isinstance(value, list) else [value])


def unwrap_list(value):
    if not is_wrapped_list(value):
        raise RuntimeError("This is not a wrapped list")

    json_value = json.loads(value)
    if len(json_value) == 1:
        return json_value[0]
    else:
        return json_value


def is_wrapped_list(value):
    try:
        json_value = json.loads(value)
    except (TypeError, ValueError):
        return False

    return isinstance(json_value, list)
