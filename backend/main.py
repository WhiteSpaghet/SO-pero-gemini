import threading
import time
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
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
# AJUSTADO: 0.3s por defecto (x10 más rápido)
INTERVALO_GENERACION = 0.3 

# --- HILO 1: MOTOR FÍSICO (x10 VELOCIDAD) ---
def motor_fisica():
    while True:
        try:
            sistema.tick_tiempo() 

            with sistema.mutex_taxis:
                taxis_activos = [t for t in sistema.taxis if t.estado == "OCUPADO" and t.destino_actual]
            
            velocidad = 8.0 if SIMULACION_ACTIVA else 2.0

            for taxi in taxis_activos:
                dest_x, dest_y = taxi.destino_actual
                try:
                    llegado = taxi.actualizar_posicion(dest_x, dest_y, velocidad)
                    if llegado:
                        with sistema.mutex_taxis:
                            taxi.estado = "LIBRE"
                            taxi.destino_actual = None
                        sistema.finalizar_viaje(taxi, random.uniform(10, 50))
                except Exception as e:
                    print(f"Error taxi {taxi.id}: {e}")
        
        except Exception as e:
            print(f"Error motor: {e}")
        
        # CAMBIO CLAVE: 0.05s en lugar de 0.5s
        time.sleep(0.05) 

hilo_motor = threading.Thread(target=motor_fisica, daemon=True)
hilo_motor.start()

# --- HILO 2: SIMULADOR DE CLIENTES ---
def simulador_clientes():
    while True:
        if SIMULACION_ACTIVA:
            cliente_id_seleccionado = None
            clientes_libres = [c for c in sistema.clientes if c.id not in sistema.clientes_viajando]
            usar_existente = False
            
            if len(clientes_libres) == 0:
                usar_existente = False
            elif random.random() < 0.7:
                usar_existente = True
            else:
                usar_existente = False

            if usar_existente:
                cliente = random.choice(clientes_libres)
                cliente_id_seleccionado = cliente.id
            else:
                nuevo = sistema.registrar_cliente(f"Bot_{random.randint(1000,9999)}", "VISA")
                cliente_id_seleccionado = nuevo.id

            sistema.procesar_solicitud(
                cliente_id_seleccionado,
                random.uniform(0, 100), random.uniform(0, 100),
                random.uniform(0, 100), random.uniform(0, 100)
            )
            
            time.sleep(INTERVALO_GENERACION) 
        else:
            time.sleep(0.1) # Idle check más rápido también

hilo_simulacion = threading.Thread(target=simulador_clientes, daemon=True)
hilo_simulacion.start()

# --- ENDPOINTS (Igual que antes) ---
class TaxiRegistro(BaseModel):
    modelo: str
    placa: str

class SolicitudViaje(BaseModel):
    cliente_id: int
    origen_x: float
    origen_y: float
    destino_x: float
    destino_y: float

class ConfigSimulacion(BaseModel):
    activa: Optional[bool] = None
    intervalo: Optional[float] = None

@app.get("/estado")
def ver_estado():
    mejor_taxi = None
    if sistema.taxis:
        mejor_taxi_obj = max(sistema.taxis, key=lambda t: t.ganancias)
        if mejor_taxi_obj.ganancias > 0:
            mejor_taxi = {"id": mejor_taxi_obj.id, "modelo": mejor_taxi_obj.modelo, "ganancias": round(mejor_taxi_obj.ganancias, 2)}
    
    return {
        "taxis": sistema.taxis,
        "clientes": sistema.clientes, 
        "empresa_ganancia": round(sistema.ganancia_empresa, 2),
        "viajes": sistema.viajes_totales,
        "mejor_taxi": mejor_taxi,
        "simulacion_activa": SIMULACION_ACTIVA,
        "intervalo_generacion": INTERVALO_GENERACION,
        "tiempo_simulado": sistema.tiempo_actual.strftime("%d/%m/%Y %H:%M")
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

@app.post("/simulacion/config")
def configurar_simulacion(config: ConfigSimulacion):
    global SIMULACION_ACTIVA, INTERVALO_GENERACION
    if config.activa is not None: SIMULACION_ACTIVA = config.activa
    if config.intervalo is not None: INTERVALO_GENERACION = max(0.05, config.intervalo) # Permitimos valores bajos
    return {"mensaje": "Configuración actualizada", "activa": SIMULACION_ACTIVA, "intervalo": INTERVALO_GENERACION}