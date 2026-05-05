from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import DTO.models as models
import ORM.schemas as schemas
from DAO.database import get_db
from dependencies.auth_guard import TokenUser, get_current_user_from_token
from utils.query_builder import apply_get_query_params

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


def _get_owned_session(
    db: Session,
    id_session: int,
    current_user: TokenUser,
) -> models.MonitoringSession:
    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.id_user != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return session


def _ensure_alert_owner(alert: models.Alert, current_user: TokenUser):
    if alert.session.id_user != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/", response_model=schemas.AlertResponse)
def create_alert(
    data: schemas.AlertCreate,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):

    _get_owned_session(db, data.id_session, current_user)

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
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    db_query = db.query(models.Alert).join(models.Alert.session).filter(
        models.MonitoringSession.id_user == current_user.user_id
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
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    _get_owned_session(db, id_session, current_user)

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
def get_alert(
    id_alert: int,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    alert = db.query(models.Alert).filter(
        models.Alert.id_alert == id_alert
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    _ensure_alert_owner(alert, current_user)

    return alert


@router.put("/{id_alert}", response_model=schemas.AlertResponse)
def update_alert(
    id_alert: int,
    data: schemas.AlertCreate,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    
    alert = db.query(models.Alert).filter(
        models.Alert.id_alert == id_alert
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    _ensure_alert_owner(alert, current_user)
    _get_owned_session(db, data.id_session, current_user)

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
def delete_alert(
    id_alert: int,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    alert = db.query(models.Alert).filter(
        models.Alert.id_alert == id_alert
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    _ensure_alert_owner(alert, current_user)

    db.delete(alert)
    db.commit()

    return {"message": "Alert deleted"}
