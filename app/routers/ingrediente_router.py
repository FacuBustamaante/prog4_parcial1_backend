from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List, Annotated
from app.database import get_session
from app.models.ingrediente import Ingrediente, IngredienteCreate, IngredienteRead

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=IngredienteRead, status_code=201)
def crear_ingrediente(ingrediente: IngredienteCreate, session: SessionDep):
    db_ingrediente = Ingrediente.model_validate(ingrediente)
    session.add(db_ingrediente)
    session.commit()
    session.refresh(db_ingrediente)
    return db_ingrediente

@router.get("/", response_model=List[IngredienteRead])
def leer_ingredientes(session: SessionDep):
    return session.exec(select(Ingrediente)).all()