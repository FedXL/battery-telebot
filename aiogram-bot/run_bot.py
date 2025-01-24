import asyncio
import logging

from bot_core.start_bot import main_aiogram_bot
from bot_core.utils.download_replies import load_replies

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
     asyncio.run(main_aiogram_bot())
