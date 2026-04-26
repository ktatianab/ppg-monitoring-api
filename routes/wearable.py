from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/wearables",
    tags=["Wearables"]
)

@router.post("/", response_model=schemas.WearableResponse)
def create_wearable(data: schemas.WearableCreate, db: Session = Depends(get_db)):

    user = db.query(models.App_user).filter(models.App_user.id_user == data.id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    model = db.query(models.WearableModel).filter(
        models.WearableModel.id_wearable_model == data.id_wearable_model
    ).first()
    if not model:
        raise HTTPException(status_code=404, detail="Wearable model not found")

    wearable = models.Wearable(**data.dict())

    db.add(wearable)
    db.commit()
    db.refresh(wearable)

    return wearable

@router.get("/", response_model=list[schemas.WearableResponse])
def get_wearables(db: Session = Depends(get_db)):
    return db.query(models.Wearable).all()

@router.get("/{id_wearable}", response_model=schemas.WearableResponse)
def get_wearable(id_wearable: int, db: Session = Depends(get_db)):
    wearable = db.query(models.Wearable).filter(
        models.Wearable.id_wearable == id_wearable
    ).first()

    if not wearable:
        raise HTTPException(status_code=404, detail="Wearable not found")

    return wearable

@router.get("/user/{id_user}", response_model=list[schemas.WearableResponse])
def get_user_wearables(id_user: int, db: Session = Depends(get_db)):
    return db.query(models.Wearable).filter(
        models.Wearable.id_user == id_user
    ).all()

@router.delete("/{id_wearable}")
def delete_wearable(id_wearable: int, db: Session = Depends(get_db)):
    wearable = db.query(models.Wearable).filter(
        models.Wearable.id_wearable == id_wearable
    ).first()

    if not wearable:
        raise HTTPException(status_code=404, detail="Wearable not found")

    db.delete(wearable)
    db.commit()

    return {"message": "Wearable deleted"}

