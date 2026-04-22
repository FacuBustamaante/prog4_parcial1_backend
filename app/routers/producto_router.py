from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Annotated
from app.database import get_session
from app.models.producto import Producto, ProductoCreate, ProductoRead
from app.models.ingrediente import Ingrediente
from app.models.producto_ingrediente import ProductoIngrediente

router = APIRouter(prefix="/productos", tags=["Productos"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=ProductoRead, status_code=201)
def crear_producto(producto_in: ProductoCreate, session: SessionDep):
    # 1. Creamos la instancia base del producto
    db_producto = Producto.model_validate(producto_in)
    
    # 2. Lógica para vincular ingredientes (Relación N:N)
    # Buscamos los ingredientes en la DB por los IDs recibidos
    if producto_in.ingredientes_ids:
        statement = select(Ingrediente).where(Ingrediente.id.in_(producto_in.ingredientes_ids))
        db_ingredientes = session.exec(statement).all()
        
        # Si no encontró todos los ingredientes, lanzamos excepción (Requisito: HTTPException) [cite: 19]
        if len(db_ingredientes) != len(producto_in.ingredientes_ids):
            raise HTTPException(status_code=400, detail="Uno o más ingredientes no existen")
            
        db_producto.ingredientes = db_ingredientes

    session.add(db_producto)
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
    statement = select(Producto).offset(offset).limit(limit)
    if nombre:
        statement = statement.where(Producto.nombre.contains(nombre))
        
    return session.exec(statement).all()

@router.put("/{producto_id}", response_model=ProductoRead)
def editar_producto(producto_id: int, producto_in: ProductoCreate, session: SessionDep):
    db_producto = session.get(Producto, producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if producto_in.ingredientes_ids:
        statement = select(Ingrediente).where(Ingrediente.id.in_(producto_in.ingredientes_ids))
        db_ingredientes = session.exec(statement).all()

        if len(db_ingredientes) != len(producto_in.ingredientes_ids):
            raise HTTPException(status_code=400, detail="Uno o más ingredientes no existen")

        db_producto.ingredientes = db_ingredientes
    else:
        db_producto.ingredientes = []

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

    tiene_relaciones = session.exec(
        select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
    ).first()
    if tiene_relaciones:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el producto porque tiene ingredientes asociados"
        )

    session.delete(db_producto)
    session.commit()