# app/crud_base.py
from typing import Any, Generic, Mapping, Sequence, Type, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """Generic CRUD operations for a SQLAlchemy model."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # --- basic reads ---

    def get(self, db: Session, id_: Any) -> ModelType | None:
        return db.get(self.model, id_)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        return (
            db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    # --- filter helpers (extra but handy) ---

    def get_by(self, db: Session, **filters: Any) -> ModelType | None:
        """First row matching simple equality filters."""
        return db.query(self.model).filter_by(**filters).first()

    def get_multi_by(self, db: Session, **filters: Any) -> list[ModelType]:
        """All rows matching simple equality filters."""
        return db.query(self.model).filter_by(**filters).all()

    # --- create ---

    def create(self, db: Session, obj_in: Mapping[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_many(
        self,
        db: Session,
        objs_in: Sequence[Mapping[str, Any]],
    ) -> list[ModelType]:
        db_objs = [self.model(**data) for data in objs_in]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return db_objs

    # --- update ---

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: Mapping[str, Any],
    ) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_many(
        self,
        db: Session,
        updates: Sequence[tuple[ModelType, Mapping[str, Any]]],
    ) -> list[ModelType]:
        for db_obj, data in updates:
            for field, value in data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
        db.commit()
        for db_obj, _ in updates:
            db.refresh(db_obj)
        return [db_obj for db_obj, _ in updates]

    # --- delete ---

    def delete(self, db: Session, id_: Any) -> None:
        obj = self.get(db, id_)
        if obj is None:
            return
        db.delete(obj)
        db.commit()

    def delete_many(self, db: Session, ids: Sequence[Any]) -> int:
        objs = (
            db.query(self.model)
            .filter(self.model.id.in_(ids))
            .all()
        )
        for obj in objs:
            db.delete(obj)
        db.commit()
        return len(objs)
