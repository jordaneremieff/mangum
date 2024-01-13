import logging

import pytest
from quart import Quart
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from mangum import Mangum
from mangum.exceptions import LifespanFailure


@pytest.mark.parametrize(
    "mock_aws_api_gateway_event,lifespan",
    [
        (["GET", None, None], "auto"),
        (["GET", None, None], "on"),
        (["GET", None, None], "off"),
    ],
    indirect=["mock_aws_api_gateway_event"],
)
def test_lifespan(mock_aws_api_gateway_event, lifespan) -> None:
    """
    Test each lifespan option using an application that supports lifespan messages.

    * "auto" (default):
        Application support for lifespan will be inferred.

        Any error that occurs during startup will be logged and the ASGI application
        cycle will continue unless a `lifespan.startup.failed` event is sent.

    * "on":
        Application support for lifespan is explicit.

        Any error that occurs during startup will be raised and a 500 response will
        be returned.

    * "off":
        Application support for lifespan should be ignored.

        The application will not enter the lifespan cycle context.
    """
    startup_complete = False
    shutdown_complete = False

    async def app(scope, receive, send):
        nonlocal startup_complete, shutdown_complete

        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                    startup_complete = True
                elif message["type"] == "lifespan.shutdown":
                    await send({"type": "lifespan.shutdown.complete"})
                    shutdown_complete = True
                    return

        if scope["type"] == "http":
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"text/plain; charset=utf-8"]],
                }
            )
            await send({"type": "http.response.body", "body": b"Hello, world!"})

    handler = Mangum(app, lifespan=lifespan)
    response = handler(mock_aws_api_gateway_event, {})
    expected = lifespan in ("on", "auto")

    assert startup_complete == expected
    assert shutdown_complete == expected
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "multiValueHeaders": {},
        "body": "Hello, world!",
    }


@pytest.mark.parametrize(
    "mock_aws_api_gateway_event,lifespan",
    [
        (["GET", None, None], "auto"),
        (["GET", None, None], "on"),
        (["GET", None, None], "off"),
    ],
    indirect=["mock_aws_api_gateway_event"],
)
def test_lifespan_unsupported(mock_aws_api_gateway_event, lifespan) -> None:
    """
    Test each lifespan option with an application that does not support lifespan events.
    """

    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"text/plain; charset=utf-8"]],
            }
        )
        await send({"type": "http.response.body", "body": b"Hello, world!"})

    handler = Mangum(app, lifespan=lifespan)
    response = handler(mock_aws_api_gateway_event, {})

    assert response == {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "multiValueHeaders": {},
        "body": "Hello, world!",
    }


@pytest.mark.parametrize(
    "mock_aws_api_gateway_event,lifespan",
    [(["GET", None, None], "auto"), (["GET", None, None], "on")],
    indirect=["mock_aws_api_gateway_event"],
)
def test_lifespan_error(mock_aws_api_gateway_event, lifespan, caplog) -> None:
    caplog.set_level(logging.ERROR)

    async def app(scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    raise Exception("error")
        else:
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"text/plain; charset=utf-8"]],
                }
            )
            await send({"type": "http.response.body", "body": b"Hello, world!"})

    handler = Mangum(app, lifespan=lifespan)
    response = handler(mock_aws_api_gateway_event, {})

    assert "Exception in 'lifespan' protocol." in caplog.text
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "multiValueHeaders": {},
        "body": "Hello, world!",
    }


@pytest.mark.parametrize(
    "mock_aws_api_gateway_event,lifespan",
    [(["GET", None, None], "auto"), (["GET", None, None], "on")],
    indirect=["mock_aws_api_gateway_event"],
)
def test_lifespan_unexpected_message(mock_aws_api_gateway_event, lifespan) -> None:
    async def app(scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 200,
                            "headers": [
                                [b"content-type", b"text/plain; charset=utf-8"]
                            ],
                        }
                    )

    handler = Mangum(app, lifespan=lifespan)
    with pytest.raises(LifespanFailure):
        handler(mock_aws_api_gateway_event, {})


@pytest.mark.parametrize(
    "mock_aws_api_gateway_event,lifespan,failure_type",
    [
        (["GET", None, None], "auto", "startup"),
        (["GET", None, None], "on", "startup"),
        (["GET", None, None], "auto", "shutdown"),
        (["GET", None, None], "on", "shutdown"),
    ],
    indirect=["mock_aws_api_gateway_event"],
)
def test_lifespan_failure(mock_aws_api_gateway_event, lifespan, failure_type) -> None:
    async def app(scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    if failure_type == "startup":
                        await send(
                            {"type": "lifespan.startup.failed", "message": "Failed."}
                        )
                    else:
                        await send({"type": "lifespan.startup.complete"})
                if message["type"] == "lifespan.shutdown":
                    if failure_type == "shutdown":
                        await send(
                            {"type": "lifespan.shutdown.failed", "message": "Failed."}
                        )
                    await send({"type": "lifespan.shutdown.complete"})

    handler = Mangum(app, lifespan=lifespan)

    with pytest.raises(LifespanFailure):
        handler(mock_aws_api_gateway_event, {})


@pytest.mark.parametrize(
    "mock_aws_api_gateway_event", [["GET", None, None]], indirect=True
)
def test_starlette_lifespan(mock_aws_api_gateway_event) -> None:
    startup_complete = False
    shutdown_complete = False

    path = mock_aws_api_gateway_event["path"]
    app = Starlette()

    @app.on_event("startup")
    async def on_startup():
        nonlocal startup_complete
        startup_complete = True

    @app.on_event("shutdown")
    async def on_shutdown():
        nonlocal shutdown_complete
        shutdown_complete = True

    @app.route(path)
    def homepage(request):
        return PlainTextResponse("Hello, world!")

    assert not startup_complete
    assert not shutdown_complete

    handler = Mangum(app)
    mock_aws_api_gateway_event["body"] = None

    response = handler(mock_aws_api_gateway_event, {})
    assert startup_complete
    assert shutdown_complete
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {
            "content-length": "13",
            "content-type": "text/plain; charset=utf-8",
        },
        "multiValueHeaders": {},
        "body": "Hello, world!",
    }


@pytest.mark.parametrize(
    "mock_aws_api_gateway_event", [["GET", None, None]], indirect=True
)
def test_quart_lifespan(mock_aws_api_gateway_event) -> None:
    startup_complete = False
    shutdown_complete = False
    path = mock_aws_api_gateway_event["path"]
    app = Quart(__name__)

    @app.before_serving
    async def on_startup():
        nonlocal startup_complete
        startup_complete = True

    @app.after_serving
    async def on_shutdown():
        nonlocal shutdown_complete
        shutdown_complete = True

    @app.route(path)
    async def hello():
        return "hello world!"

    assert not startup_complete
    assert not shutdown_complete

    handler = Mangum(app)
    response = handler(mock_aws_api_gateway_event, {})

    assert startup_complete
    assert shutdown_complete
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"content-length": "12", "content-type": "text/html; charset=utf-8"},
        "multiValueHeaders": {},
        "body": "hello world!",
    }
