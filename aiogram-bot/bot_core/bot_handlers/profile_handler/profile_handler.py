from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.db_handlers import check_user
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls
from bot_core.utils.download_replies import BOT_REPLIES

router = Router()

class KeyboardBuilder:
    def __init__(self,language:str,client_or_seller:str, config:bool):
        assert language in ('rus','kaz'), "Unknown language"
        assert client_or_seller in ('client','seller'), "Unknown user type"
        self.config = config
        self.language = language
        self.client_or_seller = client_or_seller
        self.__collect_button_texts()
    @property
    def create_kb(self):
        if not self.config:
            bot_log.critical("basic_kb")
            return self.__basic_kb()
        else:
            bot_log.critical('full_kb')
            return self.__full_kb()

    def __basic_kb(self):
        return self.__create_basic_kb()

    def __full_kb(self):
        if self.client_or_seller == 'client':
            return self.__create_client_full_kb()
        elif self.client_or_seller == 'seller':
            return self.__create_seller_full_kb()
        else:
            raise ValueError("Unknown user type")


    def __language_choice_button(self):
        if self.language == 'rus':
            rep=BOT_REPLIES['change_language_profile']['kaz']
            return types.InlineKeyboardButton(text=rep, callback_data=Calls.CHANGE_LANGUAGE_RUS)
        elif self.language == 'kaz':
            rep=BOT_REPLIES['change_language_profile']['rus']
            return types.InlineKeyboardButton(text=rep, callback_data=Calls.CHANGE_LANGUAGE_KAZ)
        else:
            raise ValueError("Unknown language")


    def __create_basic_kb(self):
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=self.button_start_req, callback_data=Calls.PROFILE.START_REGISTRATION))
        builder.add(self.__language_choice_button())
        builder.add(types.InlineKeyboardButton(text=self.button_comeback, callback_data=Calls.MAIN_MENU))
        builder.adjust(1)
        keyboard = builder.as_markup()
        return keyboard

    def __create_client_full_kb(self):
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=self.button_full_name, callback_data=Calls.PROFILE.NAME_COLLECT))
        builder.add(types.InlineKeyboardButton(text=self.button_phone, callback_data=Calls.PROFILE.PHONE_COLLECT))
        builder.add(types.InlineKeyboardButton(text=self.button_email, callback_data=Calls.PROFILE.EMAIL_COLLECT))
        builder.add(self.__language_choice_button())
        builder.add(types.InlineKeyboardButton(text=self.button_comeback, callback_data=Calls.MAIN_MENU))
        builder.adjust(2)
        keyboard = builder.as_markup()
        return keyboard

    def __create_seller_full_kb(self):
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=self.button_full_name, callback_data=Calls.PROFILE.NAME_COLLECT))
        builder.add(types.InlineKeyboardButton(text=self.button_phone, callback_data=Calls.PROFILE.PHONE_COLLECT))
        builder.add(types.InlineKeyboardButton(text=self.button_email, callback_data=Calls.PROFILE.EMAIL_COLLECT))
        builder.add(types.InlineKeyboardButton(text=self.button_trade_point_name, callback_data=Calls.PROFILE.TRADING_POINT.NAME))
        builder.add(types.InlineKeyboardButton(text=self.button_trade_point_address, callback_data=Calls.PROFILE.TRADING_POINT.ADDRESS))
        builder.add(self.__language_choice_button())
        builder.add(types.InlineKeyboardButton(text=self.button_comeback, callback_data=Calls.MAIN_MENU))
        builder.adjust(2)
        keyboard = builder.as_markup()
        return keyboard


    def __collect_button_texts(self):
        language = self.language
        self.button_start_req = BOT_REPLIES['profile_registration_button'][language]
        if language == 'rus':
            self.button_language = BOT_REPLIES['change_language_profile']['kaz']
        elif language == 'kaz':
            self.button_language = BOT_REPLIES['change_language_profile']['rus']

        self.button_comeback = BOT_REPLIES['comeback'][language]
        self.button_full_name = BOT_REPLIES['profile_full_name'][language]
        self.button_phone = BOT_REPLIES['profile_phone'][language]
        self.button_email = BOT_REPLIES['profile_email'][language]
        self.button_trade_point_name = BOT_REPLIES['trade_point_name'][language]
        self.button_trade_point_address = BOT_REPLIES['trade_point_address'][language]



class TextBuilder:

    def __init__(self,language: str,seller_or_client: str,profile_completeness:bool):
        self.language = language
        self.seller_or_client = seller_or_client
        self.profile_completeness = profile_completeness

    def test_creator(self, username,
                     first_name,
                     second_name,
                     patronymic,
                     phone_contact,
                     email,
                     trading_point_name,
                     trading_point,
                     seller_or_client):

        if self.language == 'rus':
            profile_type = "Профиль продавца" if seller_or_client == 'seller' else "Профиль клиента"
            lottery_status = "Профиль заполнен" if self.profile_completeness else "Профиль не заполнен"
            text = (f"{profile_type} <b>{username}</b>\n"
                        f"Имя: <code>{first_name}</code>\n"
                        f"Фамилия: <code>{second_name}</code>\n"
                        f"Отчество: <code>{patronymic}</code>\n"
                        f"Контактный телефон: <code>{phone_contact}</code>\n"
                        f"email: <code>{email}</code>\n\n"
                        )
            if seller_or_client=='seller':
                text += (
                    f"Название торговой точки: <code>{trading_point_name}</code>\n"
                    f"Адрес торговой точки: <code>{trading_point}</code>\n\n\n")
            text += f"Статус: <b>{lottery_status}</b>"

        elif self.language == 'kaz':
            profile_type = "Сатушы профилі" if seller_or_client == 'seller' else "Сатып алушы профилі"
            lottery_status = "Профиль толтырылды" if self.profile_completeness else "Профиль толтырылмады"
            text = (f"{profile_type}. <b>{username}</b>\n"
                        f"Аты: <code>{first_name}</code>\n"
                        f"Тегі: <code>{second_name}</code>\n"
                        f"Әкесінің аты: <code>{patronymic}</code>\n"
                        f"Байланыс телефоны: <code>{phone_contact}</code>\n"
                        f"Электронды пошта: <code>{email}</code>\n\n")
            if seller_or_client == 'seller':
                text += (f"Сауда нүктесінің атауы: <code>{trading_point_name}</code>\n"
                        f"Сауда нүктесінің мекенжайы: <code>{trading_point}</code>\n\n\n")
                text += f"Жағдай: <b>{lottery_status}</b>"
        else:
            raise ValueError('нет такого Language ')
        return text

async def profile_menu(callback: types.CallbackQuery , state: FSMContext, db: AsyncSession):
    result, result_dict = await check_user(db=db,telegram_id=callback.from_user.id)
    rus_or_kaz = result_dict['language']
    seller_or_client = result_dict['client_or_seller']
    profile_completeness = result_dict['profile_completeness']
    profile_data = result_dict['profile_data']
    await state.set_data(result_dict)

    bot_log.info(f"PROFILE MENU HANDLER {rus_or_kaz} | {seller_or_client} | {profile_completeness}")
    keyboard = KeyboardBuilder(language=rus_or_kaz, client_or_seller=seller_or_client, config=profile_completeness).create_kb
    TextConstrutor = TextBuilder(language=rus_or_kaz,seller_or_client=seller_or_client,profile_completeness=profile_completeness)
    text = TextConstrutor.test_creator(username=callback.from_user.username,
                                       first_name=profile_data.get('first_name','None'),
                                       second_name=profile_data.get('second_name','None'),
                                       patronymic=profile_data.get('patronymic','None'),
                                       phone_contact=profile_data.get('contact_phone','None'),
                                       email=profile_data.get('contact_email','None'),
                                       trading_point_name=profile_data.get('company_name','None'),
                                       trading_point=profile_data.get('company_address','None'),
                                       seller_or_client=seller_or_client,
                                       )
    await callback.answer('Profile')
    await callback.message.edit_text(text=text, reply_markup=keyboard)
router.callback_query.register(profile_menu, F.data == Calls.GO_TO_PROFILE,StateFilter(None))
