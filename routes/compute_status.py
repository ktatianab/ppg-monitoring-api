from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/compute_statuses",
    tags=["ComputeStatuses"]
)

@router.post("/", response_model=schemas.ComputeStatusResponse)
def create_status(data: schemas.ComputeStatusCreate, db: Session = Depends(get_db)):
    status = models.ComputeStatus(**data.dict())

    db.add(status)
    db.commit()
    db.refresh(status)

    return status

@router.get("/", response_model=list[schemas.ComputeStatusResponse])
def get_statuses(db: Session = Depends(get_db)):
    return db.query(models.ComputeStatus).all()

@router.put("/{id_compute_status}", response_model=schemas.ComputeStatusResponse)
def update_status(id_compute_status: int, data: schemas.ComputeStatusCreate, db: Session = Depends(get_db)):
    
    status = db.query(models.ComputeStatus).filter(
        models.ComputeStatus.id_compute_status == id_compute_status
    ).first()

    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    # Actualizar campos dinámicamente
    for key, value in data.dict().items():
        setattr(status, key, value)

    db.commit()
    db.refresh(status)

    return status

@router.delete("/{id_status}")
def delete_status(id_status: int, db: Session = Depends(get_db)):
    
    status = db.query(models.ComputeStatus).filter(
        models.ComputeStatus.id_compute_status == id_status
    ).first()

    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    db.delete(status)
    db.commit()

    return {"message": "Status deleted"}