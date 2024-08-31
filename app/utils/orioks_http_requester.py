import logging
import time
from abc import ABC, abstractmethod
from typing import final

from aiohttp import ClientSession
from prometheus_client import Histogram

from app.config import ORIOKS_PAGE_URLS, ORIOKS_REQUESTS_HEADERS, REQUESTS_TIMEOUT
from app.utils.mongo_manager import UserCookiesHelper

REQUEST_TIME = Histogram(
    "orioks_request_processing_seconds",
    "Время выполнения send_request",
    ["url", "user_telegram_id", "status_code"],
)


class OrioksHTTPRequester(ABC):
    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @classmethod
    @final
    async def send_request(cls, user_telegram_id: int) -> str:
        start = time.monotonic()
        status_code = "exception"
        try:
            async with UserCookiesHelper(user_telegram_id=user_telegram_id) as cookies:
                async with ClientSession(
                    cookies=cookies,
                    timeout=REQUESTS_TIMEOUT,
                    headers=ORIOKS_REQUESTS_HEADERS,
                ) as session:
                    async with session.get(cls.url) as response:
                        logging.info(f"{response.status} {response.url}")
                        status_code = response.status
                        if response.status != 200:
                            raise Exception(
                                f"Got status code {response.status} from orioks"
                            )
                        raw_html = await response.text()
                    return raw_html
        finally:
            REQUEST_TIME.labels(
                url=cls.url,
                user_telegram_id=str(user_telegram_id),
                status_code=str(status_code),
            ).observe(time.monotonic() - start)


class OrioksMarksHTTPRequester(OrioksHTTPRequester):
    url = ORIOKS_PAGE_URLS["notify"]["marks"]


class OrioksHomeworksHTTPRequester(OrioksHTTPRequester):
    url = ORIOKS_PAGE_URLS["notify"]["homeworks"]


class OrioksRequestsQuestionnaireHTTPRequester(OrioksHTTPRequester):
    url = ORIOKS_PAGE_URLS["notify"]["requests"]["questionnaire"]


class OrioksRequestsDocHTTPRequester(OrioksHTTPRequester):
    url = ORIOKS_PAGE_URLS["notify"]["requests"]["doc"]


class OrioksRequestsReferenceHTTPRequester(OrioksHTTPRequester):
    url = ORIOKS_PAGE_URLS["notify"]["requests"]["reference"]


class OrioksNewsHTTPRequester(OrioksHTTPRequester):
    url = ORIOKS_PAGE_URLS["notify"]["news"]


class OrioksNewsIDHTTPRequester(OrioksHTTPRequester):
    url = ORIOKS_PAGE_URLS["masks"]["news"]

    def __init__(self, news_id: int):
        self.__class__.url = ORIOKS_PAGE_URLS["masks"]["news"].format(id=news_id)
