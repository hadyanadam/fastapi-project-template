from typing import Any, Dict, Optional, Union, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .base import CRUDBase
from ..core.security import get_password_hash, verify_password
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_id(self, db: Session, *, id: str) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_multi_exclude_admin(
        self,
        db: Session,
        *,
        limit: int,
        skip: int
    ) -> List[User]:
        return db.query(User) \
            .filter(not User.is_admin) \
            .limit(limit) \
            .skip(skip) \
            .all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        data = obj_in.dict(exclude_unset=True)
        db_obj = User(
            password=get_password_hash(data.pop('password')),
            **data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            update_data.update({"password": hashed_password})
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self,
        db: Session,
        *,
        username: str,
        password: str
    ) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='user not found'
            )
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='password incorrect'
            )
        return user


crud_user = CRUDUser(User)
