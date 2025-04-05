from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, SpecialStates
from bot_core.utils.download_replies import BOT_REPLIES


router = Router()


def create_agreement_kb(language) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['yes'][language], callback_data=Calls.PROFILE.START_REGISTRATION),
                (types.InlineKeyboardButton(text=BOT_REPLIES['no'][language], callback_data=Calls.PROFILE.GO_TO_PROFILE)))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard

def comeback_to_main_menu_kb(language)->types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['comeback'][language], callback_data=Calls.MAIN_MENU))
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard

async def agreement_handler_foo(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик согласия на обработку персональных данных."""
    state_dict = await state.get_data()
    await callback.answer('Ok')
    bot_log.info(f"AGREEMENT HANDLER {callback.data}")
    language = state_dict['language']
    client_or_seller = state_dict['client_or_seller']

    if callback.data in [Calls.AGREEMENT_WATCH,Calls.PROFILE.AGREEMENT]:
        text = BOT_REPLIES['agreement'][language]
    elif callback.data == Calls.RULES_WATCH:
        if client_or_seller == 'seller':
            text = BOT_REPLIES['rules_seller_again_text'][language]
        elif client_or_seller == 'client':
            text = BOT_REPLIES['rules_client_again_text'][language]
    elif callback.data == Calls.GO_TO_FAQ:
        if client_or_seller == 'client':
            text = BOT_REPLIES['faq_text'][language]
        elif client_or_seller == 'seller':
            text = BOT_REPLIES['faq_seller_text'][language]
    else:
        raise ValueError(f"Unknown callback data: {callback.data}")

    if callback.data == Calls.PROFILE.AGREEMENT:
        keyboard_inline_menu = create_agreement_kb(language)
    else:
        keyboard_inline_menu = comeback_to_main_menu_kb(language)
    await callback.message.edit_text(text, reply_markup=keyboard_inline_menu)

router.callback_query.register(agreement_handler_foo, F.data==Calls.PROFILE.AGREEMENT, StateFilter(SpecialStates.messages_of))
router.callback_query.register(agreement_handler_foo, F.data==Calls.AGREEMENT_WATCH, StateFilter(SpecialStates.messages_of))
router.callback_query.register(agreement_handler_foo, F.data==Calls.RULES_WATCH, StateFilter(SpecialStates.messages_of))
router.callback_query.register(agreement_handler_foo, F.data==Calls.GO_TO_FAQ, StateFilter(SpecialStates.messages_of))
