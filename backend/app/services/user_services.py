from sqlalchemy.orm import Session

from app.model.user import User
from app.schemas.user_schema import UserRegister
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def create_user(db: Session, user: UserRegister):


    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return {
            "message": "Email already registered"
        }

    
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        role="Viewer",
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Registered Successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        }
    }


def login_user(db: Session, email: str, password: str):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {
            "message": "User not found"
        }

    if not verify_password(password, user.password_hash):
        return {
            "message": "Invalid Password"
        }

    token = create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }