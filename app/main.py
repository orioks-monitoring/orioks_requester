import asyncio
import logging
from typing import NoReturn, Never

from aio_pika import connect_robust
from aio_pika.patterns import RPC

from app.config import RABBIT_MQ_URL
from app.utils.orioks_http_requester import (
    OrioksMarksHTTPRequester,
    OrioksHomeworksHTTPRequester,
    OrioksRequestsQuestionnaireHTTPRequester,
    OrioksRequestsDocHTTPRequester,
    OrioksRequestsReferenceHTTPRequester,
    OrioksNewsHTTPRequester,
    OrioksNewsIDHTTPRequester,
)
from message_models.models import OrioksRequestMessage

logger = logging.getLogger(__name__)


def assert_never(_: Never) -> NoReturn:
    raise AssertionError("Unhandled type")


async def make_orioks_request(task_info: OrioksRequestMessage) -> str:
    logger.info("Got task for to orioks request with data: %s", task_info)
    await asyncio.sleep(0.5)

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

    return result


async def main() -> None:
    connection = await connect_robust(
        RABBIT_MQ_URL,
        client_properties={"connection_name": "callee"},
    )

    # Creating channel
    channel = await connection.channel()

    # Specify the queue name explicitly
    rpc = await RPC.create(channel)

    await channel.set_qos(prefetch_count=1)

    # Register multiple functions
    await rpc.register("make_orioks_request", make_orioks_request, durable=True)

    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
