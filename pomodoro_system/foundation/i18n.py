import builtins


def N_(message) -> str:  # noqa
    _ = builtins.__dict__.get("_") or None

    if _ is not None:
        return _(message)
    return message
