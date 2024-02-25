import math

from pydantic import BaseModel
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from typing import Union, List


class CRUD:
    def __init__(self, session: Session) -> None:
        self.session = session
        # self.query = self.session.query(table)

    def get_list(self, table: BaseModel):
        return self.session.query(table).all()

    def get_record(self, table: BaseModel, cond={}):
        filters = []
        for table_id, id in cond.items():
            filters.append(getattr(table, table_id) == id)
        return self.session.query(table).filter(*filters).order_by(table.create_time.desc()).first()

    def create_record(self, table: BaseModel, req: BaseModel):
        db_record = table(**req.dict())
        self.session.add(db_record)
        self.session.commit()
        self.session.refresh(db_record)
        return db_record

    def update_record(self, db_record: BaseModel, req: Union[BaseModel, dict]):
        if isinstance(req, BaseModel):
            req = req.dict()
        for key, value in req.items():
            setattr(db_record, key, value)
        self.session.commit()

        return db_record

    def patch_record(self, db_record: BaseModel, req: Union[BaseModel, dict]):
        if isinstance(req, BaseModel):
            req = req.dict()
        for key, value in req.items():
            if value:
                setattr(db_record, key, value)
            if value == 0:
                setattr(db_record, key, value)
            if value is None:
                setattr(db_record, key, value)
        self.session.commit()

        return db_record

    def patch_all(self, db_records: List[BaseModel], req: Union[BaseModel, dict]):
        if isinstance(req, BaseModel):
            req = req.dict()
        for db_record in db_records:
            for key, value in req.items():
                if value:
                    setattr(db_record, key, value)
                if value == 0:
                    setattr(db_record, key, value)
        self.session.commit()

        return db_records

    def delete_record(self, table: BaseModel, cond={}):
        db_record = self.get_record(table, cond)
        if db_record:
            self.session.delete(db_record)
            self.session.commit()
            return 1
        else:
            return -1

    def paging_record(self, table: BaseModel, req: BaseModel):
        total_row = self.session.query(table).count()
        if total_row % req.size == 0:
            total_page = math.floor(total_row / req.size)
        else:
            total_page = math.floor(total_row / req.size) + 1
        start = (req.page - 1) * req.size

        items = self.session.query(table).order_by(table.create_time.desc()).offset(start).limit(req.size).all()
        pages = {"items": items, "total_pages": total_page, "page": req.page, "size": req.size, "total_row": total_row}
        return pages

    def app_paging_record(self, table: BaseModel, size: int, checkpoint: int = 0):
        status_order = case(
            (table.status == 2, 1),
            else_=0
        )

        query = self.session.query(table).filter(table.use_locker != 1, table.account_id != 91)
        total_row = query.count()
        if checkpoint == 0:
            start = checkpoint
            items = query.order_by(status_order, table.create_time.desc()).offset(start).limit(size).all()
            return {"items": items, "next_checkpoint": total_row - size}
        else:
            start = total_row - checkpoint
            items = query.order_by(status_order, table.create_time.desc()).offset(start).limit(size).all()
            next_checkpoint = checkpoint - size
            if next_checkpoint < 1:
                next_checkpoint = -1
            return {"items": items, "next_checkpoint": next_checkpoint}

    def house_paging_record(self, table: BaseModel, size: int, checkpoint: int = 0):
        query = self.session.query(table).filter(table.use_locker != 1, table.account_id == 91)
        total_row = query.count()
        if checkpoint == 0:
            start = checkpoint
            items = query.order_by(table.create_time.desc(), table.post_id.desc()).offset(start).limit(size).all()
            return {"items": items, "next_checkpoint": total_row - size}
        else:
            start = total_row - checkpoint
            items = query.order_by(table.create_time.desc(), table.post_id.desc()).offset(start).limit(size).all()
            next_checkpoint = checkpoint - size
            if next_checkpoint < 1:
                next_checkpoint = -1
            return {"items": items, "next_checkpoint": next_checkpoint}

    def house_category_record(self, table: BaseModel, category: int, size: int, checkpoint: int = 0):
        query = self.session.query(table).filter(table.use_locker != 1, table.account_id == 91, table.category_id == category)
        total_row = query.count()
        if checkpoint == 0:
            start = checkpoint
            items = query.order_by(table.create_time.desc(), table.post_id.desc()).offset(start).limit(size).all()
            return {"items": items, "next_checkpoint": total_row - size}
        else:
            start = total_row - checkpoint
            items = query.order_by(table.create_time.desc(), table.post_id.desc()).offset(start).limit(size).all()
            next_checkpoint = checkpoint - size
            if next_checkpoint < 1:
                next_checkpoint = -1
            return {"items": items, "next_checkpoint": next_checkpoint}

    def search_record(self, table: BaseModel, req: Union[BaseModel, dict]):
        if isinstance(req, BaseModel):
            req = req.dict()
        filters = []
        for key, value in req.items():
            if value == 0 or value:
                if isinstance(value, (int, float)):
                    filters.append(getattr(table, key) == value)
                elif isinstance(value, str):
                    filters.append(getattr(table, key).contains(value))
                elif isinstance(value, list):
                    filters.append(func.json_contains(getattr(table, key), str(value)) == 1)

        result = self.session.query(table).filter(*filters).all()
        return result
