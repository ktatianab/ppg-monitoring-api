from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import DTO.models as models, ORM.schemas as schemas
from DAO.database import get_db

router = APIRouter(
    prefix="/cities",
    tags=["Cities"]
)

# CREATE
@router.post("/", response_model=schemas.CityResponse, status_code=201)
def create_city(city: schemas.CityCreate, db: Session = Depends(get_db)):  
    
    country = db.query(models.Country).filter(
        models.Country.id_country == city.id_country
    ).first()

    if country is None:
        raise HTTPException(status_code=404, detail="País no encontrado")

    db_city = models.City(
        name=city.name,
        id_country=city.id_country
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

# READ
@router.get("/", response_model=List[schemas.CityResponse])
def get_cities(db: Session = Depends(get_db)):
    return db.query(models.City).all()

# READ ID
@router.get("/{city_id}", response_model=schemas.CityResponse)
def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(models.City).filter(
        models.City.id_city == city_id
    ).first()

    if city is None:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")

    return city

# DELETE ID
@router.delete("/{city_id}", status_code=204)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(models.City).filter(
        models.City.id_city == city_id
    ).first()

    if city is None:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")

    db.delete(city)
    db.commit()
