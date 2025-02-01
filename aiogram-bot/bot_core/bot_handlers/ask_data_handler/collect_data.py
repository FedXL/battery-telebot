import logging
from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, CollectDataStates, SpecialStates
from bot_core.utils.download_replies import BOT_REPLIES

router = Router()

def keyboard_menu_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Русский",callback_data=Calls.SellerClient_PLUS_RUS),
                types.InlineKeyboardButton(text="Қазақша", callback_data=Calls.SellerClient_PLUS_KAZ))
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
    builder.add(
                types.InlineKeyboardButton(text=client_text, callback_data=Calls.ARE_U_SURE_CLIENT),
                types.InlineKeyboardButton(text=seller_text, callback_data=Calls.ARE_U_SURE_SELLER))
    builder.adjust(2)
    keyboard = builder.as_markup()
    return keyboard


async def ask_about_language(callback: types.CallbackQuery, state: FSMContext) -> None:
    bot_log.info(f"ASK ABOUT LANGUAGE HANDLER")
    await callback.answer('Ok')
    logging.info(f"ask_about_language {callback.from_user.username}")
    await callback.message.edit_text(text=create_replier_language_choice(callback.from_user.username),
                                  reply_markup=keyboard_menu_kb())


async def catch_language_choice_and_ask_about_seller_or_client(callback: types.CallbackQuery, state: FSMContext) -> None:
    bot_log.info(f'ASK ABOUT SELLER HANDLER')
    """Дальше спрашиваем юзер он продавец или покупатель"""
    await callback.answer('Ok')
    # await state.set_state(CollectDataStates.messages_of)
    if callback.data == Calls.SellerClient_PLUS_RUS:
        language = 'rus'
    elif callback.data == Calls.SellerClient_PLUS_KAZ:
        language = 'kaz'
    else:
        raise ValueError("Unknown language, stupid callback")
    state_data = await state.get_data()
    state_data['language'] = language
    await state.set_data(state_data)
    keyboard = seller_or_client_keyboard(language)
    seller_or_client_text = BOT_REPLIES["seller_or_client"][language]
    await callback.message.edit_text(seller_or_client_text, reply_markup=keyboard)


async def confirm_choice (callback: types.CallbackQuery, state: FSMContext) -> None:
    state_dict = await state.get_data()
    bot_log.info(f'CONFIRM CHOICE HANDLER: {state_dict}')
    language = state_dict.get('language')

    await callback.answer('Ok')
    if callback.data == Calls.ARE_U_SURE_SELLER:
        text = BOT_REPLIES['confirm_seller'][language]
        action_go = Calls.RULES_SELLER

    elif callback.data == Calls.ARE_U_SURE_CLIENT:
        text = BOT_REPLIES['confirm_client'][language]
        action_go = Calls.RULES_CLIENT
    else:
        raise ValueError("Unknown user type")
    if language == 'rus':
        action_comeback=Calls.SellerClient_PLUS_RUS
    elif language == 'kaz':
        action_comeback = Calls.SellerClient_PLUS_KAZ
    else:
        raise ValueError("Unknown language")
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES["confirm_choice_button"][language], callback_data=action_go),
                types.InlineKeyboardButton(text=BOT_REPLIES["comeback"][language], callback_data=action_comeback))
    builder.adjust(1)
    keyboard = builder.as_markup()
    await callback.message.edit_text(text=text, reply_markup=keyboard)




async def catch_client_or_seller_and_ask_about_rules(callback: types.CallbackQuery, state: FSMContext) -> None:
    bot_log.info('ASK ABOUT RULES HANDLER')
    state_dict = await state.get_data()
    language = state_dict.get('language')
    await callback.answer('Ok')
    if callback.data == Calls.RULES_CLIENT:
        state_dict['client_or_seller'] = 'client'
        text = BOT_REPLIES['rules_client_text'][language]
        action = Calls.CLIENT_CHOICE
    elif callback.data == Calls.RULES_SELLER:
        text = BOT_REPLIES['rules_seller_text'][language]
        action = Calls.SELLER_CHOICE
        state_dict['client_or_seller'] = 'seller'
    else:
        raise ValueError("Unknown user type")
    keyboard = yes_no_buttons(yes_action=action, no_action=Calls.START_MENU, language=language)
    await state.set_data(state_dict)
    await callback.message.edit_text(text=text, reply_markup=keyboard)





router.callback_query.register(ask_about_language, F.data == Calls.ASK_ABOUT_LANGUAGE,StateFilter(SpecialStates.messages_of))
router.callback_query.register(catch_language_choice_and_ask_about_seller_or_client, F.data.in_([Calls.SellerClient_PLUS_KAZ,Calls.SellerClient_PLUS_RUS]),StateFilter(SpecialStates.messages_of))
router.callback_query.register(confirm_choice, F.data.in_([Calls.ARE_U_SURE_SELLER, Calls.ARE_U_SURE_CLIENT]), StateFilter(SpecialStates.messages_of))
router.callback_query.register(catch_client_or_seller_and_ask_about_rules, F.data.in_([Calls.RULES_CLIENT, Calls.RULES_SELLER]), StateFilter(SpecialStates.messages_of))


