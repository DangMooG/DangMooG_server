from sqlalchemy import VARCHAR, Column, Integer, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Post(Base):
    __tablename__ = "post"
    post_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(255), nullable=False)
    price = Column(Integer, nullable=False)
    photo_id = Column(Integer)
    description = Column(VARCHAR(2000), nullable=False)
    category_id = Column(Integer, nullable=False)
    status = Column(TINYINT, nullable=False)
    user_id = Column(Integer, nullable=False)
    view_count = Column(Integer)
    comment_id = Column(Integer)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(30), unique=True, nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    is_super = Column(TINYINT, nullable=False)