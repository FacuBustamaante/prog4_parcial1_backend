from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Annotated
from app.database import get_session
from app.models.categoria import Categoria, CategoriaCreate, CategoriaRead

router = APIRouter(prefix="/categorias", tags=["Categorías"])

# Inyección de dependencia de sesión con Annotated
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=CategoriaRead, status_code=201)
def crear_categoria(categoria: CategoriaCreate, session: SessionDep):
    db_categoria = Categoria.model_validate(categoria)
    session.add(db_categoria)
    session.commit()
    session.refresh(db_categoria)
    return db_categoria

@router.get("/", response_model=List[CategoriaRead])
def leer_categorias(session: SessionDep):
    return session.exec(select(Categoria)).all()