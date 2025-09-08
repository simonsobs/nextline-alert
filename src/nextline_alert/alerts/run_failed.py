from logging import getLogger

import httpx

from nextline.plugin.spec import Context, hookimpl


class AlertRunFailed:
    '''A plugin of Nextline.

    The name of this class appears as the plugin name in the log.
    '''

    def __init__(self, url: str, platform: str):
        self._emitter = Emitter(url, platform)
        self._logger = getLogger(__name__)

    @hookimpl
    async def on_end_run(self, context: Context) -> None:
        if not self._is_to_emit(context):
            return

        alertname = self._compose_alertname(context)
        description = self._compose_description(context)
        await self._emitter.emit(alertname=alertname, description=description)

    def _is_to_emit(self, context: Context) -> bool:
        nextline = context.nextline
        fmt_exc = nextline.format_exception()
        if not fmt_exc:
            return False

        # TODO: Quick implementation to ignore KeyboardInterrupt
        #       Instead of parsing fmt_exc, store the exception type as string
        #       in RunResult in the spawned process.
        #       https://github.com/simonsobs/nextline/blob/v0.7.4/nextline/spawned/types.py#L35-L58
        if fmt_exc.rstrip().endswith('KeyboardInterrupt'):
            self._logger.info('Ignoring KeyboardInterrupt')
            return False
        return True

    def _compose_alertname(self, context: Context) -> str:
        run_arg = context.run_arg
        run_no_str = 'unknown' if run_arg is None else f'{run_arg.run_no}'
        return f'Run {run_no_str} failed'

    def _compose_description(self, context: Context) -> str:
        return context.nextline.format_exception() or ''


class Emitter:
    def __init__(self, url: str, platform: str):
        self._url = url
        self._platform = platform
        self._logger = getLogger(__name__)
        self._logger.info(f'Campana endpoint: {url}')
        self._logger.debug(f'Platform: {platform!r}')

    async def emit(self, alertname: str, description: str) -> None:
        data = self.compose_data(alertname, description)

        self._logger.info(f"Emitting alert: '{alertname}'")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self._url, json=data)
                response.raise_for_status()
        except BaseException:
            self._logger.exception(f"Failed to emit alert: '{alertname}'")
            self._logger.debug(f'Alert description: {description!r}')

    def compose_data(self, alertname: str, description: str):
        return {
            'status': 'firing',
            'alerts': [
                {
                    'status': 'firing',
                    'labels': {'alertname': alertname, 'platform': self._platform},
                    'annotations': {'description': description, 'groups': 'nextline'},
                }
            ],
        }
