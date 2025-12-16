import threading
import time
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from modulos.sistema import SistemaUnieTaxi

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sistema = SistemaUnieTaxi()
SIMULACION_ACTIVA = False

# --- HILO MOTOR FISICO (Versión Básica) ---
def motor_fisica():
    while True:
        try:
            with sistema.mutex_taxis:
                # Buscamos taxis con trabajo
                taxis_activos = [t for t in sistema.taxis if t.estado == "OCUPADO" and t.destino_actual]
            
            # Velocidad alta para provocar el fallo visual
            velocidad = 5.0 if SIMULACION_ACTIVA else 2.0

            for taxi in taxis_activos:
                dest_x, dest_y = taxi.destino_actual
                
                # Movemos
                llegado = taxi.actualizar_posicion(dest_x, dest_y, velocidad)
                
                if llegado:
                    with sistema.mutex_taxis:
                        taxi.estado = "LIBRE"
                        taxi.destino_actual = None
                    sistema.finalizar_viaje(taxi, random.uniform(10, 50))
        
        except Exception as e:
            print(f"Error motor: {e}")
        
        time.sleep(0.5) # Ritmo de actualización

hilo_motor = threading.Thread(target=motor_fisica, daemon=True)
hilo_motor.start()

# --- HILO SIMULADOR (Genera clientes) ---
def simulador_clientes():
    while True:
        if SIMULACION_ACTIVA:
            nuevo_cliente = sistema.registrar_cliente(f"Bot_{random.randint(100,999)}", "VISA")
            sistema.procesar_solicitud(
                nuevo_cliente.id,
                random.uniform(0, 100), random.uniform(0, 100),
                random.uniform(0, 100), random.uniform(0, 100)
            )
            time.sleep(random.uniform(1, 3))
        else:
            time.sleep(1)

hilo_simulacion = threading.Thread(target=simulador_clientes, daemon=True)
hilo_simulacion.start()

# --- ENDPOINTS RESTO DEL ARCHIVO (Mantén tus endpoints igual) ---
class TaxiRegistro(BaseModel):
    modelo: str
    placa: str

class SolicitudViaje(BaseModel):
    cliente_id: int
    origen_x: float
    origen_y: float
    destino_x: float
    destino_y: float

class EstadoSimulacion(BaseModel):
    activa: bool

@app.get("/estado")
def ver_estado():
    mejor_taxi = None
    if sistema.taxis:
        mejor_taxi_obj = max(sistema.taxis, key=lambda t: t.ganancias)
        if mejor_taxi_obj.ganancias > 0:
            mejor_taxi = {"id": mejor_taxi_obj.id, "modelo": mejor_taxi_obj.modelo, "ganancias": round(mejor_taxi_obj.ganancias, 2)}
    return {
        "taxis": sistema.taxis,
        "empresa_ganancia": round(sistema.ganancia_empresa, 2),
        "viajes": sistema.viajes_totales,
        "mejor_taxi": mejor_taxi,
        "simulacion_activa": SIMULACION_ACTIVA
    }

@app.post("/taxis")
def crear_taxi(datos: TaxiRegistro):
    taxi = sistema.registrar_taxi(datos.modelo, datos.placa)
    if not taxi: raise HTTPException(status_code=400, detail="Rechazado")
    return taxi

@app.delete("/taxis/{taxi_id}")
def borrar_taxi(taxi_id: int):
    exito, mensaje = sistema.eliminar_taxi(taxi_id)
    if not exito: raise HTTPException(status_code=400, detail=mensaje)
    return {"mensaje": mensaje}

@app.post("/solicitar_viaje")
def solicitar(datos: SolicitudViaje):
    res = sistema.procesar_solicitud(datos.cliente_id, datos.origen_x, datos.origen_y, datos.destino_x, datos.destino_y)
    if res == "ID_INVALIDO": return {"resultado": "Error: ID inválido."}
    if res == "CLIENTE_OCUPADO": return {"resultado": "Cliente ocupado."}
    if res == "SIN_TAXIS": return {"resultado": "No hay taxis."}
    return {"resultado": "Asignado", "taxi_id": res.id}

@app.post("/simulacion/toggle")
def toggle_simulacion(estado: EstadoSimulacion):
    global SIMULACION_ACTIVA
    SIMULACION_ACTIVA = estado.activa
    return {"mensaje": "OK"}