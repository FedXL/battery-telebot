from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .main_menu_handler.main_menu_handler import main_menu
from ..create_bot import bot
from ..bot_db.alchemy_models import UserTelegram
from ..bot_db.db_engine import telegram_bot_session
from ..utils.callback_actions import Calls
from ..utils.download_replies import BOT_REPLIES

router = Router()

def command_menu_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Продолжить",
                                           callback_data=Calls.ASK_ABOUT_LANGUAGE))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard

async def kill_state(message_or_callback, state: FSMContext) -> None:
    """ в основном нужна что бы очищать с листа лишние сообщения,
     что хранятся в state_data killing list"""
    state_dict = await state.get_data()
    killing_list = state_dict.get("killing_list", [])
    if killing_list:
        for message_id in killing_list:
            try:
                await bot.delete_message(chat_id=message_or_callback.from_user.id, message_id=message_id)
            except:
                print("message not found")
    await state.clear()

@router.message(Command("state"))
async def state(message: types.Message, state: FSMContext) -> None:
    state_name = await state.get_state()
    if state_name is None:
        state_name = "No state is set."
    await message.answer(state_name)

async def start_handler(message_or_callback: [types.Message or types.CallbackQuery], state: FSMContext,db: AsyncSession) -> None:

    if isinstance(message_or_callback, types.Message):
        telegram_id = message_or_callback.from_user.id
        username= message_or_callback.from_user.username
        hello_text = "Проверяю пользователя"
        result = await message_or_callback.answer(hello_text)

        async with db as session:
            existing_user = await session.execute(
                select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id)
            )
            existing_user = existing_user.scalar_one_or_none()
            if existing_user:
                hello_text = f"Привет, я тебя уже знаю!{existing_user.username}"
                existing_user.username = username
                existing_user.updated_at = datetime.utcnow()

                await result.edit_text(hello_text)
                new_callback = CallbackQuery(
                    id=message_or_callback.id,
                    from_user=message_or_callback.from_user,
                    message=result,
                    data=Calls.MAIN_MENU,
                    chat_instance=message_or_callback.chat_instance
                )
                await main_menu(new_callback, state, db)
            else:
                hello_text = BOT_REPLIES.get('hello_new_user_text','error').get('kaz')
                hello_text += '\n\n'
                hello_text += BOT_REPLIES.get('hello_new_user_text','error').get('rus')
                new_user = UserTelegram(
                        telegram_id=telegram_id,
                        username=username,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                        )
                session.add(new_user)
                keyboard = command_menu_kb()
                await session.commit()
                await result.edit_text(hello_text, reply_markup=keyboard)



router.callback_query.register(start_handler, F.data == Calls.START_MENU)
router.message.register(start_handler, Command("start"))
