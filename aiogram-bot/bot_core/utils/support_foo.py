import asyncio
from typing import Tuple

from aiogram import Bot

from bot_core.create_bot import bot


async def kill_messages(message_or_callback,killing_list) -> None:
    """ в основном нужна что бы очищать с листа лишние сообщения,
     что хранятся в state_data killing list"""

    if killing_list:
        for message_id in killing_list:
            try:
                await bot.delete_message(chat_id=message_or_callback.from_user.id, message_id=message_id)
            except:
                print("message not found")

async def delete_message_later(telebot: Bot, chat_id: int, message_id: int, delay: int = 3):
    """Удаляет сообщение через указанную задержку."""
    await asyncio.sleep(delay)
    try:
        await telebot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Ошибка удаления сообщения: {e}")




