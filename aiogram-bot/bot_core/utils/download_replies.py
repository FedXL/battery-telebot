import logging
import sys
from sqlalchemy import select
from bot_core.bot_db.alchemy_models import OnlyRelies
from bot_core.bot_db.db_engine import telegram_bot_session

BOT_REPLIES = {}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)



async def load_replies():
    global BOT_REPLIES
    """Загрузить реплики из базы данных."""
    try:
        async with telegram_bot_session() as session:
            logging.info("Загрузка реплик из базы данных...")
            result = await session.execute(select(OnlyRelies))
            rows = result.scalars().all()
            BOT_REPLIES = {row.name: {'kaz': row.kaz, 'rus': row.rus} for row in rows}
            logging.info("Реплики загружены успешно")
            logging.info(f"Реплики: {BOT_REPLIES}")
            return True
    except Exception as e:
        logging.error(f"Ошибка при загрузке реплик: {e}")
        return False


