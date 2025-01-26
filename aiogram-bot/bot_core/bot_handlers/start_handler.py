from typing import Union

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from .main_menu_handler.main_menu_handler import main_menu
from ..bot_db.db_handlers import check_user, create_user
from ..create_bot import bot, bot_log, dp
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


def context_for_profile(client_or_seller:str,username:str,language:str) ->str:
    """собрать приветсвие для людей у которыйх есть профайл"""
    greetings_text = f"👋 {username}"
    if client_or_seller == 'client':
        greetings_text += BOT_REPLIES['greetings_client_text'][language]
    elif client_or_seller == 'seller':
        greetings_text += BOT_REPLIES['greetings_seller_text'][language]
    else:
        raise ValueError("Unknown user type")
    return greetings_text

def context_for_hello(username):
    hello_text = f"{username}\n"
    hello_text += BOT_REPLIES['hello_new_user_text']['kaz']
    hello_text += '\n\n'
    hello_text += BOT_REPLIES['hello_new_user_text']['rus']
    return hello_text


async def start_handler(message_or_callback: Union[types.Message,types.CallbackQuery], state: FSMContext,db: AsyncSession) -> None:
    bot_log.warning('START HANDLER!')
    hello_text = "Проверяю пользователя"
    data_state = await state.get_data()
    await state.clear()
    if data_state:
        await state.update_data(data_state)
    if isinstance(message_or_callback, types.CallbackQuery):

        message = message_or_callback.message
        message_answer = await bot.send_message(chat_id=message.chat.id, text=hello_text)
        await message_or_callback.message.delete()
    else:
        message: types.Message = message_or_callback
        message_answer = await message.answer(hello_text)

    telegram_id = message.from_user.id
    username = message.from_user.username


    is_user, profile_dict = await check_user(db=db, telegram_id=telegram_id)

    if profile_dict and is_user:
        bot_log.info(f"User+profile branch {profile_dict}/{is_user}")
        language = profile_dict['language']
        client_or_seller = profile_dict['client_or_seller']
        profile_text = context_for_profile(client_or_seller=client_or_seller, username=username, language=language)
        storage_dict = await state.get_data()
        storage_dict['language'] = profile_dict['language']
        storage_dict['client_or_seller'] = profile_dict['client_or_seller']
        await state.set_data(storage_dict)
        await main_menu(callback_or_message=message, state=state, db=db)
        return
    elif is_user:
        bot_log.info(f"User branch {is_user}")
    else:
        bot_log.info(f"Create new user branch {is_user}")
        new_user = await create_user(telegram_id, username, db)
    hello_text = context_for_hello(username)
    keyboard = command_menu_kb()
    await message_answer.edit_text(hello_text, reply_markup=keyboard)
    return



router.callback_query.register(start_handler, F.data == Calls.START_MENU)
router.message.register(start_handler, Command("start"))
