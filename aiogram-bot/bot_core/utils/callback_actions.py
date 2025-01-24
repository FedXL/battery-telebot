from aiogram.fsm.state import StatesGroup, State


class Calls:
    """Класс для хранения callback_data"""
    START_MENU = 'start_menu'
    ASK_ABOUT_LANGUAGE = "ask_about_language"

    RULES = "rules"
    RULES_RUS = "rules_rus"
    RULES_KAZ = "rules_kaz"

    SELLER_OR_CLIENT = "seller_or_client"

    SELLER_CHOICE = "mainmenu_seller"
    CLIENT_CHOICE = "mainmenu_client"

    MAIN_MENU = "mainmenu"

class CollectDataStates(StatesGroup):
    messages_on = State()
    messages_of = State()