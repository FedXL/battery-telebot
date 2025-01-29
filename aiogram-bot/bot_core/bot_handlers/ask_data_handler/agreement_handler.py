from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot_core.utils.callback_actions import Calls
from bot_core.utils.download_replies import BOT_REPLIES

router = Router()


def create_agreement_kb(language) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['yes'][language], callback_data=Calls.PROFILE.START_REGISTRATION),
                (types.InlineKeyboardButton(text=BOT_REPLIES['no'][language], callback_data=Calls.PROFILE.GO_TO_PROFILE)))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard

def agreement_kb_again(language)->types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['comeback'][language], callback_data=Calls.MAIN_MENU))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard

async def agreement_handler_foo(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик согласия на обработку персональных данных."""
    state_dict = await state.get_data()
    await callback.answer('Ok')
    language = state_dict['language']
    client_or_seller = state_dict['client_or_seller']

    if callback.data in [Calls.AGREEMENT_WATCH,Calls.PROFILE.AGREEMENT]:
        text = BOT_REPLIES['agreement'][language]
    elif callback.data == Calls.RULES_WATCH:
        if client_or_seller == 'seller':
            text = BOT_REPLIES['rules_seller_text'][language]
        elif client_or_seller == 'client':
            text = BOT_REPLIES['rules_client_text'][language]
    elif callback.data == Calls.GO_TO_FAQ:
        text = BOT_REPLIES['faq_text'][language]
    else:
        raise ValueError(f"Unknown callback data: {callback.data}")

    if callback.data == Calls.PROFILE.AGREEMENT:
        keyboard_inline_menu = create_agreement_kb(language)
    else:
        keyboard_inline_menu = agreement_kb_again(language)
    await callback.message.edit_text(text, reply_markup=keyboard_inline_menu)

router.callback_query.register(agreement_handler_foo, F.data==Calls.PROFILE.AGREEMENT, StateFilter(None))
router.callback_query.register(agreement_handler_foo, F.data==Calls.AGREEMENT_WATCH, StateFilter(None))
router.callback_query.register(agreement_handler_foo, F.data==Calls.RULES_WATCH, StateFilter(None))
router.callback_query.register(agreement_handler_foo, F.data==Calls.GO_TO_FAQ, StateFilter(None))
