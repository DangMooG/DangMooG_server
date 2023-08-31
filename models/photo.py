from sqlalchemy import VARCHAR, Column, Integer, text, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Photo(Base):
    __tablename__ = "photo"
    photo_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    url = Column(VARCHAR(2000), nullable=False)
    post_id = Column(Integer, ForeignKey("post.post_id"), nullable=False)
    post = relationship("Post", backref="photos")
    category_id = Column(Integer, ForeignKey("catrgory.category_id"), nullable=False)
    status = Column(TINYINT, nullable=False)
    account_id = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"