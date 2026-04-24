from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/App_users",
    tags=["AppUsers"]
)

@router.post("/", response_model=schemas.AppUserResponse)
def create_user(user: schemas.AppUserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.App_user).filter(models.App_user.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.App_user(
        id_city=user.id_city,
        email=user.email,
        password_hash=user.password,  # idealmente aquí va el hash
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/", response_model=list[schemas.AppUserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.App_user).all()


@router.get("/{id_user}", response_model=schemas.AppUserResponse)
def get_user(id_user: int, db: Session = Depends(get_db)):
    user = db.query(models.App_user).filter(models.App_user.id_user == id_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{id_user}", response_model=schemas.AppUserResponse)
def update_user(
    id_user: int,
    user_data: schemas.AppUserCreate,
    db: Session = Depends(get_db)
):
    user = db.query(models.App_user).filter(models.App_user.id_user == id_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.id_city = user_data.id_city
    user.email = user_data.email
    user.password_hash = user_data.password
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.birth_date = user_data.birth_date

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{id_user}")
def delete_user(id_user: int, db: Session = Depends(get_db)):
    user = db.query(models.App_user).filter(models.App_user.id_user == id_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}