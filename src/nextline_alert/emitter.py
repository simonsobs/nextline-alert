import traceback
from logging import getLogger

import httpx
from nextline.plugin.spec import Context, hookimpl


class Emitter:
    def __init__(self, url: str, platform: str):
        self._url = url
        self._platform = platform
        self._logger = getLogger(__name__)
        self._logger.info(f'Campana endpoint: {url}')
        self._logger.debug(f'Platform: {platform!r}')

    @hookimpl
    async def on_end_run(self, context: Context) -> None:
        run_arg = context.run_arg
        nextline = context.nextline
        if e := nextline.exception():
            run_no_str = 'unknown' if run_arg is None else f'{run_arg.run_no}'
            alertname = f'Run {run_no_str} failed'
            desc = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            self._logger.info(f"Emitting alert: '{alertname}'")
            labels = {'alertname': alertname, 'platform': self._platform}
            try:
                await emit(url=self._url, labels=labels, description=desc)
            except BaseException:
                self._logger.exception(f"Failed to emit alert: '{alertname}'")
                self._logger.debug(f'Alert description: {desc!r}')


async def emit(url: str, labels: dict[str, str], description: str) -> None:
    data = {
        'status': 'firing',
        'alerts': [
            {
                'status': 'firing',
                'labels': labels,
                'annotations': {'description': description, 'groups': 'nextline'},
            }
        ],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
