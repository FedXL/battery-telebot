from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot_core.bot_db.db_handlers import save_profile_data_collected
from bot_core.bot_handlers.profile_handler.profile_handler import profile_menu
from bot_core.utils.callback_actions import Calls

router = Router()

async def change_language_handler(callback: types.CallbackQuery, state: FSMContext, db:AsyncSession) -> None:
    """Обработчик смены языка в профиле"""
    state_dict = await state.get_data()

    language = state_dict.get('language')
    state_dict['language'] = 'rus' if language == 'kaz' else 'kaz'
    state_dict['collected_data'] = {}
    await save_profile_data_collected(state_data=state_dict, telegram_id=callback.from_user.id, db=db)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Назад", callback_data=Calls.GO_TO_PROFILE))
    builder.adjust(1)
    keyboard = builder.as_markup()
    await callback.message.answer('Язык изменен', reply_markup=keyboard)
    await callback.message.delete()

router.callback_query.register(change_language_handler, F.data.in_([Calls.CHANGE_LANGUAGE_RUS,Calls.CHANGE_LANGUAGE_KAZ]), StateFilter(None))