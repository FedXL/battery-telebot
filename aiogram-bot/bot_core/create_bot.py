from os import getenv
from aiogram import Bot, Dispatcher, BaseMiddleware, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from dotenv import load_dotenv
from bot_core.middlware import DbSessionMiddleware

load_dotenv()
TOKEN = getenv('BOT_TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML',link_preview_show_above_text=True))
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT, debug=True)
dp.update.middleware(DbSessionMiddleware())