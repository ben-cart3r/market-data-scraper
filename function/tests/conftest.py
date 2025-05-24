import datetime
import os
from dataclasses import dataclass
from unittest.mock import MagicMock

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="session", autouse=True)
def lambda_environment():
    os.environ["TABLE_NAME"] = "market-data"


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@pytest.fixture
def setup_table(aws_credentials):
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        table = dynamodb.create_table(
            TableName="market-data",
            KeySchema=[
                {"AttributeName": "ticker", "KeyType": "HASH"},
                {"AttributeName": "date", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "ticker", "AttributeType": "S"},
                {"AttributeName": "date", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield table


@pytest.fixture
def invalid_event():
    return {
        "version": "0",
        "id": "abc-123",
        "detail-type": "InsertStockPrice",
        "source": "test.eventbridge",
        "account": "123456789012",
        "time": "2025-05-23T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {},
    }


@pytest.fixture
def valid_event():
    return {
        "version": "0",
        "id": "abc-123",
        "detail-type": "InsertStockPrice",
        "source": "test.eventbridge",
        "account": "123456789012",
        "time": "2025-05-23T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {"ticker": "GME", "period": "1d"},
    }


@pytest.fixture
def valid_backfill_event():
    return {
        "version": "0",
        "id": "abc-123",
        "detail-type": "InsertStockPrice",
        "source": "test.eventbridge",
        "account": "123456789012",
        "time": "2025-05-23T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {"ticker": "GME", "period": "2d"},
    }


# Freeze time to 2023-08-01 00:00
@pytest.fixture
def freeze_time(monkeypatch):
    now = datetime.datetime(2023, 8, 1, 0, 0, 0)
    dt_mock = MagicMock(wraps=datetime.datetime)
    dt_mock.now.return_value = now
    monkeypatch.setattr(datetime, "datetime", dt_mock)
