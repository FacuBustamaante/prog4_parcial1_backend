from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Any, Annotated, List, cast
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models.producto import Producto, ProductoCreate, ProductoRead
from app.models.ingrediente import Ingrediente
from app.models.producto_ingrediente import ProductoIngrediente

router = APIRouter(prefix="/productos", tags=["Productos"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=ProductoRead, status_code=201)
def crear_producto(producto_in: ProductoCreate, session: SessionDep):
   producto_data = producto_in.model_dump(exclude={"ingredientes_ids"})
   db_producto = Producto.model_validate(producto_data)
   session.add(db_producto)
   session.flush()

   if producto_in.ingredientes_ids:
      ingrediente_id_col = cast(Any, Ingrediente.id)
      statement = select(Ingrediente).where(ingrediente_id_col.in_(producto_in.ingredientes_ids))
      db_ingredientes = session.exec(statement).all()

      if len(db_ingredientes) != len(producto_in.ingredientes_ids):
            raise HTTPException(status_code=400, detail="Uno o más ingredientes no existen")

      session.add_all(
            [
               ProductoIngrediente(
                  producto_id=db_producto.id,
                  ingrediente_id=ingrediente.id,
               )
               for ingrediente in db_ingredientes
            ]
      )

   session.commit()
   session.refresh(db_producto)
   return db_producto

@router.get("/", response_model=List[ProductoRead])
def leer_productos(
   session: SessionDep,
   offset: int = 0,
   limit: Annotated[int, Query(le=100, description="Máximo 100 registros")] = 20,
   nombre: Annotated[str | None, Query(min_length=3)] = None
):
   ingredientes_relacion = cast(Any, Producto.ingredientes)
   nombre_col = cast(Any, Producto.nombre)

   statement = select(Producto).options(selectinload(ingredientes_relacion)).offset(offset).limit(limit)
   if nombre:
      statement = statement.where(nombre_col.contains(nombre))
      
   return session.exec(statement).all()

@router.put("/{producto_id}", response_model=ProductoRead)
def editar_producto(producto_id: int, producto_in: ProductoCreate, session: SessionDep):
   db_producto = session.get(Producto, producto_id)
   if not db_producto:
      raise HTTPException(status_code=404, detail="Producto no encontrado")

   relaciones_existentes = session.exec(
      select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
   ).all()
   for relacion in relaciones_existentes:
      session.delete(relacion)

   if producto_in.ingredientes_ids:
      ingrediente_id_col = cast(Any, Ingrediente.id)
      statement = select(Ingrediente).where(ingrediente_id_col.in_(producto_in.ingredientes_ids))
      db_ingredientes = session.exec(statement).all()

      if len(db_ingredientes) != len(producto_in.ingredientes_ids):
            raise HTTPException(status_code=400, detail="Uno o más ingredientes no existen")

      session.add_all(
            [
               ProductoIngrediente(
                  producto_id=db_producto.id,
                  ingrediente_id=ingrediente.id,
               )
               for ingrediente in db_ingredientes
            ]
      )

   producto_data = producto_in.model_dump(exclude={"ingredientes_ids"})
   db_producto.sqlmodel_update(producto_data)

   session.add(db_producto)
   session.commit()
   session.refresh(db_producto)
   return db_producto

@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, session: SessionDep):
   db_producto = session.get(Producto, producto_id)
   if not db_producto:
      raise HTTPException(status_code=404, detail="Producto no encontrado")

   relaciones = session.exec(
      select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
   ).all()
   for relacion in relaciones:
      session.delete(relacion)

   session.delete(db_producto)
   session.commit()