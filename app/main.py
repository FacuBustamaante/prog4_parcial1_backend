from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers import categoria_router, ingrediente_router, producto_router

@asynccontextmanager
async def lifespan(app: FastAPI):
   create_db_and_tables()
   yield

app = FastAPI(
   title="UTN - Programación IV - Parcial 1",
   description="Parcial 1 Programación IV",
   version="1.0.0",
   lifespan=lifespan
)

app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"], 
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

app.include_router(categoria_router.router)
app.include_router(ingrediente_router.router)
app.include_router(producto_router.router)

@app.get("/")
def estado_api():
   return {
      "status": "Backend Funcionando",
      "docs": "/docs"
   }