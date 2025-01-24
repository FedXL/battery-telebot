# from sqlalchemy import select
# from bot_core.bot_db.alchemy_models import UserTelegram, Client, ClientProfile, Seller, SellerProfile
# from bot_core.bot_db.db_engine import telegram_bot_session
# from bot_core.utils.callback_actions import Calls
#
#
# async def check_user(telegram_id):
#     async with telegram_bot_session() as session:
#         existing_user = await session.execute(
#             select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id)
#         )
#         existing_user = existing_user.scalar_one_or_none()
#         if not existing_user:
#             return {'teleuser': None, 'profile': None}
#         client = await check_user_profile(existing_user)
#         if not client:
#             return {'teleuser': existing_user, 'profile': None}
#         return {'teleuser': existing_user, 'profile': client}
#
#
# async def check_user_profile(telegram_user_obj: UserTelegram):
#     return telegram_user_obj.client_telegram
#
#
# async def create_profile_by_telegram_id(telegram_id,
#                                         client_or_seller: str,
#                                         rus_or_kaz: str):
#     async with telegram_bot_session() as session:
#         async with session.begin():
#             existing_user = await session.execute(
#                 select(UserTelegram).filter(UserTelegram.telegram_id == telegram_id)
#             )
#             existing_user = existing_user.scalar_one_or_none()
#             if not existing_user:
#                 raise Exception('User not found')
#             if client_or_seller == Calls.SELLER_CHOICE:
#                 client = existing_user.client_telegram
#                 if client:
#                     raise Exception('Client already exists!')
#                 new_client = Client(user_telegram_id=existing_user.telegram_id)
#                 session.add(new_client)
#                 new_profile_client = ClientProfile(client_id=new_client.id)
#                 new_profile_client.language=rus_or_kaz
#                 session.add(new_profile_client)
#             elif client_or_seller == Calls.CLIENT_CHOICE:
#                 seller = existing_user.seller_telegram
#                 if seller:
#                     raise Exception('Seller already exists!')
#                 new_seller = Seller(user_telegram_id=existing_user.telegram_id)
#                 session.add(new_seller)
#                 new_profile_seller = SellerProfile(seller_id=new_seller.id)
#                 new_profile_seller.language=rus_or_kaz
#                 session.add(new_profile_seller)
#             else:
#                 raise Exception('Unknown user type (client or seller)')
#         return True
#
#