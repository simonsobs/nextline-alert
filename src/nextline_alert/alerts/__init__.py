from nextline import Nextline
from nextline_alert.emitter import Emitter

from .run_failed import AlertRunFailed


def register(nextline: Nextline, emit: Emitter) -> None:
    nextline.register(AlertRunFailed(emit))
