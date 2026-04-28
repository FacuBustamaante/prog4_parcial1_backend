from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Annotated
from app.database import get_session
from app.models.ingrediente import Ingrediente, IngredienteCreate, IngredienteRead
from app.models.producto_ingrediente import ProductoIngrediente

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

@router.put("/{ingrediente_id}", response_model=IngredienteRead)
def editar_ingrediente(ingrediente_id: int, ingrediente_in: IngredienteCreate, session: SessionDep):
   db_ingrediente = session.get(Ingrediente, ingrediente_id)
   if not db_ingrediente:
      raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

   db_ingrediente.sqlmodel_update(ingrediente_in.model_dump())
   session.add(db_ingrediente)
   session.commit()
   session.refresh(db_ingrediente)
   return db_ingrediente

@router.delete("/{ingrediente_id}", status_code=204)
def eliminar_ingrediente(ingrediente_id: int, session: SessionDep):
   db_ingrediente = session.get(Ingrediente, ingrediente_id)
   if not db_ingrediente:
      raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

   en_uso = session.exec(
      select(ProductoIngrediente).where(ProductoIngrediente.ingrediente_id == ingrediente_id)
   ).first()
   if en_uso:
      raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el ingrediente porque está asociado a productos"
      )

   session.delete(db_ingrediente)
   session.commit()