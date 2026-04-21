from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Annotated
from app.database import get_session
from app.models.producto import Producto, ProductoCreate, ProductoRead
from app.models.ingrediente import Ingrediente

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