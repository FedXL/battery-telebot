import logging
import sys
from sqlalchemy import select
from bot_core.bot_db.alchemy_models import OnlyRelies
from bot_core.bot_db.db_engine import telegram_bot_session

BOT_REPLIES = {}




async def load_replies():
    global BOT_REPLIES
    """Загрузить реплики из базы данных."""
    try:
        async with telegram_bot_session() as session:
            result = await session.execute(select(OnlyRelies))
            rows = result.scalars().all()
            BOT_REPLIES = {row.name: {'kaz': row.kaz, 'rus': row.rus} for row in rows}
            return True
    except Exception as e:
        logging.error(f"Реплики не были загружены проверь соединение: {e}")
        return False


