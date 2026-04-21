from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_ingrediente import ProductoIngrediente

class IngredienteBase(SQLModel):
    nombre: str = Field(index=True, max_length=50)
    unidad_medida: str = Field(max_length=20)

class Ingrediente(IngredienteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    productos: List["Producto"] = Relationship(
        back_populates="ingredientes", 
        link_model=ProductoIngrediente
    )

class IngredienteRead(IngredienteBase):
    id: int

class IngredienteCreate(IngredienteBase):
    pass