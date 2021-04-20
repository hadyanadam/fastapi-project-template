from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from typing import List
from sqlalchemy.orm import Session
from datetime import timedelta

from .core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
)
from .crud.crud_user import crud_user
from .core.config import settings
from .schemas.user import (
    UserRetrieve,
    UserCreate,
    UserUpdate,
)
from .schemas.token import Token
from .dependencies import (
    get_db_session,
    get_current_user,
    get_is_current_user_admin,
)

router = APIRouter(
            prefix=f'{settings.API_V1_STR}/user',
            tags=['users']
        )


@router.get('/me', response_model=UserRetrieve)
def me(
    current_user: UserRetrieve = Depends(get_current_user)
):
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud_user.authenticate(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/{id}', response_model=UserRetrieve)
def get_single_user(
    id: int,
    db: Session = Depends(get_db_session),
    current_user: UserRetrieve = Depends(get_is_current_user_admin),
):
    new_user = crud_user.get(db, id=id)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return new_user


@router.get(
    '/',
    response_model=List[UserRetrieve],
    dependencies=[Depends(get_is_current_user_admin)],
)
def get_batch_user(
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db_session),
):
    return crud_user.get_multi(db, skip=skip, limit=limit)


@router.post(
    '/',
    response_model=UserRetrieve,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_is_current_user_admin)],
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db_session),
):
    return crud_user.create(db, obj_in=user_in)


@router.delete(
    '/{id}',
    response_model=UserRetrieve,
    dependencies=[Depends(get_is_current_user_admin)],
)
def delete_user(id: int, db: Session = Depends(get_db_session)):
    return crud_user.remove(db, id=id)


@router.put(
    '/{id}',
    response_model=UserRetrieve,
    dependencies=[Depends(get_is_current_user_admin)],
)
def update_user(
    id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db_session),
):
    selected_user = crud_user.get(db, id=id)
    if not selected_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return crud_user.update(db, db_obj=selected_user, obj_in=user_in)
