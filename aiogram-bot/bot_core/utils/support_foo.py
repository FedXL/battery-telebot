from bot_core.create_bot import bot


async def kill_messages(message_or_callback,killing_list) -> None:
    """ в основном нужна что бы очищать с листа лишние сообщения,
     что хранятся в state_data killing list"""

    if killing_list:
        for message_id in killing_list:
            try:
                await bot.delete_message(chat_id=message_or_callback.from_user.id, message_id=message_id)
            except:
                print("message not found")
