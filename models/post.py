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
    account_id = Column(Integer, nullable=False)
    liked = Column(Integer)
    view_count = Column(Integer)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"