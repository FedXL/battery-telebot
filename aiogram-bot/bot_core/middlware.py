from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_engine import get_db


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        data['db'] = await get_db().__anext__()
        try:
            return await handler(event, data)
        finally:
            db: AsyncSession = data.get('db')
            if db:
                await db.close()