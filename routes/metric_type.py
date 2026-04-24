from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/metric-types",
    tags=["Metric Types"]
)

@router.post("/", response_model=schemas.MetricTypeResponse)
def create_metric_type(data: schemas.MetricTypeCreate, db: Session = Depends(get_db)):
    existing_metric = db.query(models.MetricType).filter(
        models.MetricType.name == data.name
    ).first()

    if existing_metric:
        raise HTTPException(status_code=400, detail="Metric type already exists")

    metric_type = models.MetricType(**data.dict())

    db.add(metric_type)
    db.commit()
    db.refresh(metric_type)

    return metric_type


@router.get("/", response_model=list[schemas.MetricTypeResponse])
def get_metric_types(db: Session = Depends(get_db)):
    return db.query(models.MetricType).all()


@router.get("/{id_metric_type}", response_model=schemas.MetricTypeResponse)
def get_metric_type(id_metric_type: int, db: Session = Depends(get_db)):
    metric_type = db.query(models.MetricType).filter(
        models.MetricType.id_metric_type == id_metric_type
    ).first()

    if not metric_type:
        raise HTTPException(status_code=404, detail="Metric type not found")

    return metric_type


@router.put("/{id_metric_type}", response_model=schemas.MetricTypeResponse)
def update_metric_type(
    id_metric_type: int,
    data: schemas.MetricTypeCreate,
    db: Session = Depends(get_db)
):
    metric_type = db.query(models.MetricType).filter(
        models.MetricType.id_metric_type == id_metric_type
    ).first()

    if not metric_type:
        raise HTTPException(status_code=404, detail="Metric type not found")

    metric_type.unit = data.unit
    metric_type.min_value = data.min_value
    metric_type.max_value = data.max_value
    metric_type.is_derived = data.is_derived
    metric_type.name = data.name

    db.commit()
    db.refresh(metric_type)

    return metric_type


@router.delete("/{id_metric_type}")
def delete_metric_type(id_metric_type: int, db: Session = Depends(get_db)):
    metric_type = db.query(models.MetricType).filter(
        models.MetricType.id_metric_type == id_metric_type
    ).first()

    if not metric_type:
        raise HTTPException(status_code=404, detail="Metric type not found")

    db.delete(metric_type)
    db.commit()

    return {"message": "Metric type deleted"}