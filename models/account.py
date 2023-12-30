from sqlalchemy import VARCHAR, Column, Integer, TEXT, text, CHAR
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(30), unique=True, nullable=False)
    password = Column(CHAR(60), nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    profile_url = Column(VARCHAR(2000))
    available = Column(TINYINT, nullable=False)
    jail_until = Column(TIMESTAMP)
    fcm = Column(TEXT)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

    mysql_engine = "InnoDB"

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "profile_url": self.profile_url,
            "available": self.available,
            "jail_until": self.jail_until,
            "refresh_token": self.refresh_token,
            "create_time": self.create_time,
            "update_time": self.update_time
        }