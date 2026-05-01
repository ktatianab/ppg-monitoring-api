from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import DTO.models as models
import ORM.schemas as schemas
from DAO.database import get_db
from utils.query_builder import apply_get_query_params

router = APIRouter(
    prefix="/health-records",
    tags=["Health Records"]
)


@router.post("/", response_model=schemas.HealthRecordResponse)
def create_health_record(data: schemas.HealthRecordCreate, db: Session = Depends(get_db)):
    
    user = db.query(models.App_user).filter(
        models.App_user.id_user == data.id_user
    ).first()

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


@router.get("/", response_model=list[schemas.HealthRecordResponse])
def get_records(
    query: Optional[str] = Query(
        default=None,
        description="Filter records.<miembro>:<valor>"
    ),
    limit: Optional[int] = Query(
        default=None,
        ge=1,
        description="Maximum number of records to return"
    ),
    offset: Optional[int] = Query(
        default=None,
        ge=0,
        description="Number of records to skip"
    ),
    orderBy: Optional[str] = Query(
        default=None,
        description="Field used to order the results"
    ),
    sort: Optional[str] = Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort direction: asc or desc"
    ),
    db: Session = Depends(get_db)
):
    db_query = db.query(models.HealthRecord)

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.HealthRecord,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/{id_record}", response_model=schemas.HealthRecordResponse)
def get_record(id_record: int, db: Session = Depends(get_db)):
    record = db.query(models.HealthRecord).filter(
        models.HealthRecord.id_health_record == id_record
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    return record


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
