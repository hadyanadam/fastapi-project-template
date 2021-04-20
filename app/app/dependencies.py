from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from .db.session import SessionLocal
from .core.security import decode_jwt, credentials_exception, oauth2_scheme
from .schemas.user import UserRetrieve
from .crud.crud_user import crud_user


async def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_current_user(
    db: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
):
    token_data = await decode_jwt(token)
    user = crud_user.get_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_is_current_user_admin(
    current_user: UserRetrieve = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized Access"
        )
    return current_user
