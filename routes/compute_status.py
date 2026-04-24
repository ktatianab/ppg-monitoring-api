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