from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.model.user import User
from app.schemas.user_schema import UserRegister, UserLogin, UserResponse, RoleUpdate
from app.services.user_services import create_user, login_user, list_users, update_user_role
from app.utils.security import get_current_user, require_role

router = APIRouter()


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user.email, user.password)


@router.get("/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Who am I and what role do I have (frontend uses this to hide buttons)."""
    return current_user


@router.get("/users", response_model=List[UserResponse])
def users(db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    return list_users(db)


@router.put("/users/{user_id}/role", response_model=UserResponse)
def set_role(user_id: int, payload: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    return update_user_role(db, user_id, payload.role, current_user)
