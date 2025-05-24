from unittest.mock import MagicMock, patch

import boto3
import pandas as pd
import pytest
from pydantic import ValidationError

from src.lambda_handler import handle_event


def test_error_thrown_for_invalid_event(lambda_context, invalid_event):
    with pytest.raises(ValidationError) as exc_info:
        handle_event(invalid_event, lambda_context)

    assert len(exc_info.value.errors()) == 2
    assert exc_info.value.errors() == [
        {
            "type": "missing",
            "loc": ("ticker",),
            "msg": "Field required",
            "input": {},
            "url": "https://errors.pydantic.dev/2.11/v/missing",
        },
        {
            "type": "missing",
            "loc": ("period",),
            "msg": "Field required",
            "input": {},
            "url": "https://errors.pydantic.dev/2.11/v/missing",
        },
    ]


@patch("yfinance.Ticker")
def test_valid_event_inserts_data_to_dynamodb(
    mock_ticker_class, lambda_context, freeze_time, setup_table, valid_event
):
    # Given some fake market data
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Close": [10.00],
        },
        index=[pd.Timestamp("2023-08-01")],
    )
    mock_ticker_class.return_value = mock_ticker

    # When the lambda is invoked
    result = handle_event(valid_event, lambda_context)

    # Then validate successful response
    assert result["statusCode"] == 200
    assert result["body"] == "Inserted GME data"

    # Then validate data was persisted
    dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
    table = dynamodb.Table("market-data")
    result = table.get_item(Key={"ticker": "GME", "date": "2023-08-01"})
    item = result.get("Item")

    assert item == {
        "ticker": "GME",
        "date": "2023-08-01",
        "closePrice": 10.00,
        "insertedAt": "2023-08-01T00:00:00",
    }


@patch("yfinance.Ticker")
def test_backfill_inserts_multiple_data_items_to_dynamodb(
    mock_ticker_class, lambda_context, freeze_time, setup_table, valid_event
):
    # Given some fake market data
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Close": [10.00, 20.00],
        },
        index=[pd.Timestamp("2023-08-01"), pd.Timestamp("2023-08-02")],
    )
    mock_ticker_class.return_value = mock_ticker

    # When the lambda is invoked
    result = handle_event(valid_event, lambda_context)

    # Then validate successful response
    assert result["statusCode"] == 200
    assert result["body"] == "Inserted GME data"

    # Then validate data was persisted
    dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
    table = dynamodb.Table("market-data")
    result = table.get_item(Key={"ticker": "GME", "date": "2023-08-01"})
    item = result.get("Item")

    assert item == {
        "ticker": "GME",
        "date": "2023-08-01",
        "closePrice": 10.00,
        "insertedAt": "2023-08-01T00:00:00",
    }

    result = table.get_item(Key={"ticker": "GME", "date": "2023-08-02"})
    item = result.get("Item")

    assert item == {
        "ticker": "GME",
        "date": "2023-08-02",
        "closePrice": 20.00,
        "insertedAt": "2023-08-01T00:00:00",
    }
