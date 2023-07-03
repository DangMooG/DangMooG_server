from ..core.crud import CRUD
from ..core.db import SessionLocal


def get_crud():
    db = SessionLocal()
    try:
        yield CRUD(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
