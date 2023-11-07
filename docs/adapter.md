# Adapter

The heart of Mangum is the adapter class. It is a configurable wrapper that allows any [ASGI](https://asgi.readthedocs.io/en/latest/) application (or framework) to run in an [AWS Lambda](https://aws.amazon.com/lambda/) deployment. The adapter accepts a number of keyword arguments to configure settings related to logging, HTTP responses, ASGI lifespan, and API Gateway configuration.

```python
handler = Mangum(
    app,
    lifespan="auto",
    api_gateway_base_path=None,
    custom_handlers=None,
    text_mime_types=None,
)
```

All arguments are optional.

## Configuring an adapter instance

::: mangum.adapter.Mangum
    :docstring:

## Creating an AWS Lambda handler

The adapter can be used to wrap any application without referencing the underlying methods. It defines a `__call__` method that allows the class instance to be used as an AWS Lambda event handler function. 

```python
from mangum import Mangum
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


handler = Mangum(app)
```

However, this is just one convention, you may also intercept events and construct the adapter instance separately. This may be useful if you need to implement custom event handling. The `handler` in the example above could be replaced with a function.

```python
def handler(event, context):
    if event.get("some-key"):
        # Do something or return, etc.
        return

    asgi_handler = Mangum(app)
    response = asgi_handler(event, context) # Call the instance with the event arguments

    return response
```

## Retrieving the AWS event and context

The AWS Lambda handler `event` and `context` arguments are made available to an ASGI application in the ASGI connection scope.

```python
scope['aws.event']
scope['aws.context']
```

For example, if you're using FastAPI it can be retrieved from the `scope` attribute of the request object.

```python
from fastapi import FastAPI
from mangum import Mangum
from starlette.requests import Request

app = FastAPI()


@app.get("/")
def hello(request: Request):
    return {"aws_event": request.scope["aws.event"]}

handler = Mangum(app)
```

## Creating a custom event handler

`mangum` has native support only for events coming from the following services:
* API Gateway
* HTTP Gateway
* ALB
* Lambda At The Edge

If you wish your ASGI app to handle events triggered by other AWS services, for example a SQS message, you'll need to create your own handler.

A handler must implement the `LambdaHandler` [protocol](https://peps.python.org/pep-0544/) and process the expected event message structure. Check out the [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html) for what that might look like for different services that interact with AWS Lambda.

Let's take a simple endpoint as an example: we want to trigger a POST request to a `/message` route whenever we get a message from SQS.

Let's define our custom Lambda handler in a separate file `lambda_handlers.py`.

```python
import json

from mangum.handlers.utils import (
    handle_base64_response_body,
    handle_exclude_headers,
    handle_multi_value_headers,
    maybe_encode_body,
)
from mangum.types import LambdaConfig, LambdaContext, LambdaEvent, Response, Scope


class MyCustomHandler:
    """This handler is responsible for reading and processing SQS events
    that have triggered the Lambda function.
    """

    def __init__(self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> None:
        self.event = event
        self.context = context
        self.config = config

    @classmethod
    def infer(cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> bool:
        """How to distinguish SQS events from other AWS Lambda triggers"""

        return (
            "Records" in event 
            and len(event["Records"]) > 0 
            and event["Records"][0]["eventSource"] == "aws:sqs"
        )

    @property
    def body(self) -> bytes:
        """The body of the actual REST request we want to send after getting the event."""

        message_body = self.event["Records"][0]["body"]
        request_body = json.dumps({"data": message_body, "service": "sqs"})

        return maybe_encode_body(request_body, is_base64=False)

    @property
    def scope(self) -> Scope:
        """A mapping of expected keys that Mangum adapter uses under the hood"""

        headers = [{"Content-Type": "application/json"}]
        scope: Scope = {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "headers": [[k.encode(), v.encode()] for k, v in headers.items()],
            "scheme": "https",
            "path": "/message",
            "query_string": "",
            "raw_path": None,
            "root_path": "",
            "server": ("mangum", 80),
            "client": ("", 0),
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            "aws.event": self.event,
            "aws.context": self.context,
        }
        return scope

    def __call__(self, response: Response) -> dict:
        finalized_headers, multi_value_headers = handle_multi_value_headers(response["headers"])
        finalized_body, is_base64_encoded = handle_base64_response_body(
            response["body"], finalized_headers, self.config["text_mime_types"]
        )

        return {
            "statusCode": response["status"],
            "headers": handle_exclude_headers(finalized_headers, self.config),
            "multiValueHeaders": handle_exclude_headers(multi_value_headers, self.config),
            "body": finalized_body,
            "isBase64Encoded": is_base64_encoded,
        }
```

Finally, add the custom handler to your adapter via the `custom_handlers` argument.

```python
from mangum import Mangum
from fastapi import FastAPI
from pydantic import BaseModel

from .lambda_handlers import MyCustomHandler


app = FastAPI()


class InputModel(BaseModel):
    data: str
    service: str


@app.post("/message")
def read_message(input_data: InputModel):
    return {
        "message": input_data.data,
        "service": input_data.service,
    }


handler = Mangum(app, custom_handlers=[MyCustomHandler])
```

It's also worth noting that custom handlers take precedence over in-built handlers, and the order in the list matters.

This means that if there are multiple handlers for the same service, the first one in the list wins. 
