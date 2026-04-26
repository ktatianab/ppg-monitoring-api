from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db
 
router = APIRouter( 
    prefix="/monitoring_sessions",
    tags=["MonitoringSessions"]
)

@router.post("/", response_model=schemas.MonitoringSessionResponse)
def create_monitoring_session(
    data: schemas.MonitoringSessionCreate,
    db: Session = Depends(get_db)
):
    user = db.query(models.App_user).filter(models.App_user.id_user == data.id_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = models.MonitoringSession(**data.dict())

    db.add(session)
    db.commit()
    db.refresh(session)

    return session

@router.get("/", response_model=list[schemas.MonitoringSessionResponse])
def get_monitoring_sessions(db: Session = Depends(get_db)):
    return db.query(models.MonitoringSession).all()

@router.get("/{id_session}", response_model=schemas.MonitoringSessionResponse)
def get_monitoring_session(id_session: int, db: Session = Depends(get_db)):
    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Monitoring session not found")

    return session

@router.get("/user/{id_user}", response_model=list[schemas.MonitoringSessionResponse])
def get_monitoring_sessions_by_user(
    id_user: int,
    db: Session = Depends(get_db)
):
    return db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_user == id_user
    ).all()

@router.put("/{id_session}", response_model=schemas.MonitoringSessionResponse)
def update_monitoring_session(
    id_session: int,
    data: schemas.MonitoringSessionCreate,
    db: Session = Depends(get_db)
):
    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Monitoring session not found")

    session.id_user = data.id_user
    session.id_compute_status = data.id_compute_status
    session.date_time = data.date_time
    session.is_delta_encoded = data.is_delta_encoded

    db.commit()
    db.refresh(session)

    return session

@router.delete("/{id_session}")
def delete_monitoring_session(id_session: int, db: Session = Depends(get_db)):
    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Monitoring session not found")

    db.delete(session)
    db.commit()

    return {"message": "Monitoring session deleted"}