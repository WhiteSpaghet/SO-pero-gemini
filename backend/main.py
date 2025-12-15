# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# 1. Configuración de CORS
# Esto es vital para que el Frontend (puerto 5173) pueda hablar con el Backend (puerto 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # La URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Modelos de Datos (Define qué estructura tienen tus datos)
class Tarea(BaseModel):
    id: int | None = None
    titulo: str
    completada: bool = False

# 3. Base de datos simulada (una lista en memoria)
base_de_datos = [
    {"id": 1, "titulo": "Aprender FastAPI", "completada": True},
    {"id": 2, "titulo": "Conectar con React", "completada": False}
]

# 4. Endpoints (Rutas)

@app.get("/")
def home():
    return {"mensaje": "API funcionando correctamente"}

@app.get("/tareas", response_model=List[Tarea])
def obtener_tareas():
    return base_de_datos

@app.post("/tareas", response_model=Tarea)
def crear_tarea(tarea: Tarea):
    # Generamos un ID simple
    nuevo_id = len(base_de_datos) + 1
    nueva_tarea = tarea.dict()
    nueva_tarea["id"] = nuevo_id
    
    base_de_datos.append(nueva_tarea)
    return nueva_tarea