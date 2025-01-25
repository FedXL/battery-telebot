from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot_core.utils.callback_actions import Calls
from bot_core.utils.download_replies import BOT_REPLIES


def create_menu_main_kb(language:str) -> types.InlineKeyboardMarkup:

    lottery_result_button=BOT_REPLIES['lottery_result_button'][language]
    profile_button=BOT_REPLIES['profile_button'][language]
    register_battery_button=BOT_REPLIES['register_battery_button'][language]
    help_button_text=BOT_REPLIES['help_button'][language]

class ProfileMenu:
    def __init__(self,language:str,client_or_seller:str):
        assert language in ('rus','kaz'), "Unknown language"
        assert client_or_seller in ('client','seller'), "Unknown user type"
        self.language = language
        self.client_or_seller = client_or_seller

    @property
    def basic_kb(self):
        return self.__create_basic_kb()

    @property
    def full_kb(self):
        if self.client_or_seller == 'client':
            return self.__create_client_full_kb()
        elif self.client_or_seller == 'seller':
            return self.__create_seller_full_kb()
        else:
            raise ValueError("Unknown user type")


    def __create_basic_kb(self):
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Регистрация", callback_data=Calls.PROFILE.COLLECT_DATA))
        builder.add(types.InlineKeyboardButton(text="RUS", callback_data=Calls.CHANGE_LANGUAGE_RUS),
                    types.InlineKeyboardButton(text="KAZ", callback_data=Calls.CHANGE_LANGUAGE_KAZ))
        builder.add(types.InlineKeyboardButton(text="Назад в главное меню", callback_data=Calls.MAIN_MENU))
        builder.adjust(2)
        keyboard = builder.as_markup()
        return keyboard

    def __create_client_full_kb(self):
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="ФИO", callback_data=Calls.PROFILE.NAME_COLLECT))
        builder.add(types.InlineKeyboardButton(text="Телефон", callback_data=Calls.PROFILE.PHONE_COLLECT))
        builder.add(types.InlineKeyboardButton(text="RUS", callback_data=Calls.CHANGE_LANGUAGE_RUS),
                    types.InlineKeyboardButton(text="KAZ", callback_data=Calls.CHANGE_LANGUAGE_KAZ))
        builder.add(types.InlineKeyboardButton(text="Назад в главное меню", callback_data=Calls.MAIN_MENU))
        builder.adjust(2)
        keyboard = builder.as_markup()
        return keyboard

    def __create_seller_full_kb(self):
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="ФИO", callback_data=Calls.PROFILE.NAME_COLLECT))
        builder.add(types.InlineKeyboardButton(text="Телефон", callback_data=Calls.PROFILE.PHONE_COLLECT))
        builder.add(types.InlineKeyboardButton(text="Email", callback_data=Calls.PROFILE.EMAIL_COLLECT))
        builder.add(types.InlineKeyboardButton(text="Торговая точка", callback_data=Calls.PROFILE.TRADING_POINT.NAME))
        builder.add(types.InlineKeyboardButton(text="Адрес", callback_data=Calls.PROFILE.TRADING_POINT.ADDRESS))
        builder.add(types.InlineKeyboardButton(text="RUS", callback_data=Calls.CHANGE_LANGUAGE_RUS),
                    types.InlineKeyboardButton(text="KAZ", callback_data=Calls.CHANGE_LANGUAGE_KAZ))
        builder.add(types.InlineKeyboardButton(text="Назад в главное меню", callback_data=Calls.MAIN_MENU))
        builder.adjust(2)
        keyboard = builder.as_markup()
        return keyboard


async def profile_menu(callback_or_message: types.CallbackQuery | types.Message, state: FSMContext, db: AsyncSession):
    if isinstance(callback_or_message, types.CallbackQuery):


