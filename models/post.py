from sqlalchemy import VARCHAR, Column, Integer, text, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Post(Base):
    __tablename__ = "post"
    post_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(255), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(VARCHAR(2000), nullable=False)
    representative_photo_id = Column(Integer)
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False)
    status = Column(TINYINT, nullable=False)
    account_id = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    account = relationship("Account", backref="posts")  # 해당 이용자의 다른 게시글 참고 가능
    liked = Column(Integer, default=0)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"