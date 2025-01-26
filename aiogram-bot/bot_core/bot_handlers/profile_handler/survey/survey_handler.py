from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls

router = Router()


class SurveyStates(StatesGroup):
    """Класс для хранения состояний"""
    first_name_collect = State()
    second_name_collect = State()
    patronymic_name_collect = State()
    phone_collect = State()
    email_collect = State()
    trading_point_name_collect = State()
    trading_point_address_collect = State()

SURVEY_QUESTIONS_RUS = {
    "first_name_collect": "Введите ваше имя",
    "second_name_collect": "Введите вашу фамилию",
    "patronymic_name_collect": "Введите ваше отчество",
    "phone_collect": "Введите ваш номер телефона",
    "email_collect": "Введите ваш email",
    "trading_point_name_collect": "Введите название вашей торговой точки",
    "trading_point_address_collect": "Введите адрес вашей торговой точки",
}

SURVEY_QUESTIONS_KAZ = {
    "first_name_collect": "Атыңызды енгізіңіз",
    "second_name_collect": "Тегіңізді енгізіңіз",
    "patronymic_name_collect": "Әкеңіздің атын енгізіңіз",
    "phone_collect": "Телефон нөміріңізді енгізіңіз",
    "email_collect": "Электрондық поштаңызды енгізіңіз",
    "trading_point_name_collect": "Сауда нүктеңіздің атауын енгізіңіз",
    "trading_point_address_collect": "Сауда нүктеңіздің мекенжайын енгізіңіз",
}


def get_ask_text(callback_data:str,language:str) -> str:
    if language=='rus':
        text=SURVEY_QUESTIONS_RUS[callback_data]
    elif language=='kaz':
        text=SURVEY_QUESTIONS_KAZ[callback_data]

async def start_survey(callback: CallbackQuery, state: FSMContext) -> None:
    """Запуск опроса"""
    state_dict = await state.get_data()
    language = state_dict.get('language')


    if callback.data == Calls.PROFILE.START_REGISTRATION:
        text="Теперь введите ваше имя"
        await state.set_state(SurveyStates.first_name_collect)
        await callback.message.answer(text)
        '''ну тогда у меня полный путь будет и будем счелкать по очереди stats'''


async def catch_survey(message: Message,state:FSMContext):
    state_name = await state.get_state()
    state_dict = await state.get_data()
    language = state_dict.get('language')
    bot_log.info(f'state_name{state_name} | state dict {state_dict}')
    text_key = state_name.replace("SurveyStates:",'')

    if language == 'rus':
        text = SURVEY_QUESTIONS_RUS[text_key]
    elif language == 'kaz':
        text = SURVEY_QUESTIONS_KAZ[text_key]
    else:
        raise ValueError(f'Unsupported language type {language}')















router.callback_query.register(start_survey, F.data.in_(Calls.PROFILE.START_REGISTRATION,
                                                        Calls.PROFILE.PHONE_COLLECT,
                                                        Calls.PROFILE.NAME_COLLECT,
                                                        Calls.PROFILE.EMAIL_COLLECT,
                                                        Calls.PROFILE.TRADING_POINT.NAME,
                                                        Calls.PROFILE.TRADING_POINT.ADDRESS))

router.message.register(catch_survey,StateFilter(SurveyStates))