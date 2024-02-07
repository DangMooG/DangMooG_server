from sqlalchemy import VARCHAR, Column, Integer, TEXT, text, CHAR
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, TIMESTAMP
from cryptography.fernet import Fernet

from core.db import Base
import os

key = os.environ["AES_KEY"]
key.encode('utf-8')
cipher_suite = Fernet(key)


class EncryptedColumn(TypeDecorator):
    """
    양방향 암호화된 컬럼을 나타내는 타입 데코레이터
    """
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = cipher_suite.encrypt(value.encode('utf-8'))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = cipher_suite.decrypt(value).decode('utf-8')
        return value


class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(30), unique=True, nullable=False)
    password = Column(CHAR(60), nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    gm = Column(TINYINT, default=1)
    profile_url = Column(VARCHAR(2000))
    available = Column(TINYINT, nullable=False, default=2)
    jail_until = Column(TIMESTAMP)
    fcm = Column(TEXT)
    bank_info = Column(EncryptedColumn(25))
    account_number = Column(EncryptedColumn(255))
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    name_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    mysql_engine = "InnoDB"

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "gm": self.gm,
            "profile_url": self.profile_url,
            "available": self.available,
            "jail_until": self.jail_until,
            "fcm": self.fcm,
            "bank_info": self.bank_info,
            "account_number": self.account_number,
            "create_time": self.create_time,
            "update_time": self.update_time
        }


class Blame(Base):
    __tablename__ = "blame"
    blame_id = Column(Integer, primary_key=True)
    blame_user = Column(TINYINT, default=0)
    blamed_id = Column(Integer, nullable=False)
    content = Column(TEXT, nullable=False)
    blamer_id = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    mysql_engine = "InnoDB"
