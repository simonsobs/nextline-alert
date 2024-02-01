from collections.abc import Mapping
from pathlib import Path
from typing import Optional

from apluggy import asynccontextmanager
from nextlinegraphql.hook import spec
from dynaconf import Dynaconf, Validator


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (Validator("ALERT.CAMPANA_URL", must_exist=True, is_type_of=str),)


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
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        yield
