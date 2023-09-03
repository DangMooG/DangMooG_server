from sqlalchemy import VARCHAR, Column, Integer, text, CHAR
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(30), unique=True)
    access_token = Column(CHAR(60), nullable=False)
    refresh_token = Column(CHAR(60), nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    available = Column(TINYINT, nullable=False, default=0)
    jail_until = Column(TIMESTAMP)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

    mysql_engine = "InnoDB"