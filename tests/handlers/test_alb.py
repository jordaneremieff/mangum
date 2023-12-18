"""
References:
1. https://docs.aws.amazon.com/lambda/latest/dg/services-alb.html
2. https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html  # noqa: E501
"""
from typing import Dict, List, Optional

import pytest

from mangum import Mangum
from mangum.handlers.alb import ALB


def get_mock_aws_alb_event(
    method,
    path,
    query_parameters: Optional[Dict[str, List[str]]],
    headers: Optional[Dict[str, List[str]]],
    body,
    body_base64_encoded,
    multi_value_headers: bool,
):
    """Return a mock AWS ELB event.

    The `query_parameters` parameter must be given in the
    `multiValueQueryStringParameters` format - and if `multi_value_headers`
    is disabled, then they are simply transformed in to the
    `queryStringParameters` format.
    Similarly for `headers`.
    If `headers` is None, then some defaults will be used.
    if `query_parameters` is None, then no query parameters will be used.
    """
    resp = {
        "requestContext": {
            "elb": {
                "targetGroupArn": (
                    "arn:aws:elasticloadbalancing:us-east-2:123456789012:"
                    "targetgroup/lambda-279XGJDqGZ5rsrHC2Fjr/49e9d65c45c6791a"
                )
            }
        },
        "httpMethod": method,
        "path": path,
        "body": body,
        "isBase64Encoded": body_base64_encoded,
    }

    if headers is None:
        headers = {
            "accept": [
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/webp,image/apng,*/*;q=0.8"
            ],
            "accept-encoding": ["gzip"],
            "accept-language": ["en-US,en;q=0.9"],
            "connection": ["keep-alive"],
            "host": ["lambda-alb-123578498.us-east-2.elb.amazonaws.com"],
            "upgrade-insecure-requests": ["1"],
            "user-agent": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            ],
            "x-amzn-trace-id": ["Root=1-5c536348-3d683b8b04734faae651f476"],
            "x-forwarded-for": ["72.12.164.125"],
            "x-forwarded-port": ["80"],
            "x-forwarded-proto": ["http"],
            "x-imforwards": ["20"],
        }

    query_parameters = {} if query_parameters is None else query_parameters

    # Only set one of `queryStringParameters`/`multiValueQueryStringParameters`
    # and one of `headers`/multiValueHeaders (per AWS docs for ALB/lambda)
    if multi_value_headers:
        resp["multiValueQueryStringParameters"] = query_parameters
        resp["multiValueHeaders"] = headers
    else:
        # Take the last query parameter/cookie (per AWS docs for ALB/lambda)
        resp["queryStringParameters"] = {
            k: (v[-1] if len(v) > 0 else []) for k, v in query_parameters.items()
        }
        resp["headers"] = {k: (v[-1] if len(v) > 0 else []) for k, v in headers.items()}

    return resp


@pytest.mark.parametrize(
    "method,path,query_parameters,headers,req_body,body_base64_encoded,"
    "query_string,scope_body,multi_value_headers",
    [
        ("GET", "/hello/world", None, None, None, False, b"", None, False),
        (
            "GET",
            "/lambda",
            {
                "q1": ["1234ABCD"],
                "q2": ["b+c"],  # not encoded
                "q3": ["b%20c"],  # encoded
                "q4": ["/some/path/"],  # not encoded
                "q5": ["%2Fsome%2Fpath%2F"],  # encoded
            },
            None,
            "",
            False,
            b"q1=1234ABCD&q2=b+c&q3=b+c&q4=%2Fsome%2Fpath%2F&q5=%2Fsome%2Fpath%2F",
            "",
            False,
        ),
        (
            "POST",
            "/",
            {"name": ["me"]},
            None,
            "field1=value1&field2=value2",
            False,
            b"name=me",
            b"field1=value1&field2=value2",
            False,
        ),
        # Duplicate query params with multi-value headers disabled:
        (
            "POST",
            "/",
            {"name": ["me", "you"]},
            None,
            None,
            False,
            b"name=you",
            None,
            False,
        ),
        #  Duplicate query params with multi-value headers enable:
        (
            "GET",
            "/my/resource",
            {"name": ["me", "you"]},
            None,
            None,
            False,
            b"name=me&name=you",
            None,
            True,
        ),
        (
            "GET",
            "",
            {"name": ["me", "you"], "pet": ["dog"]},
            None,
            None,
            False,
            b"name=me&name=you&pet=dog",
            None,
            True,
        ),
        # A 1x1 red px gif
        (
            "POST",
            "/img",
            None,
            None,
            b"R0lGODdhAQABAIABAP8AAAAAACwAAAAAAQABAAACAkQBADs=",
            True,
            b"",
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\xff\x00\x00\x00\x00\x00,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            False,
        ),
        (
            "POST",
            "/form-submit",
            None,
            None,
            b"say=Hi&to=Mom",
            False,
            b"",
            b"say=Hi&to=Mom",
            False,
        ),
    ],
)
def test_aws_alb_scope_real(
    method,
    path,
    query_parameters,
    headers,
    req_body,
    body_base64_encoded,
    query_string,
    scope_body,
    multi_value_headers,
):
    event = get_mock_aws_alb_event(
        method,
        path,
        query_parameters,
        headers,
        req_body,
        body_base64_encoded,
        multi_value_headers,
    )
    example_context = {}
    handler = ALB(event, example_context, {"api_gateway_base_path": "/"})

    scope_path = path
    if scope_path == "":
        scope_path = "/"

    assert type(handler.body) is bytes
    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": event,
        "client": ("72.12.164.125", 0),
        "headers": [
            [
                b"accept",
                b"text/html,application/xhtml+xml,application/xml;q=0.9,image/"
                b"webp,image/apng,*/*;q=0.8",
            ],
            [b"accept-encoding", b"gzip"],
            [b"accept-language", b"en-US,en;q=0.9"],
            [b"connection", b"keep-alive"],
            [b"host", b"lambda-alb-123578498.us-east-2.elb.amazonaws.com"],
            [b"upgrade-insecure-requests", b"1"],
            [
                b"user-agent",
                b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                b" (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            ],
            [b"x-amzn-trace-id", b"Root=1-5c536348-3d683b8b04734faae651f476"],
            [b"x-forwarded-for", b"72.12.164.125"],
            [b"x-forwarded-port", b"80"],
            [b"x-forwarded-proto", b"http"],
            [b"x-imforwards", b"20"],
        ],
        "http_version": "1.1",
        "method": method,
        "path": scope_path,
        "query_string": query_string,
        "raw_path": None,
        "root_path": "",
        "scheme": "http",
        "server": ("lambda-alb-123578498.us-east-2.elb.amazonaws.com", 80),
        "type": "http",
    }

    if handler.body:
        assert handler.body == scope_body
    else:
        assert handler.body == b""


@pytest.mark.parametrize("multi_value_headers_enabled", (True, False))
def test_aws_alb_set_cookies(multi_value_headers_enabled) -> None:
    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"text/plain; charset=utf-8"],
                    [b"set-cookie", b"cookie1=cookie1; Secure"],
                    [b"set-cookie", b"cookie2=cookie2; Secure"],
                ],
            }
        )
        await send({"type": "http.response.body", "body": b"Hello, world!"})

    handler = Mangum(app, lifespan="off")
    event = get_mock_aws_alb_event(
        "GET", "/test", {}, None, None, False, multi_value_headers_enabled
    )
    response = handler(event, {})

    expected_response = {
        "statusCode": 200,
        "isBase64Encoded": False,
        "body": "Hello, world!",
    }
    if multi_value_headers_enabled:
        expected_response["multiValueHeaders"] = {
            "set-cookie": ["cookie1=cookie1; Secure", "cookie2=cookie2; Secure"],
            "content-type": ["text/plain; charset=utf-8"],
        }
    else:
        expected_response["headers"] = {
            "content-type": "text/plain; charset=utf-8",
            # Should see case mutated keys to avoid duplicate keys:
            "set-cookie": "cookie1=cookie1; Secure",
            "Set-cookie": "cookie2=cookie2; Secure",
        }
    assert response == expected_response


@pytest.mark.parametrize(
    "method,content_type,raw_res_body,res_body,res_base64_encoded",
    [
        ("GET", b"text/plain; charset=utf-8", b"Hello world", "Hello world", False),
        # A 1x1 red px gif
        (
            "POST",
            b"image/gif",
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\xff\x00\x00\x00\x00\x00,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            "R0lGODdhAQABAIABAP8AAAAAACwAAAAAAQABAAACAkQBADs=",
            True,
        ),
    ],
)
def test_aws_alb_response(
    method, content_type, raw_res_body, res_body, res_base64_encoded
):
    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", content_type]],
            }
        )
        await send({"type": "http.response.body", "body": raw_res_body})

    event = get_mock_aws_alb_event(method, "/test", {}, None, None, False, False)

    handler = Mangum(app, lifespan="off")

    response = handler(event, {})
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": res_base64_encoded,
        "headers": {"content-type": content_type.decode()},
        "body": res_body,
    }


def test_aws_alb_response_extra_mime_types():
    content_type = b"application/x-yaml"
    utf_res_body = "name: 'John Doe'"
    raw_res_body = utf_res_body.encode()
    b64_res_body = "bmFtZTogJ0pvaG4gRG9lJw=="

    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", content_type]],
            }
        )
        await send({"type": "http.response.body", "body": raw_res_body})

    event = get_mock_aws_alb_event("GET", "/test", {}, None, None, False, False)

    # Test default behavior
    handler = Mangum(app, lifespan="off")
    response = handler(event, {})
    assert content_type.decode() not in handler.config["text_mime_types"]
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": True,
        "headers": {"content-type": content_type.decode()},
        "body": b64_res_body,
    }

    # Test with modified text mime types
    handler = Mangum(app, lifespan="off")
    handler.config["text_mime_types"].append(content_type.decode())
    response = handler(event, {})
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"content-type": content_type.decode()},
        "body": utf_res_body,
    }


@pytest.mark.parametrize("multi_value_headers_enabled", (True, False))
def test_aws_alb_exclude_headers(multi_value_headers_enabled) -> None:
    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"text/plain; charset=utf-8"],
                    [b"x-custom-header", b"test"],
                ],
            }
        )
        await send({"type": "http.response.body", "body": b"Hello, world!"})

    handler = Mangum(app, lifespan="off", exclude_headers=["x-custom-header"])
    event = get_mock_aws_alb_event(
        "GET", "/test", {}, None, None, False, multi_value_headers_enabled
    )
    response = handler(event, {})

    expected_response = {
        "statusCode": 200,
        "isBase64Encoded": False,
        "body": "Hello, world!",
    }
    if multi_value_headers_enabled:
        expected_response["multiValueHeaders"] = {
            "content-type": ["text/plain; charset=utf-8"],
        }
    else:
        expected_response["headers"] = {
            "content-type": "text/plain; charset=utf-8",
        }
    assert response == expected_response
