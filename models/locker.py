from sqlalchemy import VARCHAR, Column, Integer, text, ForeignKey, Null
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Locker(Base):
    __tablename__ = "locker"
    locker_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    name = Column(VARCHAR(10), nullable=False)
    status = Column(Integer, default=1)
    post_id = Column(Integer, ForeignKey("post.post_id"), default=Null)
    account_id = Column(Integer, ForeignKey("account.account_id"), default=Null)
    account = relationship("Account", foreign_keys=[account_id])
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"


class LockerAuth(Base):
    __tablename__ = 'locker_auth'

    locker_auth_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, nullable=False)
    locker_id = Column(Integer, nullable=False)
    photo_url = Column(VARCHAR(2000), nullable=False, comment='could be uploaded url location')
    is_over = Column(TINYINT, default=0)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"