from sqlalchemy.orm import Session
from ..crud.crud_user import crud_user
from ..schemas.user import UserCreate
from ..core.config import settings
from . import base  # noqa: F401


def init_db(db: Session) -> None:
    user = crud_user.get_by_username(db=db, username=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            username=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_admin=True,
        )
        crud_user.create(db, obj_in=user_in)
