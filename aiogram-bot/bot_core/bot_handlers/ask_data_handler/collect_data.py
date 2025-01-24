import logging
from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot_core.utils.callback_actions import Calls, CollectDataStates
from bot_core.utils.download_replies import BOT_REPLIES


router = Router()

def keyboard_menu_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Русский",
                                           callback_data=Calls.RULES_RUS),
                types.InlineKeyboardButton(text="Қазақша",
                                           callback_data=Calls.RULES_KAZ))
    builder.adjust(2)
    keyboard = builder.as_markup()
    return keyboard


def yes_no_buttons(yes_action:str,
                   no_action:str,
                   language: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    yes_text = BOT_REPLIES['yes'][language]
    no_text = BOT_REPLIES['no'][language]
    builder.add(types.InlineKeyboardButton(text=yes_text, callback_data=yes_action),
                types.InlineKeyboardButton(text=no_text, callback_data=no_action))
    builder.adjust(2)
    keyboard = builder.as_markup()
    return keyboard

def create_replier_language_choice(username):
    rus = BOT_REPLIES["choice_language_text"]["rus"]
    kaz = BOT_REPLIES["choice_language_text"]["kaz"]
    return f"{username}\n{rus}\n\n{kaz}"

def seller_or_client_keyboard(language):
    builder = InlineKeyboardBuilder()
    seller_text = BOT_REPLIES["seller_button"][language]
    client_text = BOT_REPLIES["client_button"][language]
    builder.add(types.InlineKeyboardButton(text=seller_text, callback_data=Calls.SELLER_CHOICE),
                types.InlineKeyboardButton(text=client_text, callback_data=Calls.CLIENT_CHOICE))
    builder.adjust(2)
    keyboard = builder.as_markup()
    return keyboard


async def ask_about_language(callback: types.CallbackQuery, state: FSMContext) -> None:

    await callback.answer('Ok')
    logging.info(f"ask_about_language {callback.from_user.username}")
    await callback.message.answer(text=create_replier_language_choice(callback.from_user.username),
                                  reply_markup=keyboard_menu_kb())
    await state.set_state(CollectDataStates.messages_of)


async def catch_language_choice_and_ask_about_rules(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Дальше спрашиваем юзер он продавец или покупатель"""
    await callback.answer('Ok')
    await state.set_state(CollectDataStates.messages_of)
    if callback.data == Calls.RULES_RUS:
        language = 'rus'
    elif callback.data == Calls.RULES_KAZ:
        language = 'kaz'
    else:
        raise ValueError("Unknown language, stupid callback")
    keyboard = yes_no_buttons(yes_action=Calls.SELLER_OR_CLIENT, no_action=Calls.START_MENU, language=language)
    state_data = await state.get_data()
    state_data['language'] = language
    await state.set_data(state_data)
    await callback.message.answer(BOT_REPLIES.get("rules_text").get(language),reply_markup=keyboard)


async def catch_rules_and_ask_seller_or_buyer(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer('Ok')
    await state.set_state(CollectDataStates.messages_of)
    state_data = await state.get_data()

    language = state_data.get('language')
    seller_or_client_text = BOT_REPLIES.get("seller_or_client").get(language)
    keyboard = seller_or_client_keyboard(language)

    await callback.message.answer(seller_or_client_text, reply_markup=keyboard)




router.callback_query.register(ask_about_language, F.data == Calls.ASK_ABOUT_LANGUAGE)
router.callback_query.register(catch_language_choice_and_ask_about_rules, F.data.in_([Calls.RULES_RUS,Calls.RULES_KAZ]),StateFilter(CollectDataStates.messages_of))
router.callback_query.register(catch_rules_and_ask_seller_or_buyer,F.data == Calls.SELLER_OR_CLIENT, StateFilter(CollectDataStates.messages_of))

