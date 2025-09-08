from logging import getLogger

from nextline.plugin.spec import Context, hookimpl
from nextline_alert.emitter import Emitter


class AlertRunFailed:
    '''A plugin of Nextline.

    The name of this class appears as the plugin name in the log.
    '''

    def __init__(self, emit: Emitter):
        self._emit = emit
        self._logger = getLogger(__name__)

    @hookimpl
    async def on_end_run(self, context: Context) -> None:
        if not self._is_to_emit(context):
            return

        alertname = self._compose_alertname(context)
        description = self._compose_description(context)
        await self._emit(alertname=alertname, description=description)

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
