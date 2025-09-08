import asyncio
import json
import logging
import time

import pytest
import respx

from nextline import Nextline
from nextline_alert.emitter import AlertRunFailed


def func_success():  # pragma: no cover
    time.sleep(0.001)


def func_raise_ignore():  # pragma: no cover
    time.sleep(0.001)
    raise KeyboardInterrupt


def func_raise():  # pragma: no cover
    time.sleep(0.001)
    raise ValueError('test')


@respx.mock
@pytest.mark.parametrize('func', [func_success, func_raise_ignore])
async def test_emit_no_alert(func) -> None:
    nextline = Nextline(func)

    url = 'http://localhost:5000/alerts'
    platform = 'pytest'
    emitter = AlertRunFailed(url=url, platform=platform)
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
    emitter = AlertRunFailed(url=url, platform=platform)
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


@respx.mock
async def test_emit_exception(caplog: pytest.LogCaptureFixture) -> None:
    nextline = Nextline(func_raise)

    url = 'http://localhost:5000/alerts'
    platform = 'pytest'
    emitter = AlertRunFailed(url=url, platform=platform)
    assert nextline.register(emitter)

    # Mock the HTTP POST request
    route = respx.post(url).respond(status_code=500)

    # Run a script that raises an exception and fails to emit an alert
    with caplog.at_level(logging.ERROR):
        async with nextline:
            event = asyncio.Event()
            await nextline.run_continue_and_wait(event)

    # Assert the log message
    records = [r for r in caplog.records if r.name == AlertRunFailed.__module__]
    assert len(records) == 1
    assert records[0].levelname == 'ERROR'
    assert 'Failed to emit alert' in records[0].message

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
