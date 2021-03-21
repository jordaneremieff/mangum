from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Union, TYPE_CHECKING

from .types import ScopeDict

if TYPE_CHECKING:  # pragma: no cover
    from awslambdaric.lambda_context import LambdaContext


@dataclass
class Scope:
    """
    A holder for an ASGI scope

    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """

    method: str
    headers: List[List[bytes]]
    path: str
    scheme: str
    query_string: bytes
    server: Tuple[str, int]
    client: Tuple[str, int]

    # Invocation event
    trigger_event: Dict[str, Any]
    trigger_context: Union["LambdaContext", Dict[str, Any]]
    event_type: str

    type: str = "http"
    http_version: str = "1.1"
    raw_path: Optional[str] = None
    root_path: str = ""
    asgi: Dict[str, str] = field(default_factory=lambda: {"version": "3.0"})

    def as_dict(self) -> ScopeDict:
        return {
            "type": self.type,
            "http_version": self.http_version,
            "method": self.method,
            "headers": self.headers,
            "path": self.path,
            "raw_path": self.raw_path,
            "root_path": self.root_path,
            "scheme": self.scheme,
            "query_string": self.query_string,
            "server": self.server,
            "client": self.client,
            "asgi": self.asgi,
            # Meta data to pass along to the application in case they need it
            "aws.event": self.trigger_event,
            "aws.context": self.trigger_context,
            "aws.eventType": self.event_type,
        }
