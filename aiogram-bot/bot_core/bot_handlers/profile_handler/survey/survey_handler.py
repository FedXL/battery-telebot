from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot_core.bot_db.db_handlers import save_profile_data_collected
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls, SurveyStates, create_state_dict, SpecialStates, SurveyLowStates
from bot_core.utils.download_replies import BOT_REPLIES
from bot_core.utils.support_foo import kill_messages

router = Router()



Support = {
    "first_name_collect",
    "second_name_collect",
    "patronymic_name_collect",
    "phone_collect",
    "email_collect",
    "trading_point_name_collect",
    "trading_point_address_collect"
}

CallsForStartSurvey = (Calls.PROFILE.PHONE_COLLECT, Calls.PROFILE.NAME_COLLECT, Calls.PROFILE.EMAIL_COLLECT,
                                Calls.PROFILE.TRADING_POINT.NAME, Calls.PROFILE.TRADING_POINT.ADDRESS)




async def start_survey(callback: CallbackQuery, state: FSMContext) -> None:
    """Запуск опроса"""
    state_dict = await state.get_data()
    state_dict['profile'] = {}
    state_dict['kill_messages'] = []

    language = state_dict.get('language')
    if callback.data == Calls.PROFILE.START_REGISTRATION:
        text=BOT_REPLIES['first_name_collect'][language]
        await callback.answer('Ok')
        if state_dict.get('client_or_seller') == 'seller':
            await state.set_state(SurveyStates.first_name_collect)
        else:
            await state.set_state(SurveyLowStates.first_name_collect)
        result = await callback.message.edit_text(text)
        kill_messages1 = [result.message_id]
        state_dict['kill_messages'] = kill_messages1
        await state.set_data(state_dict)
    elif callback.data in  CallsForStartSurvey:
        text = BOT_REPLIES['phone_collect'][language]
        await callback.answer('Ok')
        await callback.message.answer('Введите телефон')
        bot_log.warning(f"CALLBACK DATA {callback.data}")




        # if state_dict.get('client_or_seller') == 'seller':
        #     await state.set_state(SurveyStates.phone_collect)
        # else:
        #     await state.set_state(SurveyLowStates.phone_collect)
        # result = await callback.message.edit_text(text)
        # kill_messages1 = [result.message_id]
        # state_dict['kill_messages'] = kill_messages1
        # await state.set_data(state_dict)



async def catch_survey(message: Message,state:FSMContext):
    state_name = await state.get_state()
    state_dict = await state.get_data()
    bot_log.info(f'CATCH SURVEY {state_name} | {state_dict}')
    profile_dict = state_dict.get('profile')

    seller_or_client = state_dict.get('client_or_seller')
    if seller_or_client == 'seller':
        full_states_group = SurveyStates
        replace_name = 'SurveyStates:'
    else:
        full_states_group = SurveyLowStates
        replace_name = 'SurveyLowStates:'
    profile_dict[state_name] = message.text
    state_dict['profile'] = profile_dict
    kill_list = state_dict.get('kill_messages')
    kill_list.append(message.message_id)

    language = state_dict.get('language')
    bot_log.info(f'state_name{state_name} | state dict {state_dict}')
    text_key = state_name.replace(replace_name,'')
    text = BOT_REPLIES[text_key][language]
    result=await message.answer(text)
    kill_list.append(result.message_id)
    state_dict['kill_messages'] = kill_list
    await state.set_data(state_dict)

    if seller_or_client == 'seller':
        full_states_group = SurveyStates
        replace_name = 'SurveyStates:'
    else:
        full_states_group = SurveyLowStates
        replace_name = 'SurveyLowStates:'
    states_dict = create_state_dict(full_states_group)
    bot_log.info(states_dict)
    next_state = states_dict[state_name]['next_state']
    if next_state is None:
        await state.set_state(SpecialStates.end_survey)
        return
    next_state_r = next_state.replace(replace_name, '')
    bot_log.warning(next_state_r)
    await state.set_state(getattr(full_states_group, next_state_r))

async def end_survey(message: Message, state:FSMContext,db: AsyncSession):
    state_dict = await state.get_data()
    kill_list = state_dict.get('kill_messages')
    kill_list.append(message.message_id)

    profile_dict = state_dict.get('profile')
    await save_profile_data_collected(state_data=state_dict,db=db,telegram_id=message.from_user.id)
    bot_log.info(state_dict)
    await kill_messages(message, killing_list=kill_list)
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Назад", callback_data=Calls.GO_TO_PROFILE))
    builder.adjust(1)
    keyboard = builder.as_markup()
    result = await message.answer('Спасибо за регистрацию',reply_markup=keyboard)


router.callback_query.register(start_survey, F.data.in_([Calls.PROFILE.START_REGISTRATION,Calls.PROFILE.PHONE_COLLECT,
                                Calls.PROFILE.NAME_COLLECT, Calls.PROFILE.EMAIL_COLLECT,
                                Calls.PROFILE.TRADING_POINT.NAME, Calls.PROFILE.TRADING_POINT.ADDRESS]), StateFilter(None))
router.message.register(catch_survey, StateFilter(SurveyStates, SurveyLowStates))
router.message.register(end_survey, StateFilter(SpecialStates.end_survey))