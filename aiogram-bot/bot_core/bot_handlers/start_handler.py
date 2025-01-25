from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from .main_menu_handler.main_menu_handler import main_menu
from ..bot_db.db_handlers import check_user, create_user
from ..create_bot import bot, bot_log
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

async def start_handler(message_or_callback: [types.Message or types.CallbackQuery], state: FSMContext,db: AsyncSession) -> None:
    bot_log.warning('START HANDLER!')
    if isinstance(message_or_callback, types.Message):
        message: types.Message = message_or_callback

        telegram_id = message.from_user.id
        username= message.from_user.username
        assert isinstance(username,str),f'username is not str {username}'
        hello_text = "Проверяю пользователя"
        message_answer = await message.answer(hello_text)
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

        elif is_user:
            bot_log.info(f"User branch {is_user}")
            hello_text = f"{username}\n"
            hello_text += BOT_REPLIES.get('hello_new_user_text','error').get('kaz')
            hello_text += '\n\n'
            hello_text += BOT_REPLIES.get('hello_new_user_text','error').get('rus')
            keyboard = command_menu_kb()
            await message_answer.edit_text(hello_text, reply_markup=keyboard)
        else:
            bot_log.info(f"Create new user branch {is_user}")
            new_user = await create_user(telegram_id, username, db)
            hello_text = f"{username}\n"
            hello_text += BOT_REPLIES.get('hello_new_user_text', 'error').get('kaz')
            hello_text += '\n\n'
            hello_text += BOT_REPLIES.get('hello_new_user_text', 'error').get('rus')
            keyboard = command_menu_kb()
            await message_answer.edit_text(hello_text, reply_markup=keyboard)

router.callback_query.register(start_handler, F.data == Calls.START_MENU)
router.message.register(start_handler, Command("start"))
