from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot_core.bot_db.db_handlers import check_user
from bot_core.utils.callback_actions import Calls

router = Router()

# async def battery_catch_handler(callback: types.CallbackQuery, state: FSMContext, db:AsyncSession) -> None:
#     state_dict = await state.get_data()
#     seller_or_client = state_dict['client_or_seller']
#     language = state_dict['language']
#     builder = InlineKeyboardBuilder()
#     builder2 = ReplyKeyboardBuilder()
#     builder.add(types.InlineKeyboardButton(text="Назад", callback_data=Calls.MAIN_MENU,request_location=True))
#     builder.adjust(1)
#     keyboard = builder.as_markup()
#     await callback.message.edit_text("Пожалуйста, поделитесь своей геолокацией:", reply_markup=keyboard)

async def catch_location(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession) -> None:
    """Обработчик регистрации аккумулятора с текстовой клавиатурой"""
    available, state_dict = await check_user(callback.from_user.id, db=db)

    if not available:
        await callback.answer("Вы не зарегистрированы в системе что вообще то странно сильно")
        return
    if not state_dict:
        await callback.answer("Ваш профиль не найден что опять странно")
        return
    profile_completeness = state_dict['profile_completeness']
    if not profile_completeness:
        await callback.answer("Для этого действия необходимо заполнить профиль")

    builder = ReplyKeyboardBuilder()
    builder.button(text="Не буду делиться")
    builder.button(text="Поделитесь местом где вы купили аккумулятор", request_location=True)
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)

    await callback.message.answer(
        "Пожалуйста, выберите действие или поделитесь своей геолокацией:",
        reply_markup=keyboard
    )
    await state.set_data(state_dict)

async def location_catch_and_ask_about_number(message: types.Message, state: FSMContext) -> None:
    """Обработчик получения геолокации"""
    state_dict = await state.get_data()

    if message.location:
        await message.answer("Спасибо за геолокацию!", reply_markup=ReplyKeyboardRemove())
        state_dict['location'] = {'latitude': message.location.latitude, 'longitude': message.location.longitude}
    else:
        await message.answer("Вы не поделились геолокацией", reply_markup=ReplyKeyboardRemove())
    await message.answer('Теперь введите номер аккумулятора')







router.callback_query.register(catch_location, F.data==Calls.REGISTRATION_BATTERY, StateFilter(None))
router.message.register(location_catch_and_ask_about_number, F.location, StateFilter(None))
router.message.register(location_catch_and_ask_about_number, F.text, StateFilter(None))
