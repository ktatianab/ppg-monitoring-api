from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import DTO.models as models
import ORM.schemas as schemas
from DAO.database import get_db
from utils.query_builder import apply_get_query_params

router = APIRouter(
    prefix="/ppg_samples",
    tags=["PpgSamples"]
)


@router.post("/", response_model=schemas.PpgSampleResponse)
def create_sample(data: schemas.PpgSampleCreate, db: Session = Depends(get_db)):

    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == data.id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sample = models.PpgSample(**data.dict())

    db.add(sample)
    db.commit()
    db.refresh(sample)

    return sample


@router.get("/", response_model=list[schemas.PpgSampleResponse])
def get_samples(
    query: Optional[str] = Query(
        default=None,
        description="Filter records. Example: id_session:1 or green__gte:60"
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
    db_query = db.query(models.PpgSample)

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.PpgSample,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/session/{id_session}", response_model=list[schemas.PpgSampleResponse])
def get_samples_by_session(
    id_session: int,
    query: Optional[str] = Query(default=None),
    limit: Optional[int] = Query(default=None, ge=1),
    offset: Optional[int] = Query(default=None, ge=0),
    orderBy: Optional[str] = Query(default=None),
    sort: Optional[str] = Query(default="asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    db_query = db.query(models.PpgSample).filter(
        models.PpgSample.id_session == id_session
    )

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.PpgSample,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.delete("/{id_sample}")
def delete_sample(id_sample: int, db: Session = Depends(get_db)):
    sample = db.query(models.PpgSample).filter(
        models.PpgSample.id_ppg_sample == id_sample
    ).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    db.delete(sample)
    db.commit()

    return {"message": "PPG sample deleted"}


@router.post("/bulk")
def create_samples_bulk(data: list[schemas.PpgSampleCreate], db: Session = Depends(get_db)):
    samples = [models.PpgSample(**item.dict()) for item in data]

    db.bulk_save_objects(samples)
    db.commit()

    return {"inserted": len(samples)}


@router.put("/{id_sample}", response_model=schemas.PpgSampleResponse)
def update_sample(id_sample: int, data: schemas.PpgSampleCreate, db: Session = Depends(get_db)):

    sample = db.query(models.PpgSample).filter(
        models.PpgSample.id_ppg_sample == id_sample
    ).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == data.id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    for key, value in data.dict().items():
        setattr(sample, key, value)

    db.commit()
    db.refresh(sample)

    return sample