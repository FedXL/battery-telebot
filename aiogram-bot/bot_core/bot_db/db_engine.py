from os import getenv
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

alchemy_driver = getenv('ALCHEMY_DRIVER')
alchemy_user = getenv('DB_USER')
alchemy_password = getenv('DB_PASSWORD')
alchemy_host = getenv('DB_HOST')
alchemy_port = getenv('DB_PORT')
alchemy_db = getenv('DB_NAME')

async_engine = create_async_engine(f"{alchemy_driver}://{alchemy_user}:{alchemy_password}@{alchemy_host}:{alchemy_port}/{alchemy_db}", echo=True)
SessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)
telegram_bot_session = SessionLocal

async def get_db():
    async with SessionLocal() as session:
        yield session