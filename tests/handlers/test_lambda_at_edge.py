import urllib.parse

import pytest

from mangum import Mangum
from mangum.handlers.lambda_at_edge import LambdaAtEdge


def mock_lambda_at_edge_event(
    method, path, multi_value_query_parameters, body, body_base64_encoded
):
    headers_raw = {
        "accept-encoding": "gzip,deflate",
        "x-forwarded-port": "443",
        "x-forwarded-for": "192.168.100.1",
        "x-forwarded-proto": "https",
        "host": "test.execute-api.us-west-2.amazonaws.com",
    }
    headers = {}
    for key, value in headers_raw.items():
        headers[key.lower()] = [{"key": key, "value": value}]

    event = {
        "Records": [
            {
                "cf": {
                    "config": {
                        "distributionDomainName": "mock-distribution.local.localhost",
                        "distributionId": "ABC123DEF456G",
                        "eventType": "origin-request",
                        "requestId": "lBEBo2N0JKYUP2JXwn_4am2xAXB2GzcL2FlwXI8G59PA8wghF2ImFQ==",  # noqa: E501
                    },
                    "request": {
                        "clientIp": "192.168.100.1",
                        "headers": headers,
                        "method": method,
                        "origin": {
                            "custom": {
                                "customHeaders": {
                                    "x-lae-env-custom-var": [
                                        {
                                            "key": "x-lae-env-custom-var",
                                            "value": "environment variable",
                                        }
                                    ],
                                },
                                "domainName": "www.example.com",
                                "keepaliveTimeout": 5,
                                "path": "",
                                "port": 80,
                                "protocol": "http",
                                "readTimeout": 30,
                                "sslProtocols": ["TLSv1", "TLSv1.1", "TLSv1.2"],
                            }
                        },
                        "querystring": urllib.parse.urlencode(
                            multi_value_query_parameters
                            if multi_value_query_parameters
                            else {},
                            doseq=True,
                        ),
                        "uri": path,
                    },
                }
            }
        ]
    }

    if body is not None:
        event["Records"][0]["cf"]["request"]["body"] = {
            "inputTruncated": False,
            "action": "read-only",
            "encoding": "base64" if body_base64_encoded else "text",
            "data": body,
        }
    return event


def test_aws_cf_lambda_at_edge_scope_basic():
    """
    Test the event from the AWS docs
    """
    example_event = {
        "Records": [
            {
                "cf": {
                    "config": {
                        "distributionDomainName": "d111111abcdef8.cloudfront.net",
                        "distributionId": "EDFDVBD6EXAMPLE",
                        "eventType": "origin-request",
                        "requestId": "4TyzHTaYWb1GX1qTfsHhEqV6HUDd_BzoBZnwfnvQc_1oF26ClkoUSEQ==",  # noqa: E501
                    },
                    "request": {
                        "clientIp": "203.0.113.178",
                        "headers": {
                            "x-forwarded-for": [
                                {"key": "X-Forwarded-For", "value": "203.0.113.178"}
                            ],
                            "user-agent": [
                                {"key": "User-Agent", "value": "Amazon CloudFront"}
                            ],
                            "via": [
                                {
                                    "key": "Via",
                                    "value": "2.0 2afae0d44e2540f472c0635ab62c232b.cloudfront.net (CloudFront)",  # noqa: E501
                                }
                            ],
                            "host": [{"key": "Host", "value": "example.org"}],
                            "cache-control": [
                                {
                                    "key": "Cache-Control",
                                    "value": "no-cache, cf-no-cache",
                                }
                            ],
                        },
                        "method": "GET",
                        "origin": {
                            "custom": {
                                "customHeaders": {},
                                "domainName": "example.org",
                                "keepaliveTimeout": 5,
                                "path": "",
                                "port": 443,
                                "protocol": "https",
                                "readTimeout": 30,
                                "sslProtocols": ["TLSv1", "TLSv1.1", "TLSv1.2"],
                            }
                        },
                        "querystring": "",
                        "uri": "/",
                    },
                }
            }
        ]
    }
    example_context = {}
    handler = LambdaAtEdge(
        example_event, example_context, {"api_gateway_base_path": "/"}
    )

    assert type(handler.body) is bytes
    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": example_event,
        "client": ("203.0.113.178", 0),
        "headers": [
            [b"x-forwarded-for", b"203.0.113.178"],
            [b"user-agent", b"Amazon CloudFront"],
            [
                b"via",
                b"2.0 2afae0d44e2540f472c0635ab62c232b.cloudfront.net (CloudFront)",
            ],
            [b"host", b"example.org"],
            [b"cache-control", b"no-cache, cf-no-cache"],
        ],
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "raw_path": None,
        "root_path": "",
        "scheme": "https",
        "server": ("example.org", 80),
        "type": "http",
    }


@pytest.mark.parametrize(
    "method,path,multi_value_query_parameters,req_body,"
    "body_base64_encoded,query_string,scope_body",
    [
        ("GET", "/hello/world", None, None, False, b"", None),
        (
            "POST",
            "/",
            {"name": ["me"]},
            "field1=value1&field2=value2",
            False,
            b"name=me",
            b"field1=value1&field2=value2",
        ),
        (
            "GET",
            "/my/resource",
            {"name": ["me", "you"]},
            None,
            False,
            b"name=me&name=you",
            None,
        ),
        (
            "GET",
            "",
            {"name": ["me", "you"], "pet": ["dog"]},
            None,
            False,
            b"name=me&name=you&pet=dog",
            None,
        ),
        # A 1x1 red px gif
        (
            "POST",
            "/img",
            None,
            b"R0lGODdhAQABAIABAP8AAAAAACwAAAAAAQABAAACAkQBADs=",
            True,
            b"",
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\xff\x00\x00\x00\x00\x00,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        ),
        ("POST", "/form-submit", None, b"say=Hi&to=Mom", False, b"", b"say=Hi&to=Mom"),
    ],
)
def test_aws_api_gateway_scope_real(
    method,
    path,
    multi_value_query_parameters,
    req_body,
    body_base64_encoded,
    query_string,
    scope_body,
):
    event = mock_lambda_at_edge_event(
        method, path, multi_value_query_parameters, req_body, body_base64_encoded
    )
    example_context = {}
    handler = LambdaAtEdge(event, example_context, {"api_gateway_base_path": "/"})

    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": event,
        "client": ("192.168.100.1", 0),
        "headers": [
            [b"accept-encoding", b"gzip,deflate"],
            [b"x-forwarded-port", b"443"],
            [b"x-forwarded-for", b"192.168.100.1"],
            [b"x-forwarded-proto", b"https"],
            [b"host", b"test.execute-api.us-west-2.amazonaws.com"],
        ],
        "http_version": "1.1",
        "method": method,
        "path": path,
        "query_string": query_string,
        "raw_path": None,
        "root_path": "",
        "scheme": "https",
        "server": ("test.execute-api.us-west-2.amazonaws.com", 443),
        "type": "http",
    }

    if handler.body:
        assert handler.body == scope_body
    else:
        assert handler.body == b""


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
def test_aws_lambda_at_edge_response(
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

    event = mock_lambda_at_edge_event(method, "/test", {}, None, False)

    handler = Mangum(app, lifespan="off")

    response = handler(event, {})
    assert response == {
        "status": 200,
        "isBase64Encoded": res_base64_encoded,
        "headers": {
            "content-type": [{"key": "content-type", "value": content_type.decode()}]
        },
        "body": res_body,
    }


def test_aws_lambda_at_edge_response_extra_mime_types():
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

    event = mock_lambda_at_edge_event("POST", "/test", {}, None, False)

    # Test default behavior
    handler = Mangum(app, lifespan="off")
    response = handler(event, {})
    assert content_type.decode() not in handler.config["text_mime_types"]
    assert response == {
        "status": 200,
        "isBase64Encoded": True,
        "headers": {
            "content-type": [{"key": "content-type", "value": content_type.decode()}]
        },
        "body": b64_res_body,
    }

    # Test with modified text mime types
    handler = Mangum(app, lifespan="off")
    handler.config["text_mime_types"].append(content_type.decode())
    response = handler(event, {})
    assert response == {
        "status": 200,
        "isBase64Encoded": False,
        "headers": {
            "content-type": [{"key": "content-type", "value": content_type.decode()}]
        },
        "body": utf_res_body,
    }


def test_aws_lambda_at_edge_exclude_():
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
        await send({"type": "http.response.body", "body": b"Hello world"})

    event = mock_lambda_at_edge_event("GET", "/test", {}, None, False)

    handler = Mangum(app, lifespan="off", exclude_headers=["x-custom-header"])

    response = handler(event, {})
    assert response == {
        "status": 200,
        "isBase64Encoded": False,
        "headers": {
            "content-type": [
                {"key": "content-type", "value": b"text/plain; charset=utf-8".decode()}
            ]
        },
        "body": "Hello world",
    }
