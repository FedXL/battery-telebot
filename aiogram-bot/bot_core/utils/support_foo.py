import asyncio
from typing import Tuple

from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot_core.create_bot import bot
from bot_core.utils.callback_actions import Calls
from bot_core.utils.download_replies import BOT_REPLIES


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




def comeback_to_main_menu_kb(language)->types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['comeback'][language], callback_data=Calls.MAIN_MENU))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard

def back_to_main_menu_kb(language:str)->types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=BOT_REPLIES['to_main_menu_from_battery'][language])
    keyboard_my = builder.as_markup(resize_keyboard=True)
    return keyboard_my
