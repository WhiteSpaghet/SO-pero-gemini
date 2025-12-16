import threading
import time
import math
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- CONFIGURACIÓN CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS (Pydantic) ---
class Coordenada(BaseModel):
    x: float
    y: float

class TaxiRegistro(BaseModel):
    modelo: str
    placa: str

class ClienteRegistro(BaseModel):
    nombre: str
    tarjeta: str

class SolicitudViaje(BaseModel):
    cliente_id: int
    origen_x: float
    origen_y: float
    destino_x: float
    destino_y: float

# --- CLASES DE LA SIMULACIÓN (Lógica de SO) ---

class Taxi:
    def __init__(self, id, modelo, placa, x, y):
        self.id = id
        self.modelo = modelo
        self.placa = placa
        self.x = x
        self.y = y
        self.estado = "LIBRE"  # LIBRE, OCUPADO
        self.calificacion = round(random.uniform(3.5, 5.0), 2)
        self.ganancias = 0.0
        self.destino_actual = None
        self.cliente_actual = None

class Cliente:
    def __init__(self, id, nombre, tarjeta):
        self.id = id
        self.nombre = nombre
        self.en_viaje = False

class SistemaUnieTaxi:
    def __init__(self):
        self.taxis: List[Taxi] = []
        self.clientes: List[Cliente] = []
        self.ganancia_empresa = 0.0
        self.viajes_totales = 0
        
        # --- SEMÁFOROS Y SINCRONIZACIÓN ---
        # Mutex para evitar que dos hilos modifiquen la lista de taxis a la vez
        self.mutex_taxis = threading.Lock() 
        # Mutex para proteger la contabilidad (Recurso Crítico)
        self.mutex_contabilidad = threading.Lock()

    def registrar_taxi(self, modelo, placa):
        # Simulamos verificación de antecedentes
        if random.random() < 0.1: # 10% de probabilidad de tener antecedentes
            return None
        
        nuevo_taxi = Taxi(
            id=len(self.taxis) + 1,
            modelo=modelo,
            placa=placa,
            x=random.uniform(0, 100), # Mapa de 100x100
            y=random.uniform(0, 100)
        )
        with self.mutex_taxis:
            self.taxis.append(nuevo_taxi)
        return nuevo_taxi

    def buscar_taxi_cercano(self, cx, cy):
        mejor_taxi = None
        distancia_minima = float('inf')

        # SECCIÓN CRÍTICA: Leemos la lista de taxis
        with self.mutex_taxis:
            for taxi in self.taxis:
                if taxi.estado == "LIBRE":
                    dist = math.sqrt((taxi.x - cx)**2 + (taxi.y - cy)**2)
                    
                    # Radio de 2km (asumimos 1 unidad = 100m, 2km = 20 unidades)
                    if dist <= 20: 
                        # Lógica de desempate por calificación
                        if dist < distancia_minima:
                            distancia_minima = dist
                            mejor_taxi = taxi
                        elif dist == distancia_minima:
                            if taxi.calificacion > mejor_taxi.calificacion:
                                mejor_taxi = taxi
            
            # Si encontramos uno, lo reservamos atómicamente
            if mejor_taxi:
                mejor_taxi.estado = "OCUPADO"
        
        return mejor_taxi

    def finalizar_viaje(self, taxi: Taxi, costo):
        # SECCIÓN CRÍTICA: Dinero
        with self.mutex_contabilidad:
            comision = costo * 0.20
            pago_taxi = costo - comision
            
            taxi.ganancias += pago_taxi
            self.ganancia_empresa += comision
            self.viajes_totales += 1
            
            # Check aleatorio de calidad (5 al día)
            if self.viajes_totales % 5 == 0:
                print(f"[AUDITORÍA] Revisando calidad del viaje del Taxi {taxi.id}...")

sistema = SistemaUnieTaxi()

# --- HILO DE SIMULACIÓN DE MOVIMIENTO ---
# Este hilo corre siempre en el fondo moviendo los taxis ocupados
def motor_fisica():
    while True:
        with sistema.mutex_taxis:
            for taxi in sistema.taxis:
                if taxi.estado == "OCUPADO" and taxi.destino_actual:
                    # Mover taxi hacia el destino
                    dest_x, dest_y = taxi.destino_actual
                    dx = dest_x - taxi.x
                    dy = dest_y - taxi.y
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist < 1: # Ha llegado
                        taxi.x = dest_x
                        taxi.y = dest_y
                        taxi.estado = "LIBRE"
                        taxi.destino_actual = None
                        # Calcular costo (Simulado: 10$ por unidad de distancia)
                        sistema.finalizar_viaje(taxi, costo=random.uniform(10, 50))
                    else:
                        # Avanzar un paso (velocidad)
                        step = 2 
                        taxi.x += (dx / dist) * step
                        taxi.y += (dy / dist) * step
        
        time.sleep(0.5) # Actualizar cada medio segundo

# Arrancar el hilo motor al iniciar
hilo_motor = threading.Thread(target=motor_fisica, daemon=True)
hilo_motor.start()

# --- ENDPOINTS API ---

@app.get("/estado")
def obtener_estado():
    # Retorna la foto actual del sistema para el frontend
    return {
        "taxis": sistema.taxis,
        "empresa_ganancia": round(sistema.ganancia_empresa, 2),
        "viajes": sistema.viajes_totales
    }

@app.post("/taxis")
def nuevo_taxi(datos: TaxiRegistro):
    taxi = sistema.registrar_taxi(datos.modelo, datos.placa)
    if not taxi:
        raise HTTPException(status_code=400, detail="Antecedentes penales detectados. Rechazado.")
    return taxi

@app.post("/solicitar_viaje")
def solicitar(datos: SolicitudViaje):
    # 1. Buscar taxi (usa mutex internamente)
    taxi = sistema.buscar_taxi_cercano(datos.origen_x, datos.origen_y)
    
    if not taxi:
        return {"resultado": "No hay taxis disponibles en tu zona (2km)"}
    
    # 2. Asignar viaje
    taxi.destino_actual = (datos.destino_x, datos.destino_y)
    # Teletransportamos al taxi al cliente por simplicidad visual, 
    # o podrías hacer que viaje primero al cliente y luego al destino.
    taxi.x = datos.origen_x
    taxi.y = datos.origen_y
    
    return {
        "resultado": "Taxi asignado",
        "taxi": taxi,
        "tiempo_estimado": "5 min"
    }