import os
from typing import cast
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Cargamos las variables del archivo .env
load_dotenv()

# Obtenemos la URL y usamos 'cast' para asegurar que sea tratada como string
DATABASE_URL = cast(str, os.getenv("DATABASE_URL"))

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no encontrada en el archivo .env")

# Creamos el motor de conexión [cite: 21, 70]
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    # Importaciones locales para evitar ciclos 
    from app.models.categoria import Categoria
    from app.models.producto import Producto
    from app.models.ingrediente import Ingrediente
    from app.models.producto_ingrediente import ProductoIngrediente
    
    # Crea las tablas en PostgreSQL [cite: 21, 68]
    SQLModel.metadata.create_all(engine)