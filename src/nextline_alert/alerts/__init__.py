from nextline import Nextline

from .run_failed import AlertRunFailed
from .types import EmitFunc


def register(nextline: Nextline, emit: EmitFunc) -> None:
    nextline.register(AlertRunFailed(emit))
