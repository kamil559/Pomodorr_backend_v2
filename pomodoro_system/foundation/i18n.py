import builtins
import gettext


def setup_i18n(language: str) -> None:
    translation = gettext.translation("messages", "pomodoro_system/locale", languages=[language])
    translation.install()


def N_(message) -> str:  # noqa
    _ = builtins.__dict__.get("_") or None

    if _ is not None:
        return _(message)
    return message
