from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/Measurements",
    tags=["Measurements"]
)




@router.post("/", response_model=schemas.MeasurementResponse)
def create_measurement(data: schemas.MeasurementCreate, db: Session = Depends(get_db)):
    metric_type = db.query(models.MetricType).filter(
        models.MetricType.id_metric_type == data.id_metric_type
    ).first()

    if not metric_type:
        raise HTTPException(status_code=404, detail="Metric type not found")

    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == data.id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Monitoring session not found")

    measurement = models.Measurementurement(**data.dict())

    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    return measurement


@router.get("/", response_model=list[schemas.MeasurementResponse])
def get_measurements(db: Session = Depends(get_db)):
    return db.query(models.Measurement).all()


@router.get("/{id_measurement}", response_model=schemas.MeasurementResponse)
def get_measurement(id_measurement: int, db: Session = Depends(get_db)):
    measurement = db.query(models.Measurementurement).filter(
        models.Measurement.id_measurement == id_measurement
    ).first()

    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    return measurement


@router.get("/session/{id_session}", response_model=list[schemas.MeasurementResponse])
def get_measurements_by_session(id_session: int, db: Session = Depends(get_db)):
    return db.query(models.Measurement).filter(
        models.Measurement.id_session == id_session
    ).all()


@router.put("/{id_measurement}", response_model=schemas.MeasurementResponse)
def update_measurement(
    id_measurement: int,
    data: schemas.MeasurementCreate,
    db: Session = Depends(get_db)
):
    measurement = db.query(models.Measurementurement).filter(
        models.Measurement.id_measurement == id_measurement
    ).first()

    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    measurement.id_metric_type = data.id_metric_type
    measurement.id_session = data.id_session
    measurement.value = data.value
    measurement.error_message = data.error_message

    db.commit()
    db.refresh(measurement)

    return measurement


@router.delete("/{id_measurement}")
def delete_measurement(id_measurement: int, db: Session = Depends(get_db)):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id_measurement == id_measurement
    ).first()

    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    db.delete(measurement)
    db.commit()

    return {"message": "Measurement deleted"}
