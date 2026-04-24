from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/health-records",
    tags=["Health Records"]
)

#CREATE
@router.post("/", response_model=schemas.HealthRecordResponse)
def create_health_record(data: schemas.HealthRecordCreate, db: Session = Depends(get_db)):
    
    user = db.query(models.AppUser).filter(models.AppUser.id_user == data.id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = models.HealthRecord(
        id_user=data.id_user,
        weight_kg=data.weight_kg,
        height_cm=data.height_cm
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

#READ
@router.get("/", response_model=list[schemas.HealthRecordResponse])
def get_records(db: Session = Depends(get_db)):
    return db.query(models.HealthRecord).all()

#READ by ID
@router.get("/{id_record}", response_model=schemas.HealthRecordResponse)
def get_record(id_record: int, db: Session = Depends(get_db)):
    record = db.query(models.HealthRecord).filter(
        models.HealthRecord.id_health_record == id_record
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    return record

#UPDATE
@router.put("/{id_record}", response_model=schemas.HealthRecordResponse)
def update_record(
    id_record: int,
    data: schemas.HealthRecordCreate,
    db: Session = Depends(get_db)
):
    record = db.query(models.HealthRecord).filter(
        models.HealthRecord.id_health_record == id_record
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    record.id_user = data.id_user
    record.weight_kg = data.weight_kg
    record.height_cm = data.height_cm

    db.commit()
    db.refresh(record)

    return record

#DELETE
@router.delete("/{id_record}")
def delete_record(id_record: int, db: Session = Depends(get_db)):
    record = db.query(models.HealthRecord).filter(
        models.HealthRecord.id_health_record == id_record
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()

    return {"message": "Health record deleted"}