from typing import Optional
from sqlmodel import SQLModel, Field

class ProductoIngrediente(SQLModel, table=True):
   producto_id: Optional[int] = Field(
      default=None, foreign_key="producto.id", primary_key=True
   )
   ingrediente_id: Optional[int] = Field(
      default=None, foreign_key="ingrediente.id", primary_key=True
   )