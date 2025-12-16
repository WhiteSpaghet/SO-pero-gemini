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

# --- ESTADO DE SIMULACIÓN ---
SIMULACION_ACTIVA = False

# --- HILO 1: MOTOR FÍSICO (Mueve los taxis) ---
def motor_fisica():
    while True:
        # Bloqueamos la lista el menor tiempo posible
        with sistema.mutex_taxis:
            taxis_activos = [t for t in sistema.taxis if t.estado == "OCUPADO" and t.destino_actual]

        # Procesamos fuera del bloqueo principal o iteramos con cuidado
        for taxi in taxis_activos:
            try:
                dest_x, dest_y = taxi.destino_actual
                
                # Velocidad variable según simulación
                velocidad = 5 if SIMULACION_ACTIVA else 2 
                
                # Movemos el taxi
                llegado = taxi.actualizar_posicion(dest_x, dest_y, velocidad)
                
                if llegado:
                    # Necesitamos volver a bloquear para modificar estado compartido de forma segura
                    with sistema.mutex_taxis:
                        taxi.estado = "LIBRE"
                        taxi.destino_actual = None
                    
                    # Pagamos (esto ya usa su propio mutex interno)
                    costo_viaje = random.uniform(10, 50)
                    sistema.finalizar_viaje(taxi, costo_viaje)
                        
            except Exception as e:
                print(f"[ERROR CRÍTICO EN MOTOR FÍSICO - Taxi {taxi.id}]: {e}")
                # Si un taxi da error, lo reseteamos para que no congele la simulación
                with sistema.mutex_taxis:
                    taxi.estado = "LIBRE"
                    taxi.destino_actual = None
        
        time.sleep(0.5)

# --- HILO 2: GENERADOR AUTOMÁTICO DE CLIENTES (Modo Simulación) ---
def simulador_clientes():
    while True:
        if SIMULACION_ACTIVA:
            # 1. Crear un cliente ficticio (ID automático)
            nuevo_cliente = sistema.registrar_cliente(f"Bot_{random.randint(100,999)}", "VISA")
            
            # 2. Solicitar viaje aleatorio
            sistema.procesar_solicitud(
                cliente_id=nuevo_cliente.id,
                ox=random.uniform(0, 100), oy=random.uniform(0, 100),
                dx=random.uniform(0, 100), dy=random.uniform(0, 100)
            )
            print(f"[SIMULACIÓN] Cliente Bot #{nuevo_cliente.id} ha solicitado un viaje.")
            
            # Espera aleatoria entre 1 y 3 segundos para el siguiente cliente
            time.sleep(random.uniform(1, 3))
        else:
            time.sleep(1) # Si está apagado, solo comprobamos cada segundo

hilo_simulacion = threading.Thread(target=simulador_clientes, daemon=True)
hilo_simulacion.start()

# --- DTOs ---
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

# --- RUTAS API ---

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
        "simulacion_activa": SIMULACION_ACTIVA # Enviamos el estado al frontend
    }

@app.post("/taxis")
def crear_taxi(datos: TaxiRegistro):
    taxi = sistema.registrar_taxi(datos.modelo, datos.placa)
    if not taxi: raise HTTPException(status_code=400, detail="Rechazado por antecedentes")
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
    if res == "CLIENTE_OCUPADO": return {"resultado": f"Error: Cliente {datos.cliente_id} ocupado."}
    if res == "SIN_TAXIS": return {"resultado": "No hay taxis disponibles."}
    return {"resultado": "Taxi asignado", "taxi_id": res.id, "modelo": res.modelo}

# --- RUTAS NUEVAS PARA SIMULACIÓN ---
@app.post("/simulacion/toggle")
def toggle_simulacion(estado: EstadoSimulacion):
    global SIMULACION_ACTIVA
    SIMULACION_ACTIVA = estado.activa
    return {"mensaje": f"Simulación {'ACTIVADA' if SIMULACION_ACTIVA else 'DETENIDA'}"}