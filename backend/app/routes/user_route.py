from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user_schema import UserRegister, UserLogin
from app.services.user_services import create_user, login_user

router = APIRouter()


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user.email, user.password)