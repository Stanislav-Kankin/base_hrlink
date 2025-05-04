import aiohttp
from config import config
from utils.logging import logger


async def get_balance() -> float:
    """
    Получает текущий баланс аккаунта на ProxyAPI.
    Возвращает баланс в виде числа или None в случае ошибки.
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Используем правильный endpoint из документации
            url = "https://api.proxyapi.ru/proxyapi/balance"
            headers = {
                "Authorization": f"Bearer {config.PROXY_API_KEY}",
                "Content-Type": "application/json"
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    balance = data.get("balance")
                    if balance is not None:
                        return float(balance)
                    logger.error("Баланс не найден в ответе")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка при получении баланса: {response.status}, {error_text}"
                    )
                    return None
    except Exception as e:
        logger.error(f"Ошибка при получении баланса: {e}")
        return None
