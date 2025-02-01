from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import SpecialStates, Calls
from bot_core.utils.download_replies import BOT_REPLIES
from bot_core.utils.support_foo import comeback_to_main_menu_kb

router = Router()



async def lottery_result(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer('ok')
    bot_log.info('START lottery_result')
    state_dict = await state.get_data()
    kill_messages = state_dict.get('kill_message')
    if not kill_messages:
        state_dict['kill_message'] = []
    language = state_dict.get('language')
    text = BOT_REPLIES['lottery_result_text'][language]
    await callback.message.delete()
    res=await callback.message.answer(text, reply_markup=comeback_to_main_menu_kb(language=language))


    await state.set_data(state_dict)




router.callback_query.register(lottery_result, F.data == Calls.LOTTERY_RESULTS, StateFilter(SpecialStates.messages_of))