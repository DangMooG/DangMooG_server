from passlib.context import CryptContext
from sqlalchemy.orm import Session
from schemas.user import UserCreate
from models.post import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user_create: UserCreate):
    db_user = User(username=user_create.username,
                   password=pwd_context.hash(user_create.password1),
                   email=user_create.email,
                   is_super=user_create.is_super)
    db.add(db_user)
    db.commit()