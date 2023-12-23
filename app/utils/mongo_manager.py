from http.cookies import SimpleCookie

from app.config import FERNET_CIPHER_SUITE
from app.utils.MongoHelper import MongoContextManager


async def _get_user_orioks_cookies_from_telegram_id(
    user_telegram_id: int,
) -> SimpleCookie:
    """
    Get user orioks cookies from mongo database. Then decrypt it
    and return as SimpleCookie object.

    :param user_telegram_id: telegram id of user
    :raises FileNotFoundError: if cookies of user with telegram id not found in database
    :return: SimpleCookie object with user orioks cookies
    """
    async with MongoContextManager(
        database="users_data", collection="cookies"
    ) as mongo:
        cookies = await mongo.find_one({"user_telegram_id": user_telegram_id})
        if cookies is None:
            raise FileNotFoundError(
                f'Cookies of user with telegram id {user_telegram_id} not found in database'
            )

    dict_of_cookies = {}
    for key, value in cookies["cookies"].items():
        dict_of_cookies[key] = FERNET_CIPHER_SUITE.decrypt(
            value.encode("utf-8")
        ).decode("utf-8")

    return SimpleCookie(dict_of_cookies)


class UserCookiesHelper:
    """
    Context manager for working with user cookies in mongo database.

    Usage:
    async with UserCookiesHelper(user_telegram_id=1234567890) as cookies:
        async with ClientSession(cookies=cookies) as session:
            async with session.get("https://orioks.miet.ru/") as response:
                print(await response.text())

    """

    def __init__(self, user_telegram_id: int) -> None:
        self.user_telegram_id = user_telegram_id

    async def __aenter__(self) -> SimpleCookie:
        """
        Get user orioks cookies from mongo database. Then decrypt it
        and return as SimpleCookie object.

        :raises FileNotFoundError: if cookies of user with telegram id not found in database
        :return: SimpleCookie object with user orioks cookies
        """
        return await _get_user_orioks_cookies_from_telegram_id(
            user_telegram_id=self.user_telegram_id
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Do nothing.
        """
        pass
