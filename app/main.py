import asyncio
import logging
from typing import Never, NoReturn

from aio_pika import connect_robust
from aio_pika.patterns import RPC
from prometheus_client import start_http_server

from app.config import ORIOKS_REQUESTER_SECONDS_BETWEEN_REQUESTS, RABBIT_MQ_URL
from app.logging import setup_logging
from app.utils.orioks_http_requester import (
    OrioksHomeworksHTTPRequester,
    OrioksMarksHTTPRequester,
    OrioksNewsHTTPRequester,
    OrioksNewsIDHTTPRequester,
    OrioksRequestsDocHTTPRequester,
    OrioksRequestsQuestionnaireHTTPRequester,
    OrioksRequestsReferenceHTTPRequester,
)
from message_models.models import OrioksRequestMessage

logger = logging.getLogger(__name__)


def assert_never(_: Never) -> NoReturn:
    raise AssertionError("Unhandled type")


async def make_orioks_request(task_info: OrioksRequestMessage) -> str:
    logger.info("Got task for to orioks request with data: %s", task_info)

    event_type_to_requester_mapper = {
        "marks": OrioksMarksHTTPRequester,
        "homeworks": OrioksHomeworksHTTPRequester,
        "requests-questionnaire": OrioksRequestsQuestionnaireHTTPRequester,
        "requests-doc": OrioksRequestsDocHTTPRequester,
        "requests-reference": OrioksRequestsReferenceHTTPRequester,
        "news": OrioksNewsHTTPRequester,
        "news-individual": OrioksNewsIDHTTPRequester(task_info.news_id),
    }
    if requester := event_type_to_requester_mapper.get(task_info.event_type, None):
        result = await requester.send_request(
            user_telegram_id=task_info.user_telegram_id
        )
    else:
        assert_never(task_info.event_type)

    await asyncio.sleep(ORIOKS_REQUESTER_SECONDS_BETWEEN_REQUESTS)

    return result


async def main() -> None:
    setup_logging()

    logger.info("Starting metrics server...")
    start_http_server(port=8880)
    logger.info("Metrics server started.")

    logger.info("Connecting to RabbitMQ at %s", RABBIT_MQ_URL)
    connection = await connect_robust(
        RABBIT_MQ_URL,
        client_properties={"connection_name": "callee"},
    )
    logger.info("Connected to RabbitMQ.")

    channel = await connection.channel()
    rpc = await RPC.create(channel)

    await channel.set_qos(prefetch_count=1)
    await rpc.register("make_orioks_request", make_orioks_request, durable=True)

    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
