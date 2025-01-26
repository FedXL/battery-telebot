from aiogram.fsm.state import StatesGroup, State


class Calls:
    """Класс для хранения callback_data"""
    START_MENU = 'start_menu'
    ASK_ABOUT_LANGUAGE = "ask_about_language"

    RULES = "rules"
    RULES_CLIENT = "rules_client"
    RULES_SELLER = "rules_seller"

    SellerClient_PLUS_RUS = "sellerclient_rus"
    SellerClient_PLUS_KAZ = "sellerclient_kaz"
    SELLER_OR_CLIENT = "seller_or_client"

    SELLER_CHOICE = "mainmenu_seller"
    CLIENT_CHOICE = "mainmenu_client"

    MAIN_MENU = "mainmenu"

    LOTTERY_RESULTS = "lottery_results"
    GO_TO_PROFILE = "go_to_profile"
    REGISTRATION_BATTERY = "registration_battery"
    HELP = "help"

    CHANGE_LANGUAGE = 'profile_change_language'
    CHANGE_LANGUAGE_RUS = 'change_language_rus'
    CHANGE_LANGUAGE_KAZ = 'change_language_kaz'

    class PROFILE:
        START_REGISTRATION = 'profile_collect_all_data'
        NAME_COLLECT = 'profile_collect_name'
        PHONE_COLLECT = 'profile_collect_phone'
        EMAIL_COLLECT = 'profile_collect_email'

        class TRADING_POINT:
            NAME = 'profile_collect_trading_point_name'
            ADDRESS = 'profile_collect_trading_point_address'


class CollectDataStates(StatesGroup):
    messages_on = State()
    messages_of = State()