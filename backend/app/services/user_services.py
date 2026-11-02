from fastapi import HTTPException
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

    
    # The very first account becomes Admin so someone can manage roles;
    # everyone after that starts as Viewer until an Admin promotes them.
    first_user = db.query(User).count() == 0

    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        role="Admin" if first_user else "Viewer",
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


def list_users(db: Session):
    return db.query(User).order_by(User.id).all()


def update_user_role(db: Session, user_id: int, role: str, acting_user: User):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == acting_user.id and role != user.role:
        raise HTTPException(status_code=400, detail="You cannot change your own role")
    user.role = role
    db.commit()
    db.refresh(user)
    return user
