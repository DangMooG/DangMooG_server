from sqlalchemy import VARCHAR, Column, Integer, text, ForeignKey, Null
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base
from models.chat import Chat


class Photo(Base):
    __tablename__ = "photo"
    photo_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    url = Column(VARCHAR(2000), nullable=False)
    post_id = Column(Integer, ForeignKey("post.post_id"), nullable=False)
    post = relationship("Post", backref="photos")
    category_id = Column(Integer, ForeignKey("category.category_id"), default=Null)
    category = relationship("Category", backref="photos")
    account_id = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    mysql_engine = "InnoDB"


class ChatPhoto(Base):
    __tablename__ = "chatphoto"
    chatphoto_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    url = Column(VARCHAR(2000), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat.chat_id"), nullable=False)
    chat = relationship("Chat", backref="chats")
    account_id = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    mysql_engine = "InnoDB"