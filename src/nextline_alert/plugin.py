from collections.abc import Mapping
from pathlib import Path
from typing import Optional, cast

from apluggy import asynccontextmanager
from dynaconf import Dynaconf, Validator
from nextline import Nextline
from nextlinegraphql.hook import spec

from .emitter import Emitter

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (
    Validator('ALERT.CAMPANA_URL', must_exist=True, is_type_of=str),
    Validator('ALERT.PLATFORM', must_exist=True, is_type_of=str),
)


class Plugin:
    @spec.hookimpl
    def dynaconf_preload(self) -> Optional[tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[tuple[str, ...]]:
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf):
        self._url = settings.alert.campana_url
        self._platform = settings.alert.platform

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        self._emitter = Emitter(url=self._url, platform=self._platform)
        nextline = cast(Nextline, context['nextline'])
        nextline.register(self._emitter)
        yield
