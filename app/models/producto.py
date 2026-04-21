from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_ingrediente import ProductoIngrediente

class ProductoBase(SQLModel):
    nombre: str = Field(index=True, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio: float = Field(default=0.0)
    categoria_id: int = Field(foreign_key="categoria.id")

class Producto(ProductoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relación 1:N [cite: 16, 68]
    categoria: "Categoria" = Relationship(back_populates="productos")
    
    # Relación N:N [cite: 16, 68]
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos", 
        link_model=ProductoIngrediente
    )

class ProductoRead(ProductoBase):
    id: int

# AQUÍ ESTÁ LA CORRECCIÓN:
class ProductoCreate(ProductoBase):
    # Este campo permite recibir los IDs desde el Frontend [cite: 27, 83]
    ingredientes_ids: List[int] = []