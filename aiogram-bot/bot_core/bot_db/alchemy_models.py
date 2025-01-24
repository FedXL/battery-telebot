from sqlalchemy import  Column, Integer, String, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class OnlyRelies(Base):
    __tablename__ = 'phrases_onlyreplies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, comment='Название фразы', unique=True)
    description = Column(String(255), nullable=True, comment='Описание фразы')

    kaz = Column(Text, nullable=True, comment='Фраза на казахском')
    rus = Column(Text, nullable=True, comment='Фраза на русском')

    def __repr__(self):
        return f"<Phrases(name={self.name})>"




class UserTelegram(Base):
    __tablename__ = 'bot_usertelegram'

    telegram_id = Column(BigInteger, primary_key=True, unique=True, nullable=False, comment='ID телеграмма')
    username = Column(String(255), nullable=True, comment='Имя пользователя')
    created_at = Column(DateTime, default=datetime.utcnow, comment='Дата создания')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                        comment='Дата Последнего посещения')

    def __repr__(self):
        return f"<UserTelegram(telegram_id={self.telegram_id})>"


class UserWhatsApp(Base):
    __tablename__ = 'bot_userwhatsapp'
    phone_watsapp = Column(BigInteger, primary_key=True, unique=True, nullable=False, comment='ID WhatsApp')
    username = Column(String(255), nullable=True, comment='Имя пользователя')
    created_at = Column(DateTime, default=datetime.utcnow, comment='Дата создания')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                        comment='Дата Последнего посещения')

    def __repr__(self):
        return f"<UserWhatsApp(phone_watsapp={self.phone_watsapp})>"

class Client(Base):
    __tablename__ = 'bot_client'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_watsapp_id = Column(BigInteger, ForeignKey('bot_userwhatsapp.phone_watsapp'), nullable=True)
    user_telegram_id = Column(BigInteger, ForeignKey('bot_usertelegram.telegram_id'), nullable=True)
    user_telegram = relationship('UserTelegram', backref='client_telegram')
    user_watsapp = relationship('UserWhatsApp', backref='client_watsapp')

class Seller(Base):
     __tablename__ = 'bot_seller'

     id = Column(Integer, primary_key=True, autoincrement=True)
     user_watsapp_id = Column(BigInteger, ForeignKey('bot_userwhatsapp.phone_watsapp'), nullable=True)
     user_telegram_id = Column(BigInteger, ForeignKey('bot_usertelegram.telegram_id'), nullable=True)
     user_telegram = relationship('UserTelegram', backref='seller_telegram')
     user_watsapp = relationship('UserWhatsApp', backref='seller_watsapp')

class ClientProfile(Base):
    __tablename__ = 'bot_clientprofile'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('bot_client.id'), unique=True, nullable=False)
    phone_from_telegram = Column(String(255), nullable=True, comment='Телефон из телеграма')
    first_name = Column(String(255), nullable=True, comment='Имя')
    second_name = Column(String(255), nullable=True, comment='Фамилия')
    patronymic = Column(String(255), nullable=True, comment='Отчество')
    contact_phone = Column(String(255), nullable=True, comment='Контактный телефон')
    contact_email = Column(String(255), nullable=True, comment='Контактный email')

    language = Column(String(255), nullable=True, comment='Язык')

    client = relationship('Client', backref='profile')


class SellerProfile(Base):
    __tablename__ = 'bot_sellerprofile'

    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey('bot_seller.id'),unique=True, nullable=False)
    phone_from_telegram = Column(String(255), nullable=True, comment='Телефон из телеграма')
    first_name = Column(String(255), nullable=True, comment='Имя')
    second_name = Column(String(255), nullable=True, comment='Фамилия')
    patronymic = Column(String(255), nullable=True, comment='Отчество')
    contact_phone = Column(String(255), nullable=True, comment='Контактный телефон')
    contact_email = Column(String(255), nullable=True, comment='Контактный email')

    language = Column(String(255), nullable=True, comment='Язык')

    company_address = Column(String(255), nullable=True, comment='Адрес компании')
    company_name = Column(String(255), nullable=True, comment='Название компании')

    seller = relationship('Seller', backref='profile')