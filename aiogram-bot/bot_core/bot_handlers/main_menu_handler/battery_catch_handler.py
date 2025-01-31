import asyncio
import random
from aiogram import types, Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import check_user, add_invalid_try, add_valid_battery
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, SpecialStates, CatchBattery
from bot_core.utils.check_battery import valid_battery_code
from bot_core.utils.download_replies import BOT_REPLIES
from bot_core.utils.support_foo import delete_message_later

router = Router()

def comeback_to_main_menu_kb(language)->types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['comeback'][language], callback_data=Calls.MAIN_MENU))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard


async def start_battery_register_way(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession) -> None:
    """Обработчик регистрации аккумулятора с текстовой клавиатурой"""
    available, state_dict = await check_user(callback.from_user.id, db=db)
    state_dict['kill_message'] = []
    if not available:
        await callback.answer("Вы не зарегистрированы в системе что вообще то странно сильно")
        return
    if not state_dict:
        await callback.answer("Ваш профиль не найден что опять странно")
        return

    profile_completeness = state_dict['profile_completeness']
    if not profile_completeness:
        await callback.answer("❌")
        result = await callback.message.answer("Для этого действия необходимо заполнить профиль")
        asyncio.create_task(delete_message_later(callback.bot, result.chat.id, result.message_id))
        return
    if state_dict['client_or_seller'] == 'seller':
        await callback.answer("❌")
        return

    await callback.answer('ok')
    language = state_dict['language']
    builder = ReplyKeyboardBuilder()
    builder.button(text=BOT_REPLIES['no_location_button'][language])
    builder.button(text=BOT_REPLIES['plz_location_button'][language], request_location=True)
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback.message.delete()
    result=await callback.message.answer(
        text = BOT_REPLIES['plz_location_text'][language],
        reply_markup=keyboard)
    state_dict['kill_message'].append(result.message_id)
    await state.set_data(state_dict)
    await state.set_state(CatchBattery.catch_location)


async def location_catch_and_ask_about_number(message: types.Message, state: FSMContext) -> None:
    """1) Получить геолокацию
    2) Попросить чек"""

    state_dict = await state.get_data()
    bot_log.info(f"LOCATION CATCH HANDLER: {state_dict}")
    state_dict['kill_message'].append(message.message_id)

    if message.location:
        result = await message.answer("Спасибо за геолокацию!", reply_markup=ReplyKeyboardRemove())
        state_dict['location'] = {'latitude': message.location.latitude, 'longitude': message.location.longitude}
        state_dict['kill_message'].append(result.message_id)
    else:
        bot = message.bot
        result = await message.answer("Вы не поделились геолокацие", reply_markup=ReplyKeyboardRemove())
        state_dict['kill_message'].append(result.message_id)
    builder = ReplyKeyboardBuilder()
    builder.button(text="Нету чека")
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)

    result=await message.answer('Еще поделитесь чеком пожалуйста если есть', reply_markup=keyboard)
    state_dict['kill_message'].append(result.message_id)
    await state.set_state(CatchBattery.catch_image)
    await state.set_data(state_dict)


async def catch_image_and_ask_code(message: types.Message, state: FSMContext) -> None:
    """Обработчик получения изображения"""
    state_dict = await state.get_data()
    bot_log.info(f'CATCH sales receipt HANDLER {state_dict}')
    state_dict['kill_message'].append(message.message_id)
    if message.photo:
        result=await message.answer("Спасибо за фото!", reply_markup=ReplyKeyboardRemove())
        state_dict['photo'] = message.photo[-1].file_id
        state_dict['kill_message'].append(result.message_id)
    else:
        result=await message.answer("Вы не отправили фото", reply_markup=ReplyKeyboardRemove())
        state_dict['kill_message'].append(result.message_id)
    result = await message.answer('Теперь введите номер аккумулятора')
    state_dict['kill_message'].append(result.message_id)
    await state.set_data(state_dict)
    await state.set_state(CatchBattery.catch_battery)



async def catch_battery_number_end(message: types.Message, state: FSMContext,db:AsyncSession) -> None:
    """Обработчик получения номера аккумулятора"""

    state_dict = await state.get_data()
    state_dict['battery_number'] = message.text
    language = state_dict['language']
    await state.set_data(state_dict)

    mes=await message.answer('Спасибо за информацию!')
    state_dict['kill_message'].append(mes.message_id)
    result,comment = valid_battery_code(message.text)
    if result:
        state_dict = {**state_dict, **result}
        code = str(random.randint(100000, 999999))
        state_dict['confirmation_code'] = code
        mes=await message.answer('Аккумулятор валиден')
        state_dict['kill_message'].append(mes.message_id)
        result = await add_valid_battery(db=db, telegram_id=message.from_user.id, data=state_dict)

        if result:
            mes=await message.answer('Аккумулятор успешно зарегистрирован')
            state_dict['kill_message'].append(mes.message_id)
            await message.answer('Код регистрации покупки для продавца:' + str(code), reply_markup=comeback_to_main_menu_kb(state_dict['language']))
        else:
            mes = await message.answer('Ошибка при регистрации аккумулятора', reply_markup=comeback_to_main_menu_kb(state_dict['language']))
            state_dict['kill_message'].append(mes.message_id)
            context = state_dict.get('serial')
            context += 'Скорее всего ввод номера который уже зарегистрирован'
            await add_invalid_try(db=db, telegram_id=message.from_user.id, battery_number=context)
        await state.set_state(SpecialStates.messages_of)
    else:
        builder = ReplyKeyboardBuilder()
        builder.button(text=BOT_REPLIES['to_main_menu_from_battery'][language])

        builder.adjust(1)
        keyboard = builder.as_markup(resize_keyboard=True)

        text = f"{message.text} - {comment}"
        text = text[:250]
        await add_invalid_try(db=db, telegram_id=message.from_user.id, battery_number=text)
        mes=await message.answer('Наверное ошиблись, ещё раз попробуйте.',reply_markup=keyboard)
        state_dict['kill_message'].append(mes.message_id)
        await state.set_data(state_dict)

router.callback_query.register(start_battery_register_way, F.data == Calls.REGISTRATION_BATTERY, StateFilter(SpecialStates.messages_of))
router.message.register(location_catch_and_ask_about_number, F.location, StateFilter(CatchBattery.catch_location))
router.message.register(location_catch_and_ask_about_number, F.text, StateFilter(CatchBattery.catch_location))
router.message.register(catch_image_and_ask_code, F.photo, StateFilter(CatchBattery.catch_image))
router.message.register(catch_image_and_ask_code, F.text, StateFilter(CatchBattery.catch_image))
router.message.register(catch_battery_number_end, F.text, StateFilter(CatchBattery.catch_battery))

