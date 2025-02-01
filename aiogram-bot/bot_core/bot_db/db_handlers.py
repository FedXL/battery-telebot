import random
from datetime import datetime
from typing import Union, Dict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from bot_core.bot_db.alchemy_models import UserTelegram, Client, Seller, ClientProfile, SellerProfile, InvalidTry, \
    Battery, TelegramMessage
from bot_core.create_bot import bot_log
from bot_core.utils.callback_actions import Calls


async def check_user(telegram_id, db: AsyncSession) -> Union[bool, bool] or Union[bool, Dict[str, str]]:
    """
        Check if a user exists and has a profile.

        Returns:
            (bool, bool):
                - (False, False) if user not found.
                - (True, False) if user found but no profile.
                - (True, Dict[str, str]) if user found and has profile.
    """

    bot_log.info(f'Checking user {telegram_id}')
    async with db.begin():
        telegram_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        telegram_user = telegram_user.scalar_one_or_none()
        if not telegram_user:
            return False, False
        client = await db.execute(select(Client).filter(Client.user_telegram_id == telegram_user.telegram_id))
        client = client.scalar_one_or_none()
        seller = await db.execute(select(Seller).filter(Seller.user_telegram_id == telegram_user.telegram_id))
        seller = seller.scalar_one_or_none()
        if client and seller:
            raise Exception('User has both client and seller profiles')
        if not client and not seller:
            return True, False
        if client:
            bot_log.info(f'User {telegram_id} is client')
            client_or_seller='client'
            profile = await db.execute(select(ClientProfile).filter(ClientProfile.client_id == client.id))
            bot_log.info(f'Profile is query{profile}')
        elif seller:
            bot_log.info(f'User {telegram_id} is seller')
            client_or_seller='seller'
            profile = await db.execute(select(SellerProfile).filter(SellerProfile.seller_id == seller.id))
            bot_log.info(f'Profile is query {profile}')
        if not profile:
            return True, False
        profile = profile.scalar_one_or_none()
        bot_log.info(f'Profile is {profile}')
        if not profile:
            bot_log.critical('Profile not found but clien/seller is. Killing client or seller')
            if client:
                await db.delete(client)
            if seller:
                await db.delete(seller)
            await db.commit()
            return True, False


        try:
            is_full_profile = profile_completeness(profile=profile)
            profile_dict = profile_to_dict(profile=profile)
        except Exception as error:
            bot_log.error(f'some error {error}')


        profile_data_base = {'language': profile.language,
                             'profile_data': profile_dict,
                             'client_or_seller': client_or_seller,
                             'profile_completeness': is_full_profile}
        return True, profile_data_base

async def create_user(telegram_id, username, db: AsyncSession):
    async with db.begin():
        new_user = UserTelegram(
            telegram_id=telegram_id,
            username=username,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        await db.flush()
    return new_user


def profile_completeness(profile: Union[ClientProfile, SellerProfile]) -> bool:
    '''Надо для определения какой в меню профиля меню заказывать полное или урезанное'''
    if isinstance(profile, ClientProfile):
        bot_log.warning('CLIENT profile_completeness')
        bot_log.info(f"Profile is full {profile.first_name} | {profile.second_name} | {profile.patronymic} | {profile.contact_phone} | {profile.contact_email}")
        if profile.first_name and profile.second_name and profile.patronymic and profile.contact_phone and profile.contact_email:
            bot_log.warning('CLIENT profile_completeness is full')
            return True
        else:
            bot_log.warning('CLIENT profile_completeness is NOT full')
            return False
    elif isinstance(profile, SellerProfile):
        bot_log.warning('SELLER profile_completeness')
        bot_log.info(f"Profile is full {profile.first_name} | {profile.second_name} | {profile.patronymic} | {profile.company_address} | {profile.company_name} | {profile.contact_phone} | {profile.contact_email}")
        if profile.first_name and profile.second_name and profile.patronymic and profile.company_address and profile.company_name and profile.contact_phone and profile.contact_email:
            bot_log.warning('SELLER profile_completeness is full')
            return True
        else:
            bot_log.warning('SELLER profile_completeness is NOT full')
            return False
    else:
        raise Exception('Unknown profile type')

def profile_to_dict(profile: Union[ClientProfile,SellerProfile]) -> dict:
    profile_dict = {
        'client_or_seller': 'client',
        'phone_from_telegram': profile.phone_from_telegram,
        'first_name': profile.first_name,
        'second_name': profile.second_name,
        'patronymic': profile.patronymic,
        'contact_phone': profile.contact_phone,
        'contact_email': profile.contact_email,
        'language': profile.language
    }
    if isinstance(profile, SellerProfile):
        profile_dict['client_or_seller'] = 'seller'
        profile_dict['company_address'] = profile.company_address
        profile_dict['company_name'] = profile.company_name
    return profile_dict



async def create_profiles(db: AsyncSession,
                          rus_or_kaz: str,
                          callback_data:str,
                          telegram_id):
    async with db.begin():
        existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        existing_user = existing_user.scalar_one_or_none()
        if not existing_user:
            raise Exception('User not found')

        if callback_data == Calls.SELLER_CHOICE:
            existing_client = await db.execute(
                select(Client).filter(Client.user_telegram_id == existing_user.telegram_id))
            client = existing_client.scalar_one_or_none()
            if client:
                return False , f"На этот телеграм айди {telegram_id} уже зарегистрирован покупатель"
            new_seller = Seller(user_telegram_id=existing_user.telegram_id)
            db.add(new_seller)
            await db.flush()
            new_profile_seller = SellerProfile(seller_id=new_seller.id)
            new_profile_seller.language = rus_or_kaz
            db.add(new_profile_seller)

        elif callback_data == Calls.CLIENT_CHOICE:
            existing_seller = await db.execute(
                select(Seller).filter(Seller.user_telegram_id == existing_user.telegram_id))
            seller = existing_seller.scalar_one_or_none()
            if seller:
                return False, f"На этот телеграм айди {telegram_id} уже зарегистрирован продавец"
            new_client = Client(user_telegram_id=existing_user.telegram_id)
            db.add(new_client)
            await db.flush()
            new_client_profile = ClientProfile(client_id=new_client.id)
            new_client_profile.language = rus_or_kaz
            db.add(new_client_profile)
        else:
            return False, f'Непонятный callback_data {callback_data}'

    return True, 'Профиль создан'


async def save_profile_data_collected(db: AsyncSession, state_data: dict, telegram_id: int):
    async with db.begin():
        existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        existing_user = existing_user.scalar_one_or_none()
        if not existing_user:
            raise Exception('User not found')
        if state_data['client_or_seller'] == 'client':
            existing_client = await db.execute(
                select(Client).filter(Client.user_telegram_id == existing_user.telegram_id))
            client = existing_client.scalar_one_or_none()
            if not client:
                raise Exception('Client not found')
            existing_profile = await db.execute(select(ClientProfile).filter(ClientProfile.client_id == client.id))
            profile = existing_profile.scalar_one_or_none()
            if not profile:
                raise Exception('Profile not found')
            try:
                profile.first_name = state_data['collected_data']['first_name_collect']
            except:
                pass
            try:
                profile.second_name = state_data['collected_data']['second_name_collect']
            except:
                pass
            try:
                profile.patronymic = state_data['collected_data']['patronymic_name_collect']
            except:
                pass
            try:
                profile.contact_phone = state_data['collected_data']['phone_collect']
            except:
                pass
            try:
                profile.contact_email = state_data['collected_data']['email_collect']
            except:
                pass
            try:
                profile.language = state_data['language']
            except:
                pass
        elif state_data['client_or_seller'] == 'seller':
            existing_seller = await db.execute(
                select(Seller).filter(Seller.user_telegram_id == existing_user.telegram_id))
            seller = existing_seller.scalar_one_or_none()
            if not seller:
                raise Exception('Seller not found')
            existing_profile = await db.execute(select(SellerProfile).filter(SellerProfile.seller_id == seller.id))
            profile = existing_profile.scalar_one_or_none()
            if not profile:
                raise Exception('Profile not found')
            try:
                profile.first_name = state_data['collected_data']['first_name_collect']
            except:
                pass
            try:
                profile.second_name = state_data['collected_data']['second_name_collect']
            except:
                pass
            try:
                profile.patronymic = state_data['collected_data']['patronymic_name_collect']
            except:
                pass
            try:
                profile.contact_phone = state_data['collected_data']['phone_collect']
            except:
                pass
            try:
                profile.contact_email = state_data['collected_data']['email_collect']
            except:
                pass
            try:
                profile.language = state_data['language']
            except:
                pass
            try:
                profile.company_name = state_data['collected_data']['trading_point_name_collect']
            except:
                pass
            try:
                profile.company_address = state_data['collected_data']['trading_point_address_collect']
            except:
                pass
        else:
            raise Exception('Unknown client_or_seller')
    return True, 'Данные профиля сохранены'

async def add_invalid_try(db: AsyncSession, telegram_id: int,battery_number:str):
    async with db.begin():
        result = False
        try:
            existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
            existing_user = existing_user.scalar_one_or_none()
            if not existing_user:
                raise Exception('User not found')
            new_try = InvalidTry(telegram_user_id=existing_user.telegram_id, number=battery_number)
            db.add(new_try)
            await db.commit()
            result = True
        except IntegrityError:
            await db.rollback()
        finally:
            return result

async def get_battery_by_client_telegram_id(db: AsyncSession, telegram_id: int):
    bot_log.warning('START TO GET BATTERY from Client')
    async with db.begin():
        existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        existing_user = existing_user.scalar_one_or_none()
        if not existing_user:
            raise Exception('User not found')
        client = await db.execute(select(Client).filter(Client.user_telegram_id == existing_user.telegram_id))
        client = client.scalar_one_or_none()
        if not client:
            raise Exception('Client not found')
        batterys = await db.execute(select(Battery).filter(Battery.client_id == client.id))
        batterys = batterys.scalars().all()
        if not batterys:
            return
        result_dict= {}
        for num,battery in enumerate(batterys,1):
            result_dict[num] = battery.to_dict()
        return result_dict


async def get_battery_by_seller_telegram_id(db: AsyncSession, telegram_id: int):
    bot_log.warning('START TO GET BATTERY from Seller')
    async with db.begin():

        existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        existing_user = existing_user.scalar_one_or_none()

        if not existing_user:
            raise Exception('User not found')

        seller = await db.execute(select(Seller).filter(Seller.user_telegram_id == existing_user.telegram_id))
        seller = seller.scalar_one_or_none()

        if not seller:
            raise Exception('Client not found')

        batterys = await db.execute(select(Battery).filter(Battery.seller_id == seller.id))
        batterys = batterys.scalars().all()

        if not batterys:
            return

        result_dict= {}

        for num, battery in enumerate(batterys, 1):
            result_dict[num] = battery.to_dict()
        return result_dict



async def add_valid_battery(db: AsyncSession, telegram_id: str, data: dict):
    async with db.begin():
        existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
        existing_user = existing_user.scalar_one_or_none()
        if not existing_user:
            raise Exception('User not found')

        client = await db.execute(select(Client).filter(Client.user_telegram_id == existing_user.telegram_id))
        client = client.scalar_one_or_none()
        if not client:
            raise Exception('Client not found')
        location = data.get('location', {})
        latitude = location.get('latitude', None)
        longitude = location.get('longitude', None)

        new_battery = Battery(
            serial=data['serial'],
            client_id=client.id,
            latitude=latitude,
            longitude=longitude,
            confirmation_code=data['confirmation_code'],
            invoice_telegram_id=data.get('photo',None),
        )
        db.add(new_battery)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return False

    return True

async def get_battery_by_code(db: AsyncSession, code: str):
    async with db.begin():
        battery = await db.execute(select(Battery).filter(Battery.confirmation_code == code))
        battery = battery.scalar_one_or_none()
        if not battery:
            return
        return battery.to_dict()


async def connect_battery_from_code_to_seller(db: AsyncSession, code: str, seller_telegram_id: int) -> bool:
    async with db.begin():
        result = await db.execute(
            select(Seller)
            .join(UserTelegram, Seller.user_telegram_id == UserTelegram.telegram_id)
            .filter(UserTelegram.telegram_id == seller_telegram_id))
        seller = result.scalar_one_or_none()
        if not seller:
            return False
        battery = await db.scalar(select(Battery).filter_by(confirmation_code=code))
        if not battery:
            return False
        if battery.seller_id:
            return False
        battery.seller_id = seller.id
        battery.confirmation_code = None
        await db.commit()
    return True

async def add_message(db: AsyncSession, message: str, telegram_id: int):
    async with db.begin():
        try:
            existing_user = await db.execute(select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id))
            existing_user = existing_user.scalar_one_or_none()
            new_message = TelegramMessage(telegram_id=existing_user.telegram_id, message=message)
            db.add(new_message)
            await db.commit()
            result=True
        except Exception as error:
            bot_log.error(f'Error in add_message {error}')
            await db.rollback()
            result=False
        finally:
            return result
