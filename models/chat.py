from sqlalchemy import VARCHAR, Column, Integer, text, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Chat(Base):
    __tablename__ = "chat"
    chat_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    post_id = Column(Integer, nullable=False)
    room_id = Column(Integer, nullable=False)
    is_seller = Column(TINYINT, nullable=False)
    account_id = Column(Integer, nullable=False)
    chat_str = Column(String)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"