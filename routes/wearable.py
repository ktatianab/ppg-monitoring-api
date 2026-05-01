from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import DTO.models as models
import ORM.schemas as schemas
from DAO.database import get_db
from utils.query_builder import apply_get_query_params

router = APIRouter(
    prefix="/wearables",
    tags=["Wearables"]
)


@router.post("/", response_model=schemas.WearableResponse)
def create_wearable(data: schemas.WearableCreate, db: Session = Depends(get_db)):

    user = db.query(models.App_user).filter(
        models.App_user.id_user == data.id_user
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    model = db.query(models.WearableModel).filter(
        models.WearableModel.id_wearable_model == data.id_wearable_model
    ).first()
    if not model:
        raise HTTPException(status_code=404, detail="Wearable model not found")

    wearable = models.Wearable(**data.dict())

    db.add(wearable)
    db.commit()
    db.refresh(wearable)

    return wearable


@router.get("/", response_model=list[schemas.WearableResponse])
def get_wearables(
    query: Optional[str] = Query(
        default=None,
        description="Filter records. Example: id_user:1 or id_wearable_model:2"
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
    db_query = db.query(models.Wearable)

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.Wearable,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/user/{id_user}", response_model=list[schemas.WearableResponse])
def get_user_wearables(
    id_user: int,
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
    db_query = db.query(models.Wearable).filter(
        models.Wearable.id_user == id_user
    )

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.Wearable,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/{id_wearable}", response_model=schemas.WearableResponse)
def get_wearable(id_wearable: int, db: Session = Depends(get_db)):
    wearable = db.query(models.Wearable).filter(
        models.Wearable.id_wearable == id_wearable
    ).first()

    if not wearable:
        raise HTTPException(status_code=404, detail="Wearable not found")

    return wearable


@router.put("/{id_wearable}", response_model=schemas.WearableResponse)
def update_wearable(
    id_wearable: int,
    data: schemas.WearableCreate,
    db: Session = Depends(get_db)
):
    wearable = db.query(models.Wearable).filter(
        models.Wearable.id_wearable == id_wearable
    ).first()

    if not wearable:
        raise HTTPException(status_code=404, detail="Wearable not found")

    user = db.query(models.App_user).filter(
        models.App_user.id_user == data.id_user
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    model = db.query(models.WearableModel).filter(
        models.WearableModel.id_wearable_model == data.id_wearable_model
    ).first()
    if not model:
        raise HTTPException(status_code=404, detail="Wearable model not found")

    for key, value in data.dict().items():
        setattr(wearable, key, value)

    db.commit()
    db.refresh(wearable)

    return wearable


@router.delete("/{id_wearable}")
def delete_wearable(id_wearable: int, db: Session = Depends(get_db)):
    wearable = db.query(models.Wearable).filter(
        models.Wearable.id_wearable == id_wearable
    ).first()

    if not wearable:
        raise HTTPException(status_code=404, detail="Wearable not found")

    db.delete(wearable)
    db.commit()

    return {"message": "Wearable deleted"}