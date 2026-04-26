from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/wearable-models",
    tags=["Wearable Models"]
)

@router.post("/", response_model=schemas.WearableModelResponse)
def create_model(data: schemas.WearableModelCreate, db: Session = Depends(get_db)):
    model = models.WearableModel(**data.dict())

    db.add(model)
    db.commit()
    db.refresh(model)

    return model

@router.get("/", response_model=list[schemas.WearableModelResponse])
def get_models(db: Session = Depends(get_db)):
    return db.query(models.WearableModel).all()

@router.get("/{model_id}", response_model=schemas.WearableModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(models.WearableModel).filter(
        models.WearableModel.id_wearable_model == model_id
    ).first()

    if model is None:
        raise HTTPException(status_code=404, detail="Modelo de wearable no encontrado")

    return model

@router.put("/{model_id}", response_model=schemas.WearableModelResponse)
def update_model(model_id: int, data: schemas.WearableModelCreate, db: Session = Depends(get_db)):

    model = db.query(models.WearableModel).filter(
        models.WearableModel.id_wearable_model == model_id
    ).first()

    if model is None:
        raise HTTPException(status_code=404, detail="Modelo de wearable no encontrado")

    # Actualizar campos dinámicamente
    for key, value in data.dict().items():
        setattr(model, key, value)

    db.commit()
    db.refresh(model)

    return model

@router.delete("/{model_id}", status_code=204)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(models.WearableModel).filter(
        models.WearableModel.id_wearable_model == model_id
    ).first()

    if model is None:
        raise HTTPException(status_code=404, detail="Modelo de wearable no encontrado")

    db.delete(model)
    db.commit()