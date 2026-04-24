from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/security-levels",
    tags=["Security Levels"]
)

@router.post("/", response_model=schemas.SeverityLevelResponse)
def create_severity(data: schemas.SeverityLevelCreate, db: Session = Depends(get_db)):
    existing = db.query(models.SeverityLeveltyLevel).filter(
        models.SeverityLevel.name == data.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Severity already exists")

    severity = models.SeverityLevel(**data.dict())

    db.add(severity)
    db.commit()
    db.refresh(severity)

    return severity

@router.get("/", response_model=list[schemas.SeverityLevelResponse])
def get_severities(db: Session = Depends(get_db)):
    return db.query(models.SeverityLevel).all()

@router.get("/{id_severity_level}", response_model=schemas.SeverityLevelResponse)
def get_severity(id_severity_level: int, db: Session = Depends(get_db)):
    severity = db.query(models.SeverityLevel).filter(
        models.SeverityLevel.id_severity_level == id_severity_level
    ).first()

    if not severity:
        raise HTTPException(status_code=404, detail="Severity not found")

    return severity

@router.put("/{id_severity_level}", response_model=schemas.SeverityLevelResponse)
def update_severity(
    id_severity_level: int,
    data: schemas.SeverityLevelCreate,
    db: Session = Depends(get_db)
):
    severity = db.query(models.SeverityLevel).filter(
        models.SeverityLevel.id_severity_level == id_severity_level
    ).first()

    if not severity:
        raise HTTPException(status_code=404, detail="Severity not found")

    severity.name = data.name
    severity.description = data.description

    db.commit()
    db.refresh(severity)

    return severity

@router.delete("/{id_severity_level}")
def delete_severity(id_severity_level: int, db: Session = Depends(get_db)):
    severity = db.query(models.SeverityLevel).filter(
        models.SeverityLevel.id_severity_level == id_severity_level
    ).first()

    if not severity:
        raise HTTPException(status_code=404, detail="Severity not found")

    db.delete(severity)
    db.commit()

    return {"detail": "Severity deleted successfully"}

