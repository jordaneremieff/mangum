from mangum.types import (
    Scope,
    Headers,
    LambdaConfig,
    LambdaContext,
    LambdaEvent,
)


class CustomHandler:
    @classmethod
    def infer(
        cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig
    ) -> bool:
        return "my-custom-key" in event

    def __init__(
        self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig
    ) -> None:
        self.event = event
        self.context = context
        self.config = config

    @property
    def body(self) -> bytes:
        return b"My request body"

    @property
    def scope(self) -> Scope:
        headers = {}
        return {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "headers": [[k.encode(), v.encode()] for k, v in headers.items()],
            "path": "/",
            "raw_path": None,
            "root_path": "",
            "scheme": "https",
            "query_string": b"",
            "server": ("mangum", 8080),
            "client": ("127.0.0.1", 0),
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            "aws.event": self.event,
            "aws.context": self.context,
        }

    def __call__(self, *, status: int, headers: Headers, body: bytes) -> dict:
        return {"statusCode": status, "headers": {}, "body": body.decode()}


def test_custom_handler():
    event = {"my-custom-key": 1}
    handler = CustomHandler(event, {}, {"api_gateway_base_path": "/"})
    assert type(handler.body) is bytes
    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": event,
        "client": ("127.0.0.1", 0),
        "headers": [],
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "raw_path": None,
        "root_path": "",
        "scheme": "https",
        "server": ("mangum", 8080),
        "type": "http",
    }
