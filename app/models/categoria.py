from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class CategoriaBase(SQLModel):
    nombre: str = Field(index=True, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=255)

class Categoria(CategoriaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    productos: List["Producto"] = Relationship(back_populates="categoria")

class CategoriaRead(CategoriaBase):
    id: int

class CategoriaCreate(CategoriaBase):
    pass