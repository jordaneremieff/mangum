import typing
import os
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

from mangum.backends.base import WebSocketBackend
from mangum.exceptions import WebSocketError


@dataclass
class DynamoDBBackend(WebSocketBackend):

    table_name: str
    region_name: typing.Optional[str] = None
    endpoint_url: typing.Optional[str] = None

    def __post_init__(self) -> None:
        region_name = self.region_name or os.environ["AWS_REGION"]
        try:
            dynamodb_resource = boto3.resource(
                "dynamodb", region_name=region_name, endpoint_url=self.endpoint_url
            )
            dynamodb_resource.meta.client.describe_table(TableName=self.table_name)
        except ClientError as exc:
            raise WebSocketError(exc)

        self.table = dynamodb_resource.Table(self.table_name)

    def create(self, connection_id: str, initial_scope: str) -> None:
        self.table.put_item(
            Item={"connectionId": connection_id, "initial_scope": initial_scope},
            ConditionExpression=f"attribute_not_exists(connectionId)",
        )

    def fetch(self, connection_id: str) -> str:
        try:
            item = self.table.get_item(Key={"connectionId": connection_id})["Item"]
        except KeyError:
            raise WebSocketError(f"Connection not found: {connection_id}")

        initial_scope = item["initial_scope"]

        return initial_scope

    def delete(self, connection_id: str) -> None:
        self.table.delete_item(Key={"connectionId": connection_id})
