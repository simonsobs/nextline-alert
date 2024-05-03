import asyncio
import json
import time

import respx
from nextline import Nextline

from nextline_alert.emitter import Emitter


def func_success():
    time.sleep(0.001)


def func_raise():
    time.sleep(0.001)
    raise ValueError('test')


@respx.mock
async def test_emit_no_alert() -> None:
    nextline = Nextline(func_success)

    url = 'http://localhost:5000/alerts'
    platform = 'pytest'
    emitter = Emitter(url=url, platform=platform)
    assert nextline.register(emitter)

    # Mock the HTTP POST request
    route = respx.post(url).respond(status_code=200)

    # Run a script that does not raise an exception
    async with nextline:
        event = asyncio.Event()
        await nextline.run_continue_and_wait(event)

    # Assert the HTTP POST request
    assert not route.called


@respx.mock
async def test_emit_alert() -> None:
    nextline = Nextline(func_raise)

    url = 'http://localhost:5000/alerts'
    platform = 'pytest'
    emitter = Emitter(url=url, platform=platform)
    assert nextline.register(emitter)

    # Mock the HTTP POST request
    route = respx.post(url).respond(status_code=200)

    # Run a script that raises an exception
    async with nextline:
        event = asyncio.Event()
        await nextline.run_continue_and_wait(event)

    # Assert the HTTP POST request
    assert route.called
    assert len(route.calls) == 1
    call = route.calls[0]
    assert url == call.request.url
    data = json.loads(call.request.content)
    labels = data['alerts'][0]['labels']
    description = data['alerts'][0]['annotations']['description']
    assert platform == labels['platform']
    assert 'ValueError' in description
