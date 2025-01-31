from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import add_message
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, SpecialStates
from bot_core.utils.support_foo import back_to_main_menu_kb, delete_message_later


router = Router()


async def catch_message_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик получения сообщения"""
    state_dict = await state.get_data()
    bot_log.info(f'CATCH MESSAGE HANDLER {state_dict}')
    message_killer = state_dict.get('kill_message',None)
    if not message_killer:
        state_dict['kill_message'] = []
    await callback.answer('Ok')
    mes=await callback.message.edit_text('Для отправки сообщения теперь просто введите текст')
    state_dict['kill_message'].append(mes.message_id)
    await state.set_state(SpecialStates.messanger)
    await state.set_data(state_dict)

async def catch_messages_handler(message: types.Message, state: FSMContext, db:AsyncSession) -> None:
    """Обработчик получения сообщения"""
    state_dict = await state.get_data()

    bot_log.info(f'CATCH MESSAGE HANDLER {state_dict}')
    language = state_dict.get('language','rus')
    result = await add_message(db=db, message=message.text, telegram_id=message.from_user.id)
    if result:
        result=await message.answer('🔸Ваше сообщение получено🔸', reply_markup=back_to_main_menu_kb(language))
        await delete_message_later(telebot=result.bot, chat_id=result.chat.id, message_id=result.message_id,
                                   delay=10)
    else:
        mes = await message.answer('❌Произошла ошибка❌',reply_markup=back_to_main_menu_kb(language))
        state_dict['kill_message'].append(mes.message_id)
    await state.set_data(state_dict)


router.callback_query.register(catch_message_handler, F.data == Calls.CATCH_MESSAGE, StateFilter(SpecialStates.messages_of))
router.message.register(catch_messages_handler, StateFilter(SpecialStates.messanger))
