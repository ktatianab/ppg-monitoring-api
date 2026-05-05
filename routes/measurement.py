from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import DTO.models as models
import ORM.schemas as schemas
from DAO.database import get_db
from dependencies.auth_guard import TokenUser, get_current_user_from_token
from utils.query_builder import apply_get_query_params

router = APIRouter(
    prefix="/Measurements",
    tags=["Measurements"]
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
        raise HTTPException(status_code=404, detail="Monitoring session not found")

    if session.id_user != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return session


def _ensure_measurement_owner(
    measurement: models.Measurement,
    current_user: TokenUser,
):
    if measurement.session.id_user != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/", response_model=schemas.MeasurementResponse)
def create_measurement(
    data: schemas.MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    metric_type = db.query(models.MetricType).filter(
        models.MetricType.id_metric_type == data.id_metric_type
    ).first()

    if not metric_type:
        raise HTTPException(status_code=404, detail="Metric type not found")

    _get_owned_session(db, data.id_session, current_user)

    measurement = models.Measurement(**data.dict())

    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    return measurement


@router.get("/", response_model=list[schemas.MeasurementResponse])
def get_measurements(
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
    db_query = db.query(models.Measurement).join(models.Measurement.session).filter(
        models.MonitoringSession.id_user == current_user.user_id
    )

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.Measurement,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/{id_measurement}", response_model=schemas.MeasurementResponse)
def get_measurement(
    id_measurement: int,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id_measurement == id_measurement
    ).first()

    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    _ensure_measurement_owner(measurement, current_user)

    return measurement


@router.get("/session/{id_session}", response_model=list[schemas.MeasurementResponse])
def get_measurements_by_session(
    id_session: int,
    query: Optional[str] = Query(
        default=None,
        description="Filter records. Example: value__gte:60"
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

    db_query = db.query(models.Measurement).filter(
        models.Measurement.id_session == id_session
    )

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.Measurement,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.put("/{id_measurement}", response_model=schemas.MeasurementResponse)
def update_measurement(
    id_measurement: int,
    data: schemas.MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id_measurement == id_measurement
    ).first()

    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    _ensure_measurement_owner(measurement, current_user)

    _get_owned_session(db, data.id_session, current_user)

    metric_type = db.query(models.MetricType).filter(
        models.MetricType.id_metric_type == data.id_metric_type
    ).first()

    if not metric_type:
        raise HTTPException(status_code=404, detail="Metric type not found")

    measurement.id_metric_type = data.id_metric_type
    measurement.id_session = data.id_session
    measurement.value = data.value
    measurement.error_message = data.error_message

    db.commit()
    db.refresh(measurement)

    return measurement


@router.delete("/{id_measurement}")
def delete_measurement(
    id_measurement: int,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id_measurement == id_measurement
    ).first()

    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    _ensure_measurement_owner(measurement, current_user)

    db.delete(measurement)
    db.commit()

    return {"message": "Measurement deleted"}
