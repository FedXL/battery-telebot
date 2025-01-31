from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import save_profile_data_collected
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, SurveyStates, SpecialStates, SurveyLowStates
from bot_core.utils.download_replies import BOT_REPLIES
from bot_core.utils.support_foo import kill_messages

router = Router()

Init_chain_call = Calls.PROFILE.START_REGISTRATION
Incoming_direct_calls = (Calls.PROFILE.PHONE_COLLECT,
                         Calls.PROFILE.NAME_COLLECT,
                         Calls.PROFILE.EMAIL_COLLECT,
                         Calls.PROFILE.TRADING_POINT.NAME,
                         Calls.PROFILE.TRADING_POINT.ADDRESS)




class SurveyManager:
    """state manager"""
    name_list = [
        "first_name_collect",
        "second_name_collect",
        "patronymic_name_collect"
    ]
    email_list = ['email_collect']
    trade_point_name = ['trading_point_name_collect']
    trade_point_address = ['trading_point_address_collect']
    phone_list = ['phone_collect']

    class Seller:
        full_chain = [
            "first_name_collect",
            "second_name_collect",
            "patronymic_name_collect",
            "phone_collect",
            "email_collect",
            "trading_point_name_collect",
            "trading_point_address_collect"
        ]
    class Client:
        full_chain = [
            "first_name_collect",
            "second_name_collect",
            "patronymic_name_collect",
            "phone_collect",
            "email_collect"
        ]

def get_chain(seller_or_client, callback_data):
    chains_dict_seller = {
        Calls.PROFILE.START_REGISTRATION: SurveyManager.Seller.full_chain if seller_or_client == 'seller' else SurveyManager.Client.full_chain,
        Calls.PROFILE.NAME_COLLECT: SurveyManager.name_list,
        Calls.PROFILE.PHONE_COLLECT: SurveyManager.phone_list,
        Calls.PROFILE.EMAIL_COLLECT: SurveyManager.email_list,
        Calls.PROFILE.TRADING_POINT.NAME: SurveyManager.trade_point_name,
        Calls.PROFILE.TRADING_POINT.ADDRESS: SurveyManager.trade_point_address
    }
    chain:list = chains_dict_seller.get(callback_data)
    new_chain:list = chain.copy()
    return new_chain

def get_state_element_from_chain(seller_or_client, chained_element):
    if seller_or_client == 'seller':
        my_dict = {
            "first_name_collect": SurveyStates.first_name_collect,
            "second_name_collect": SurveyStates.second_name_collect,
            "patronymic_name_collect": SurveyStates.patronymic_name_collect,
            "phone_collect": SurveyStates.phone_collect,
            "email_collect": SurveyStates.email_collect,
            "trading_point_name_collect": SurveyStates.trading_point_name_collect,
            "trading_point_address_collect": SurveyStates.trading_point_address_collect
        }
    else:
        my_dict = {
            "first_name_collect": SurveyLowStates.first_name_collect,
            "second_name_collect": SurveyLowStates.second_name_collect,
            "patronymic_name_collect": SurveyLowStates.patronymic_name_collect,
            "phone_collect": SurveyLowStates.phone_collect,
            "email_collect": SurveyLowStates.email_collect
        }
    return my_dict[chained_element]


seller_callback_to_state_dict = {
    Calls.PROFILE.NAME_COLLECT: SurveyStates.first_name_collect,
    Calls.PROFILE.PHONE_COLLECT: SurveyStates.phone_collect,
    Calls.PROFILE.EMAIL_COLLECT: SurveyStates.email_collect,
    Calls.PROFILE.TRADING_POINT.NAME:SurveyStates.trading_point_name_collect,
    Calls.PROFILE.TRADING_POINT.ADDRESS: SurveyStates.trading_point_address_collect
}

client_callback_to_state_dict = {
    Calls.PROFILE.NAME_COLLECT: SurveyLowStates.first_name_collect,
    Calls.PROFILE.PHONE_COLLECT: SurveyLowStates.phone_collect,
    Calls.PROFILE.EMAIL_COLLECT: SurveyLowStates.email_collect
}

def get_first_state_from_callback(seller_or_client, callback_data):
    """это только для start_survey"""
    if seller_or_client == 'seller':
        return seller_callback_to_state_dict[callback_data]
    else:
        return client_callback_to_state_dict[callback_data]


async def start_survey(callback: CallbackQuery, state: FSMContext) -> None:
    state_dict = await state.get_data()
    bot_log.info(f"START SURVEY {state_dict}")
    state_dict['collected_data'] = {}
    state_dict['kill_messages'] = []
    state_dict['state_chain'] = []
    seller_or_client = state_dict['client_or_seller']
    language = state_dict['language']
    chain = get_chain(seller_or_client=seller_or_client, callback_data=callback.data)

    if callback.data == Init_chain_call:
        bot_log.warning(f"Full chain call {callback.data} | {language}")
        text=BOT_REPLIES['first_name_collect'][language]
        await callback.answer('Ok')
        result = await callback.message.edit_text(text)
        catch_state = get_first_state_from_callback(seller_or_client, Calls.PROFILE.NAME_COLLECT)
    elif callback.data in  Incoming_direct_calls:
        bot_log.warning(f"Direct call {callback.data}")
        text = BOT_REPLIES[chain[0]][language]
        catch_state = get_first_state_from_callback(seller_or_client, callback.data)
        await callback.answer('Ok')
        result = await callback.message.edit_text(text=text)
    else:
        bot_log.error(f"Unknown callback data {callback.data}")
        raise ValueError('Unknown callback data')

    state_dict['kill_messages'].append(result.message_id)
    state_dict['state_chain'] = chain
    await state.set_data(state_dict)
    bot_log.critical(f"Start Survey ends: {state_dict}")
    await state.set_state(catch_state)
    if len(chain) ==1:
        await state.set_state(SpecialStates.end_survey)
        bot_log.critical(
            '<-!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!<<-ALARM +|+ ZERO->>!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!->')
        return


async def catch_survey(message: Message,state:FSMContext):
    bot_log.info(f"CATCH SURVEY ----------------------")
    state_name = await state.get_state()
    state_key = state_name.split(':')[-1]
    state_dict = await state.get_data()
    bot_log.info(f"catch_survey {state_dict}")
    state_dict['collected_data'][state_key] = message.text
    state_dict['kill_messages'].append(message.message_id)
    seller_or_client = state_dict['client_or_seller']
    language = state_dict['language']
    chain = state_dict['state_chain']
    chain.pop(0)
    next_chain_element = chain[0] if chain else None
    next_chain_element2 = chain[1] if chain and len(chain) > 1 else None
    if next_chain_element:
        builder = ReplyKeyboardBuilder()
        builder.button(text=BOT_REPLIES['skip_button'][language])
        builder.adjust(1)
        keyboard = builder.as_markup(resize_keyboard=True)



        text = BOT_REPLIES[next_chain_element][language]
        if next_chain_element == 'email_collect':
            result = await message.answer(text,reply_markup=keyboard)
        else:
            result = await message.answer(text, reply_markup=ReplyKeyboardRemove())
        state_dict['kill_messages'].append(result.message_id)
        state_dict['state_chain'] = chain
    bot_log.info(f"catch_survey {state_dict}")
    await state.set_data(state_dict)
    if next_chain_element2 is None:
        await state.set_state(SpecialStates.end_survey)
        bot_log.critical(
            '<-!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!<<-ALARM +|+ ZERO->>!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!->')
        return
    await state.set_state(get_state_element_from_chain(seller_or_client, next_chain_element))


async def end_survey(message: Message, state:FSMContext, db: AsyncSession):
    bot_log.info(f"END SURVEY -----------------------")
    state_dict = await state.get_data()
    state_name = await state.get_state()
    state_key = state_name.split(':')[-1]
    state_dict['kill_messages'].append(message.message_id)
    last_chain_element = state_dict['state_chain'].pop(0)
    state_dict['collected_data'][last_chain_element] = message.text
    profile_dict = state_dict.get('profile')
    language = state_dict['language']
    await kill_messages(message, killing_list=state_dict['kill_messages'])
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=BOT_REPLIES['comeback'][language], callback_data=Calls.GO_TO_PROFILE))
    builder.adjust(1)
    keyboard = builder.as_markup()
    await save_profile_data_collected(state_data=state_dict, db=db, telegram_id=message.from_user.id)
    result = await message.answer('_', reply_markup=ReplyKeyboardRemove())

    await message.answer(BOT_REPLIES['data_received'][language], reply_markup=keyboard)
    await result.delete()
    await state.clear()
    await state.set_state(SpecialStates.messages_of)

router.callback_query.register(start_survey, F.data.in_([Calls.PROFILE.START_REGISTRATION,Calls.PROFILE.PHONE_COLLECT,
                                Calls.PROFILE.NAME_COLLECT, Calls.PROFILE.EMAIL_COLLECT,
                                Calls.PROFILE.TRADING_POINT.NAME, Calls.PROFILE.TRADING_POINT.ADDRESS]), StateFilter(SpecialStates.messages_of))
router.message.register(catch_survey, StateFilter(SurveyStates, SurveyLowStates))
router.message.register(end_survey, StateFilter(SpecialStates.end_survey))


















