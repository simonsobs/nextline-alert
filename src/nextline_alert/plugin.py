from collections.abc import Mapping

from apluggy import asynccontextmanager
from nextlinegraphql.hook import spec


class Plugin:
    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        yield
