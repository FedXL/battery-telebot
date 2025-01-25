import logging
from os import getenv
from aiogram import Bot, Dispatcher, BaseMiddleware, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from dotenv import load_dotenv
from bot_core.middlware import DbSessionMiddleware

load_dotenv()
TOKEN = getenv('BOT_TOKEN')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
bot_log = logging.getLogger('my_bot_logger')

# Ensure the logger outputs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)



bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML',link_preview_show_above_text=True))
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT, debug=True)
dp.update.middleware(DbSessionMiddleware())