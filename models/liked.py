from sqlalchemy import Column, Integer, ForeignKey

from core.db import Base


class Liked(Base):
    __tablename__ = "liked"
    liked_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.post_id"), nullable=False)
    account_id = Column(Integer, ForeignKey("account.account_id"), nullable=False)

    mysql_engine = "InnoDB"