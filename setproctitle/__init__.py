"""Allow customization of the process title."""

import sys
import logging

logger = logging.getLogger("setproctitle")

__version__ = "1.3.0.dev0"


def setproctitle(title: str) -> None:
    logger.debug("setproctitle C module not available")
    return None


def getproctitle() -> str:
    logger.debug("setproctitle C module not available")
    return " ".join(sys.argv)


def setthreadtitle(title: str) -> None:
    logger.debug("setproctitle C module not available")
    return None


def getthreadtitle() -> str:
    logger.debug("setproctitle C module not available")
    return ""


try:
    from . import _setproctitle  # type: ignore
except ImportError as e:
    logger.debug("failed to import setproctitle: %s", e)
else:
    setproctitle = _setproctitle.setproctitle  # noqa: F811
    getproctitle = _setproctitle.getproctitle  # noqa: F811
    setthreadtitle = _setproctitle.setthreadtitle  # noqa: F811
    getthreadtitle = _setproctitle.getthreadtitle  # noqa: F811
