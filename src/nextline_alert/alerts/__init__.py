from nextline import Nextline

from .run_failed import AlertRunFailed


def register(nextline: Nextline, url: str, platform: str) -> None:
    nextline.register(AlertRunFailed(url=url, platform=platform))
