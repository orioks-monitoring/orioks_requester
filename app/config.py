import os
from pathlib import Path

import aiohttp
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

SERVICE_NAME = os.getenv("SERVICE_NAME", "checking")
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs" / SERVICE_NAME

RABBIT_MQ_URL = os.getenv("RABBIT_MQ_URL", "amqp://guest:guest@localhost/")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

REQUESTS_TIMEOUT = aiohttp.ClientTimeout(total=30)
ORIOKS_REQUESTS_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "User-Agent": "orioks_monitoring/2.0 (Linux; aiohttp)",
}

ORIOKS_PAGE_URLS = {
    "login": "https://orioks.miet.ru/user/login",
    "masks": {
        "news": "https://orioks.miet.ru/main/view-news?id={id}",
        "homeworks": "https://orioks.miet.ru/student/homework/view?id_thread={id}",
        "requests": {
            "questionnaire": "https://orioks.miet.ru/request/questionnaire/view?id_thread={id}",  # not sure
            "doc": "https://orioks.miet.ru/request/doc/view?id_thread={id}",  # not sure
            "reference": "https://orioks.miet.ru/request/reference/view?id_thread={id}",
        },
    },
    "notify": {
        "marks": "https://orioks.miet.ru/student/student",
        "news": "https://orioks.miet.ru",
        "homeworks": "https://orioks.miet.ru/student/homework/list",
        "requests": {
            "questionnaire": "https://orioks.miet.ru/request/questionnaire/list?AnketaTreadForm[status]=1,2,4,6,3,5,7&AnketaTreadForm[accept]=-1",
            "doc": "https://orioks.miet.ru/request/doc/list?DocThreadForm[status]=1,2,4,6,3,5,7&DocThreadForm[type]=0",
            "reference": "https://orioks.miet.ru/request/reference/list?ReferenceThreadForm[status]=1,2,4,6,3,5,7",
        },
    },
}

FERNET_KEY_FOR_COOKIES = bytes(
    os.getenv("FERNET_KEY_FOR_COOKIES", "my32lengthsupersecretnooneknows1"), "utf-8"
)
FERNET_CIPHER_SUITE = Fernet(FERNET_KEY_FOR_COOKIES)

ORIOKS_REQUESTER_SECONDS_BETWEEN_REQUESTS = float(
    os.getenv("ORIOKS_REQUESTER_SECONDS_BETWEEN_REQUESTS", 1.5)
)
