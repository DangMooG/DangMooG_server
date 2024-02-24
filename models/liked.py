from sqlalchemy.types import TIMESTAMP
from sqlalchemy import Column, Integer, ForeignKey, text

from core.db import Base


class Liked(Base):
    __tablename__ = "liked"
    liked_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.post_id"), nullable=False)
    account_id = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    mysql_engine = "InnoDB"