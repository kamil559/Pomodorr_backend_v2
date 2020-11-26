import builtins
import gettext


def setup_i18n(language: str) -> None:
    t = gettext.translation("messages", "locale", languages=[language])
    t.install()


def N_(message) -> str:  # noqa
    _ = builtins.__dict__.get("_") or None

    if _ is not None:
        return _(message)
    return message
