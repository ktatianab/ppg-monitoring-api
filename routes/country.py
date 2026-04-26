from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/countries",
    tags=["Countries"]
)


@router.post("/", response_model=schemas.CountryResponse, status_code=201)
def create_country(country: schemas.CountryCreate, db: Session = Depends(get_db)):
    db_country = models.Country(
        name=country.name
    )
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country

@router.get("/", response_model=List[schemas.CountryResponse])
def get_countries(db: Session = Depends(get_db)):
    return db.query(models.Country).all()

@router.get("/{country_id}", response_model=schemas.CountryResponse)
def get_country(country_id: int, db: Session = Depends(get_db)):
    country = db.query(models.Country).filter(
        models.Country.id_country == country_id
    ).first()

    if country is None:
        raise HTTPException(status_code=404, detail="País no encontrado")

    return country

@router.put("/{country_id}", response_model=schemas.CountryResponse)
def update_country(country_id: int, data: schemas.CountryCreate, db: Session = Depends(get_db)):

    country = db.query(models.Country).filter(
        models.Country.id_country == country_id
    ).first()

    if country is None:
        raise HTTPException(status_code=404, detail="País no encontrado")

    # Actualizar campos
    country.name = data.name

    db.commit()
    db.refresh(country)

    return country

@router.delete("/{country_id}", status_code=204)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    country = db.query(models.Country).filter(
        models.Country.id_country == country_id
    ).first()

    if country is None:
        raise HTTPException(status_code=404, detail="País no encontrado")

    db.delete(country)
    db.commit()