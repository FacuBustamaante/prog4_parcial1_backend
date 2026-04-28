from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.categoria import Categoria, CategoriaCreate, CategoriaRead
from app.models.producto import Producto
from typing import Annotated

router = APIRouter(prefix="/categorias", tags=["Categorías"])

@router.post("/", response_model=CategoriaRead, status_code=201)
def crear_categoria(categoria: CategoriaCreate, session: Session = Depends(get_session)):
   db_categoria = Categoria.model_validate(categoria)
   session.add(db_categoria)
   session.commit()
   session.refresh(db_categoria)
   return db_categoria

@router.get("/", response_model=list[CategoriaRead])
def leer_categorias(session: Annotated[Session, Depends(get_session)]):
   return session.exec(select(Categoria)).all()

@router.put("/{categoria_id}", response_model=CategoriaRead)
def editar_categoria(
   categoria_id: int,
   categoria_in: CategoriaCreate,
   session: Session = Depends(get_session)
):
   db_categoria = session.get(Categoria, categoria_id)
   if not db_categoria:
      raise HTTPException(status_code=404, detail="Categoría no encontrada")

   db_categoria.sqlmodel_update(categoria_in.model_dump())
   session.add(db_categoria)
   session.commit()
   session.refresh(db_categoria)
   return db_categoria

@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(categoria_id: int, session: Session = Depends(get_session)):
   db_categoria = session.get(Categoria, categoria_id)
   if not db_categoria:
      raise HTTPException(status_code=404, detail="Categoría no encontrada")

   tiene_productos = session.exec(
      select(Producto).where(Producto.categoria_id == categoria_id)
   ).first()
   if tiene_productos:
      raise HTTPException(
            status_code=409,
            detail="No se puede eliminar la categoría porque tiene productos asociados"
      )

   session.delete(db_categoria)
   session.commit()