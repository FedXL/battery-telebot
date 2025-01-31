import asyncio
from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import check_user, get_battery_by_code, connect_battery_from_code_to_seller
from bot_core.utils.callback_actions import CatchBattery, CatchCode, Calls, SpecialStates
from bot_core.utils.check_battery import valid_code
from bot_core.utils.support_foo import delete_message_later, comeback_to_main_menu_kb, back_to_main_menu_kb

router = Router()

async def start_code_catch_for_seller(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession) -> None:
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
    if state_dict['client_or_seller'] == 'client':
        await callback.answer("❌")
        return

    await callback.answer('ok')
    language = state_dict['language']
    keyboard_reply=back_to_main_menu_kb(language)
    text = "Введите 6-ти значный код для регистрации аккумулятора"
    await callback.message.delete()
    result = await callback.message.answer(text = text, reply_markup=keyboard_reply)
    state_dict['kill_message'].append(result.message_id)
    await state.set_data(state_dict)
    await state.set_state(CatchCode.catch_code)


async def catch_code(message: types.Message, state: FSMContext, db:AsyncSession) -> None:
    """
        1) Получить геолокацию
        2) Проверить на валидность
        3) Сохранить в базу данных
    """
    state_dict = await state.get_data()
    language = state_dict.get('language')
    text = message.text
    is_valid, comment = valid_code(text)

    if is_valid:
        mes=await message.answer('код принят ищу батарею')
        battery = await get_battery_by_code(db=db,code=is_valid['code'])
        await mes.delete()
        if battery:
            mes=await message.answer(f"Аккумулятор найден: {battery.get('serial')}", reply_markup=back_to_main_menu_kb(language))
            state_dict['kill_message'].append(mes.message_id)
            result = await connect_battery_from_code_to_seller(db=db, code=is_valid['code'], seller_telegram_id=message.from_user.id)
            await message.answer(f"Продажа успешно зарегистрированная", reply_markup=comeback_to_main_menu_kb(language))
        else:
            mes = await message.reply(f"По такому коду не зарегистрирован ни один аккумулятор", reply_markup=back_to_main_menu_kb(language))
            state_dict['kill_message'].append(mes.message_id)
    else:
        mes=await message.reply(comment, reply_markup=back_to_main_menu_kb(language))
        state_dict['kill_message'].append(mes.message_id)
    await state.set_data(state_dict)

router.callback_query.register(start_code_catch_for_seller, F.data == Calls.REGISTRATION_CODE,
                               StateFilter(SpecialStates.messages_of))
router.message.register(catch_code, F.text, StateFilter(CatchCode.start, CatchCode.catch_code))
