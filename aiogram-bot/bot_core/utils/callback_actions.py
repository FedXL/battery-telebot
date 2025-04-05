from aiogram.fsm.state import StatesGroup, State


class Calls:
    """Класс для хранения callback_data"""
    START_MENU = 'start_menu'
    ASK_ABOUT_LANGUAGE = "ask_about_language"

    CATCH_MESSAGE = "catch_message"


    MY_BATTERY_LIST = "my_battery_list"
    MY_SELLER_LIST = "my_seller_list"

    RULES = "rules"
    RULES_CLIENT = "rules_client"
    RULES_SELLER = "rules_seller"
    RULES_WATCH = 'rules_watch'

    ARE_U_SURE_SELLER = 'are_u_sure_seller'
    ARE_U_SURE_CLIENT = 'are_u_sure_client'

    SellerClient_PLUS_RUS = "sellerclient_rus"
    SellerClient_PLUS_KAZ = "sellerclient_kaz"
    SELLER_OR_CLIENT = "client_or_seller"



    SELLER_CHOICE = "mainmenu_seller"
    CLIENT_CHOICE = "mainmenu_client"

    MAIN_MENU = "mainmenu"

    LOTTERY_RESULTS_SELLERS = "lottery_results_for_seller"
    LOTTERY_RESULTS_CLIENTS = "lottery_results_for_client"
    GO_TO_PROFILE = "go_to_profile"
    REGISTRATION_BATTERY = "registration_battery"
    REGISTRATION_CODE = 'registration_code'
    HELP = "help"

    CHANGE_LANGUAGE = 'profile_change_language'
    CHANGE_LANGUAGE_RUS = 'change_language_rus'
    CHANGE_LANGUAGE_KAZ = 'change_language_kaz'

    AGREEMENT_WATCH = 'agreement_watch'

    GO_TO_FAQ = 'go_to_faq'

    class PROFILE:
        START_REGISTRATION = 'profile_collect_all_data'
        NAME_COLLECT = 'profile_collect_name'
        PHONE_COLLECT = 'profile_collect_phone'
        EMAIL_COLLECT = 'profile_collect_email'
        GO_TO_PROFILE = 'go_to_profile'
        AGREEMENT = 'agreement'
        class TRADING_POINT:
            NAME = 'profile_collect_trading_point_name'
            ADDRESS = 'profile_collect_trading_point_address'


class CollectDataStates(StatesGroup):
    messages_on = State()
    messages_of = State()


class SurveyStates(StatesGroup):
    """Класс для хранения состояний"""
    first_name_collect = State()
    second_name_collect = State()
    patronymic_name_collect = State()
    phone_collect = State()
    email_collect = State()
    trading_point_name_collect = State()
    trading_point_address_collect = State()

class SurveyLowStates(StatesGroup):
    first_name_collect = State()
    second_name_collect = State()
    patronymic_name_collect = State()
    phone_collect = State()
    email_collect = State()


class StateNode:
    pass


class SpecialStates(SurveyStates):
    end_survey = State()
    messages_of = State()

    messanger = State()

class RegisterBattery(StatesGroup):
    catch_location = State()
    catch_battery = State()

class CatchBattery(StatesGroup):
    """Стейты для регистрации аккумулятора"""
    # catch_location = State()
    catch_image = State()
    catch_battery = State()

class CatchCode(StatesGroup):
    start = State()
    catch_code = State()
    end = State()