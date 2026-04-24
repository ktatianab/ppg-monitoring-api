from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)

@router.post("/", response_model=schemas.AlertResponse)
def create_alert(data: schemas.AlertCreate, db: Session = Depends(get_db)):

    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == data.id_session
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    severity = db.query(models.SeverityLevel).filter(
        models.SeverityLevel.id_severity_level == data.id_severity_level
    ).first()
    if not severity:
        raise HTTPException(status_code=404, detail="Severity level not found")

    alert = models.Alert(**data.dict())

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert

@router.get("/", response_model=list[schemas.AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).all() 

@router.get("/{id_alert}", response_model=schemas.AlertResponse)
def get_alert(id_alert: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(
        models.Alert.id_alert == id_alert
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.get("/session/{id_session}", response_model=list[schemas.AlertResponse])
def get_alerts_by_session(id_session: int, db: Session = Depends(get_db)):
    return db.query(models.Alert).filter(
        models.Alert.id_session == id_session
    ).all()

@router.delete("/{id_alert}")
def delete_alert(id_alert: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(
        models.Alert.id_alert == id_alert
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()

    return {"message": "Alert deleted"}