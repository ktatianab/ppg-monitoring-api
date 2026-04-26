from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

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
def get_samples(db: Session = Depends(get_db)):
    return db.query(models.PpgSample).all()

@router.get("/session/{id_session}", response_model=list[schemas.PpgSampleResponse])
def get_samples_by_session(id_session: int, db: Session = Depends(get_db)):
    return db.query(models.PpgSample).filter(
        models.PpgSample.id_session == id_session).all()

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

    # Validar que la sesión exista
    session = db.query(models.MonitoringSession).filter(
        models.MonitoringSession.id_session == data.id_session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Actualizar campos
    for key, value in data.dict().items():
        setattr(sample, key, value)

    db.commit()
    db.refresh(sample)

    return sample