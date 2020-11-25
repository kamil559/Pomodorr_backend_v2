import builtins
from collections import UserString


class RuntimeTranslatedString(UserString):
    def __str__(self):
        _ = builtins.__dict__.get("_")
        return str(_(self.data))

    def __repr__(self):
        _ = builtins.__dict__.get("_")
        return repr(_(self.data))


def N_(message) -> RuntimeTranslatedString:  # noqa
    return RuntimeTranslatedString(message)
