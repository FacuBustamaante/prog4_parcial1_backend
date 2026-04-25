from typing import TYPE_CHECKING, List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_ingrediente import ProductoIngrediente
from app.models.ingrediente import IngredienteRead

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.ingrediente import Ingrediente

class ProductoBase(SQLModel):
    nombre: str = Field(index=True, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio: float = Field(default=0.0)
    categoria_id: int = Field(foreign_key="categoria.id")

class Producto(ProductoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    categoria: "Categoria" = Relationship(back_populates="productos")
    
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos", 
        link_model=ProductoIngrediente
    )

class ProductoRead(ProductoBase):
    id: int
    ingredientes: List[IngredienteRead] = Field(default_factory=list)

class ProductoCreate(ProductoBase):
    ingredientes_ids: List[int] = []