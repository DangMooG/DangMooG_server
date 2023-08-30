from sqlalchemy import VARCHAR, Column, Integer, text
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from core.db import Base


class Category(Base):
    __tablename__ = "category"
    category_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    category_name = Column(VARCHAR(255), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    mysql_engine = "InnoDB"