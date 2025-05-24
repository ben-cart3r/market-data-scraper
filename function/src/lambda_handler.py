import datetime
import os
from decimal import Decimal
from typing import Any, Dict

import boto3
import yfinance as yf
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import envelopes, event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel

logger = Logger()


class ScrapeMarketDataEvent(BaseModel):
    ticker: str
    period: str


def insert_stock_price(table, ticker: str, date: str, close_price: float):
    item = {
        "ticker": ticker,
        "date": date,
        "closePrice": Decimal(str(close_price)),
        "insertedAt": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    try:
        table.put_item(Item=item)
        logger.info(f"Inserted {ticker} @ {date}: {close_price}")
    except Exception as e:
        logger.error(f"Error inserting {ticker} @ {date}:", e)


@event_parser(model=ScrapeMarketDataEvent, envelope=envelopes.EventBridgeEnvelope)
@logger.inject_lambda_context(log_event=True)
def handle_event(event: ScrapeMarketDataEvent, context: LambdaContext) -> Dict[Any, Any]:
    logger.info(event)

    table_name = os.getenv("TABLE_NAME")
    dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
    table = dynamodb.Table(table_name)

    ticker = yf.Ticker(event.ticker)
    data = ticker.history(period=event.period)
    dict = data.to_dict("index")

    for key in dict.keys():
        insert_stock_price(table, event.ticker, key.date().isoformat(), dict[key]["Close"])

    return {"statusCode": 200, "body": f"Inserted {event.ticker} data"}
