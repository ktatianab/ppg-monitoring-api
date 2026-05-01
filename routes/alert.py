from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import DTO.models as models
import ORM.schemas as schemas
from DAO.database import get_db
from utils.query_builder import apply_get_query_params

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
def get_alerts(
    query: Optional[str] = Query(
        default=None,
        description="Filter records. <miembro>:<valor>"
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
    db_query = db.query(models.Alert)

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.Alert,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/session/{id_session}", response_model=list[schemas.AlertResponse])
def get_alerts_by_session(
    id_session: int,
    query: Optional[str] = Query(
        default=None,
        description="Filter records. Example: id_severity_level:2"
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
    db_query = db.query(models.Alert).filter(
        models.Alert.id_session == id_session
    )

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.Alert,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/{id_alert}", response_model=schemas.AlertResponse)
def get_alert(id_alert: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(
        models.Alert.id_alert == id_alert
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.put("/{id_alert}", response_model=schemas.AlertResponse)
def update_alert(id_alert: int, data: schemas.AlertCreate, db: Session = Depends(get_db)):
    
    alert = db.query(models.Alert).filter(
        models.Alert.id_alert == id_alert
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

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

    for key, value in data.dict().items():
        setattr(alert, key, value)

    db.commit()
    db.refresh(alert)

    return alert


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