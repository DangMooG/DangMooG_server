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