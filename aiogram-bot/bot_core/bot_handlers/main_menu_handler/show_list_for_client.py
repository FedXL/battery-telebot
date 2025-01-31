from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import get_battery_by_client_telegram_id
from bot_core.utils.callback_actions import Calls, SpecialStates
from bot_core.utils.download_replies import BOT_REPLIES

router = Router()

def comeback_to_main_menu_kb(language)->types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['comeback'][language], callback_data=Calls.GO_TO_PROFILE))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard

async def create_my_battery_list(callback: types.CallbackQuery,db: AsyncSession, state:FSMContext) -> None:
    await callback.answer('ok')
    language=await state.get_value('language')
    result=await get_battery_by_client_telegram_id(db, callback.from_user.id)
    text = callback.from_user.username
    text += "\nСписок ваших аккумуляторов"
    if result:
        you_have_a_code = False
        for key,value in result.items():
            if value.get('confirmation_code'):
                code_or_seller = value.get('confirmation_code')
                you_have_a_code =True
            else:
                seller  = value.get('seller_id')
                code_or_seller = f'Продавец №{seller}'

            text += f"\n{key}: {value.get('serial')} <code>{code_or_seller}</code>"
    else:
        text += "\n\n У вас нет аккумуляторов в системе."
    await callback.message.edit_text(text, reply_markup=comeback_to_main_menu_kb(language=language))


router.callback_query.register(create_my_battery_list, F.data == Calls.MY_BATTERY_LIST, StateFilter(SpecialStates.messages_of))