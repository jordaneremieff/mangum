import urllib.parse

import pytest

from mangum import Mangum
from mangum.handlers.api_gateway import HTTPGateway


def get_mock_aws_http_gateway_event_v1(
    method, path, query_parameters, body, body_base64_encoded
):
    query_string = urllib.parse.urlencode(query_parameters if query_parameters else {})
    return {
        "version": "1.0",
        "resource": path,
        "path": path,
        "httpMethod": method,
        "headers": {
            "accept-encoding": "gzip,deflate",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
            "host": "test.execute-api.us-west-2.amazonaws.com",
        },
        "multiValueHeaders": {
            "accept-encoding": ["gzip", "deflate"],
            "x-forwarded-port": ["443"],
            "x-forwarded-proto": ["https"],
            "host": ["test.execute-api.us-west-2.amazonaws.com"],
        },
        "queryStringParameters": {k: v[0] for k, v in query_parameters.items()}
        if query_parameters
        else {},
        "multiValueQueryStringParameters": {k: v for k, v in query_parameters.items()}
        if query_parameters
        else {},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "id",
            "authorizer": {"claims": None, "scopes": None},
            "domainName": "id.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "id",
            "extendedRequestId": "request-id",
            "httpMethod": method,
            "identity": {
                "accessKey": None,
                "accountId": None,
                "caller": None,
                "cognitoAuthenticationProvider": None,
                "cognitoAuthenticationType": None,
                "cognitoIdentityId": None,
                "cognitoIdentityPoolId": None,
                "principalOrgId": None,
                "sourceIp": "192.168.100.1",
                "user": None,
                "userAgent": "user-agent",
                "userArn": None,
                "clientCert": {
                    "clientCertPem": "CERT_CONTENT",
                    "subjectDN": "www.example.com",
                    "issuerDN": "Example issuer",
                    "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                    "validity": {
                        "notBefore": "May 28 12:30:02 2019 GMT",
                        "notAfter": "Aug  5 09:36:04 2021 GMT",
                    },
                },
            },
            "path": path,
            "protocol": "HTTP/1.1",
            "requestId": "id=",
            "requestTime": "04/Mar/2020:19:15:17 +0000",
            "requestTimeEpoch": 1583349317135,
            "resourceId": None,
            "resourcePath": path,
            "stage": "$default",
        },
        "pathParameters": query_string,
        "stageVariables": None,
        "body": body,
        "isBase64Encoded": body_base64_encoded,
    }


def get_mock_aws_http_gateway_event_v2(
    method, path, query_parameters, body, body_base64_encoded
):
    query_string = urllib.parse.urlencode(query_parameters if query_parameters else {})
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": query_string,
        "cookies": ["cookie1", "cookie2"],
        "headers": {
            "accept-encoding": "gzip,deflate",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
            "host": "test.execute-api.us-west-2.amazonaws.com",
        },
        "queryStringParameters": {k: v[0] for k, v in query_parameters.items()}
        if query_parameters
        else {},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "authorizer": {
                "jwt": {
                    "claims": {"claim1": "value1", "claim2": "value2"},
                    "scopes": ["scope1", "scope2"],
                }
            },
            "domainName": "id.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "id",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "192.168.100.1",
                "userAgent": "agent",
            },
            "requestId": "id",
            "routeKey": "$default",
            "stage": "$default",
            "time": "12/Mar/2020:19:03:58 +0000",
            "timeEpoch": 1583348638390,
        },
        "body": body,
        "pathParameters": {"parameter1": "value1"},
        "isBase64Encoded": body_base64_encoded,
        "stageVariables": {"stageVariable1": "value1", "stageVariable2": "value2"},
    }


def test_aws_http_gateway_scope_basic_v1():
    """
    Test the event from the AWS docs
    """
    example_event = {
        "version": "1.0",
        "resource": "/my/path",
        "path": "/my/path",
        "httpMethod": "GET",
        "headers": {"Header1": "value1", "Header2": "value2"},
        "multiValueHeaders": {"Header1": ["value1"], "Header2": ["value1", "value2"]},
        "queryStringParameters": {"parameter1": "value1", "parameter2": "value"},
        "multiValueQueryStringParameters": {
            "parameter1": ["value1", "value2"],
            "parameter2": ["value"],
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "id",
            "authorizer": {"claims": None, "scopes": None},
            "domainName": "id.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "id",
            "extendedRequestId": "request-id",
            "httpMethod": "GET",
            "identity": {
                "accessKey": None,
                "accountId": None,
                "caller": None,
                "cognitoAuthenticationProvider": None,
                "cognitoAuthenticationType": None,
                "cognitoIdentityId": None,
                "cognitoIdentityPoolId": None,
                "principalOrgId": None,
                "sourceIp": "IP",
                "user": None,
                "userAgent": "user-agent",
                "userArn": None,
                "clientCert": {
                    "clientCertPem": "CERT_CONTENT",
                    "subjectDN": "www.example.com",
                    "issuerDN": "Example issuer",
                    "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                    "validity": {
                        "notBefore": "May 28 12:30:02 2019 GMT",
                        "notAfter": "Aug  5 09:36:04 2021 GMT",
                    },
                },
            },
            "path": "/my/path",
            "protocol": "HTTP/1.1",
            "requestId": "id=",
            "requestTime": "04/Mar/2020:19:15:17 +0000",
            "requestTimeEpoch": 1583349317135,
            "resourceId": None,
            "resourcePath": "/my/path",
            "stage": "$default",
        },
        "pathParameters": None,
        "stageVariables": None,
        "body": "Hello from Lambda!",
        "isBase64Encoded": False,
    }

    example_context = {}
    handler = HTTPGateway(
        example_event, example_context, {"api_gateway_base_path": "/"}
    )

    assert type(handler.body) is bytes
    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": example_event,
        "client": ("IP", 0),
        "headers": [[b"header1", b"value1"], [b"header2", b"value1, value2"]],
        "http_version": "1.1",
        "method": "GET",
        "path": "/my/path",
        "query_string": b"parameter1=value1&parameter1=value2&parameter2=value",
        "raw_path": None,
        "root_path": "",
        "scheme": "https",
        "server": ("mangum", 80),
        "type": "http",
    }


def test_aws_http_gateway_scope_v1_only_non_multi_headers():
    """
    Ensure only queryStringParameters headers still works (unsure if this is possible
    from HTTP Gateway)
    """
    example_event = get_mock_aws_http_gateway_event_v1(
        "GET", "/test", {"hello": ["world", "life"]}, None, False
    )
    del example_event["multiValueQueryStringParameters"]
    example_context = {}
    handler = HTTPGateway(
        example_event, example_context, {"api_gateway_base_path": "/"}
    )
    assert handler.scope["query_string"] == b"hello=world"


def test_aws_http_gateway_scope_v1_no_headers():
    """
    Ensure no headers still works (unsure if this is possible from HTTP Gateway)
    """
    example_event = get_mock_aws_http_gateway_event_v1(
        "GET", "/test", {"hello": ["world", "life"]}, None, False
    )
    del example_event["multiValueQueryStringParameters"]
    del example_event["queryStringParameters"]
    example_context = {}
    handler = HTTPGateway(
        example_event, example_context, {"api_gateway_base_path": "/"}
    )
    assert handler.scope["query_string"] == b""


def test_aws_http_gateway_scope_basic_v2():
    """
    Test the event from the AWS docs
    """
    example_event = {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/my/path",
        "rawQueryString": "parameter1=value1&parameter1=value2&parameter2=value",
        "cookies": ["cookie1", "cookie2"],
        "headers": {"Header1": "value1", "Header2": "value1,value2"},
        "queryStringParameters": {"parameter1": "value1,value2", "parameter2": "value"},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "authentication": {
                "clientCert": {
                    "clientCertPem": "CERT_CONTENT",
                    "subjectDN": "www.example.com",
                    "issuerDN": "Example issuer",
                    "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                    "validity": {
                        "notBefore": "May 28 12:30:02 2019 GMT",
                        "notAfter": "Aug  5 09:36:04 2021 GMT",
                    },
                }
            },
            "authorizer": {
                "jwt": {
                    "claims": {"claim1": "value1", "claim2": "value2"},
                    "scopes": ["scope1", "scope2"],
                }
            },
            "domainName": "id.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "id",
            "http": {
                "method": "POST",
                "path": "/my/path",
                "protocol": "HTTP/1.1",
                "sourceIp": "IP",
                "userAgent": "agent",
            },
            "requestId": "id",
            "routeKey": "$default",
            "stage": "$default",
            "time": "12/Mar/2020:19:03:58 +0000",
            "timeEpoch": 1583348638390,
        },
        "body": "Hello from Lambda",
        "pathParameters": {"parameter1": "value1"},
        "isBase64Encoded": False,
        "stageVariables": {"stageVariable1": "value1", "stageVariable2": "value2"},
    }
    example_context = {}
    handler = HTTPGateway(
        example_event, example_context, {"api_gateway_base_path": "/"}
    )

    assert type(handler.body) is bytes
    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": example_event,
        "client": ("IP", 0),
        "headers": [
            [b"header1", b"value1"],
            [b"header2", b"value1,value2"],
            [b"cookie", b"cookie1; cookie2"],
        ],
        "http_version": "1.1",
        "method": "POST",
        "path": "/my/path",
        "query_string": b"parameter1=value1&parameter1=value2&parameter2=value",
        "raw_path": None,
        "root_path": "",
        "scheme": "https",
        "server": ("mangum", 80),
        "type": "http",
    }


@pytest.mark.parametrize(
    "method,path,query_parameters,req_body,body_base64_encoded,query_string,scope_body",
    [
        ("GET", "/my/test/path", None, None, False, b"", None),
        ("GET", "", {"name": "me"}, None, False, b"name=me", None),
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
def test_aws_http_gateway_scope_real_v1(
    method,
    path,
    query_parameters,
    req_body,
    body_base64_encoded,
    query_string,
    scope_body,
) -> None:
    event = get_mock_aws_http_gateway_event_v1(
        method, path, query_parameters, req_body, body_base64_encoded
    )
    example_context = {}
    handler = HTTPGateway(event, example_context, {"api_gateway_base_path": "/"})

    scope_path = path
    if scope_path == "":
        scope_path = "/"

    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": event,
        "client": ("192.168.100.1", 0),
        "headers": [
            [b"accept-encoding", b"gzip, deflate"],
            [b"x-forwarded-port", b"443"],
            [b"x-forwarded-proto", b"https"],
            [b"host", b"test.execute-api.us-west-2.amazonaws.com"],
        ],
        "http_version": "1.1",
        "method": method,
        "path": scope_path,
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
    "method,path,query_parameters,req_body,body_base64_encoded,query_string,scope_body",
    [
        ("GET", "/my/test/path", None, None, False, b"", None),
        ("GET", "", {"name": "me"}, None, False, b"name=me", None),
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
def test_aws_http_gateway_scope_real_v2(
    method,
    path,
    query_parameters,
    req_body,
    body_base64_encoded,
    query_string,
    scope_body,
) -> None:
    event = get_mock_aws_http_gateway_event_v2(
        method, path, query_parameters, req_body, body_base64_encoded
    )
    example_context = {}
    handler = HTTPGateway(event, example_context, {"api_gateway_base_path": "/"})

    scope_path = path
    if scope_path == "":
        scope_path = "/"

    assert handler.scope == {
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "aws.context": {},
        "aws.event": event,
        "client": ("192.168.100.1", 0),
        "headers": [
            [b"accept-encoding", b"gzip,deflate"],
            [b"x-forwarded-port", b"443"],
            [b"x-forwarded-proto", b"https"],
            [b"host", b"test.execute-api.us-west-2.amazonaws.com"],
            [b"cookie", b"cookie1; cookie2"],
        ],
        "http_version": "1.1",
        "method": method,
        "path": scope_path,
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
        (
            "GET",
            b"application/json",
            b'{"hello": "world", "foo": true}',
            '{"hello": "world", "foo": true}',
            False,
        ),
        ("GET", None, b"Hello world", "SGVsbG8gd29ybGQ=", True),
        (
            "GET",
            None,
            b'{"hello": "world", "foo": true}',
            "eyJoZWxsbyI6ICJ3b3JsZCIsICJmb28iOiB0cnVlfQ==",
            True,
        ),
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
def test_aws_http_gateway_response_v1(
    method, content_type, raw_res_body, res_body, res_base64_encoded
):
    """
    Test response types make sense. v1 does less magic than v2.
    """

    async def app(scope, receive, send):
        headers = []
        if content_type is not None:
            headers.append([b"content-type", content_type])

        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": headers,
            }
        )
        await send({"type": "http.response.body", "body": raw_res_body})

    event = get_mock_aws_http_gateway_event_v1(method, "/test", {}, None, False)

    handler = Mangum(app, lifespan="off")

    response = handler(event, {})

    res_headers = {}
    if content_type is not None:
        res_headers = {"content-type": content_type.decode()}

    assert response == {
        "statusCode": 200,
        "isBase64Encoded": res_base64_encoded,
        "headers": res_headers,
        "multiValueHeaders": {},
        "body": res_body,
    }


@pytest.mark.parametrize(
    "method,content_type,raw_res_body,res_body,res_base64_encoded",
    [
        ("GET", b"text/plain; charset=utf-8", b"Hello world", "Hello world", False),
        (
            "GET",
            b"application/json",
            b'{"hello": "world", "foo": true}',
            '{"hello": "world", "foo": true}',
            False,
        ),
        ("GET", None, b"Hello world", "Hello world", False),
        (
            "GET",
            None,
            b'{"hello": "world", "foo": true}',
            '{"hello": "world", "foo": true}',
            False,
        ),
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
def test_aws_http_gateway_response_v2(
    method, content_type, raw_res_body, res_body, res_base64_encoded
):
    async def app(scope, receive, send):
        headers = []
        if content_type is not None:
            headers.append([b"content-type", content_type])

        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": headers,
            }
        )
        await send({"type": "http.response.body", "body": raw_res_body})

    event = get_mock_aws_http_gateway_event_v2(method, "/test", {}, None, False)

    handler = Mangum(app, lifespan="off")

    response = handler(event, {})

    if content_type is None:
        content_type = b"application/json"
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": res_base64_encoded,
        "headers": {"content-type": content_type.decode()},
        "body": res_body,
    }


def test_aws_http_gateway_response_v1_extra_mime_types():
    content_type = b"application/x-yaml"
    utf_res_body = "name: 'John Doe'"
    raw_res_body = utf_res_body.encode()
    b64_res_body = "bmFtZTogJ0pvaG4gRG9lJw=="

    async def app(scope, receive, send):
        headers = []
        if content_type is not None:
            headers.append([b"content-type", content_type])

        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": headers,
            }
        )
        await send({"type": "http.response.body", "body": raw_res_body})

    event = get_mock_aws_http_gateway_event_v1("POST", "/test", {}, None, False)

    # Test default behavior
    handler = Mangum(app, lifespan="off")
    response = handler(event, {})
    assert content_type.decode() not in handler.config["text_mime_types"]
    assert response == {
        "statusCode": 200,
        "isBase64Encoded": True,
        "headers": {"content-type": content_type.decode()},
        "multiValueHeaders": {},
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
        "multiValueHeaders": {},
        "body": utf_res_body,
    }


def test_aws_http_gateway_response_v2_extra_mime_types():
    content_type = b"application/x-yaml"
    utf_res_body = "name: 'John Doe'"
    raw_res_body = utf_res_body.encode()
    b64_res_body = "bmFtZTogJ0pvaG4gRG9lJw=="

    async def app(scope, receive, send):
        headers = []
        if content_type is not None:
            headers.append([b"content-type", content_type])

        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": headers,
            }
        )
        await send({"type": "http.response.body", "body": raw_res_body})

    event = get_mock_aws_http_gateway_event_v2("POST", "/test", {}, None, False)

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
