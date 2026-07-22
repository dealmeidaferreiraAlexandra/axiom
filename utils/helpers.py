# utils/helpers.py

import logging

_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Return a module logger, configuring a default handler once.

    Using logging instead of print keeps otherwise-swallowed errors visible
    (with severity, timestamps and, when needed, tracebacks) without crashing
    the app.
    """
    global _CONFIGURED

    if not _CONFIGURED:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        _CONFIGURED = True

    return logging.getLogger(name)
