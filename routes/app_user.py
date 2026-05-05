from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import DTO.models as models
import ORM.schemas as schemas
from DAO.database import get_db
from dependencies.auth_guard import TokenUser, get_current_user_from_token
from utils.query_builder import apply_get_query_params

router = APIRouter(
    prefix="/App_users",
    tags=["AppUsers"]
)


@router.post("/", response_model=schemas.AppUserResponse)
def create_user(*_args, **_kwargs):
    raise HTTPException(
        status_code=405,
        detail="User registration is handled by MS AUTH",
    )


@router.get("/", response_model=list[schemas.AppUserResponse])
def get_users(
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
    db_query = db.query(models.App_user).filter(
        models.App_user.id_user == current_user.user_id
    )

    db_query = apply_get_query_params(
        db_query=db_query,
        model=models.App_user,
        query=query,
        limit=limit,
        offset=offset,
        order_by=orderBy,
        sort=sort
    )

    return db_query.all()


@router.get("/{id_user}", response_model=schemas.AppUserResponse)
def get_user(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    if id_user != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(models.App_user).filter(
        models.App_user.id_user == id_user
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{id_user}", response_model=schemas.AppUserResponse)
def update_user(
    id_user: int,
    user_data: schemas.AppUserCreate,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    if id_user != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(models.App_user).filter(
        models.App_user.id_user == id_user
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    city = db.query(models.City).filter(
        models.City.id_city == user_data.id_city
    ).first()

    if city is None:
        raise HTTPException(status_code=404, detail="City not found")

    user.id_city = user_data.id_city
    user.email = user_data.email
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.birth_date = user_data.birth_date

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{id_user}")
def delete_user(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user_from_token),
):
    if id_user != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(models.App_user).filter(
        models.App_user.id_user == id_user
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
