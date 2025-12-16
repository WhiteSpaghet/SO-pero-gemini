import threading
import math
import random
from datetime import datetime, timedelta
from .taxi import Taxi
from .cliente import Cliente

class SistemaUnieTaxi:
    def __init__(self):
        self.taxis = []     
        self.clientes = []  
        self.cola_espera = []
        
        self.ganancia_empresa = 0.0
        self.viajes_totales = 0
        self.contador_id_taxi = 0 
        self.contador_id_cliente = 0
        self.clientes_viajando = set() 

        # Control de tiempo para contrataciones
        self.ultimo_refuerzo = datetime.min # Nunca se ha contratado
        
        self.tiempo_actual = datetime(2025, 12, 12, 6, 0, 0) 

        self.mutex_taxis = threading.RLock() 
        self.mutex_contabilidad = threading.RLock()

    def tick_tiempo(self):
        self.tiempo_actual += timedelta(minutes=20)

    # --- GERENTE MUY RÁPIDO (2 por segundo) ---
    def gestionar_abastecimiento(self):
        """
        Revisa la cola y contrata refuerzos RÁPIDAMENTE.
        Reglas:
        1. Solo si hay 5+ personas esperando.
        2. Límite de flota ampliado a 20.
        3. Velocidad: 2 taxis por segundo (0.5s de espera).
        """
        LIMITE_FLOTA = 20 
        TIEMPO_ENTRE_CONTRATACIONES = 0.5 # <--- 0.5s = 2 taxis por segundo
        
        ahora_real = datetime.now() 

        with self.mutex_taxis:
            # CHECK 1: Límite de flota
            if len(self.taxis) >= LIMITE_FLOTA:
                return 

            # CHECK 2: Cooldown (Ahora es solo medio segundo)
            segundos_pasados = (ahora_real - self.ultimo_refuerzo).total_seconds()
            if segundos_pasados < TIEMPO_ENTRE_CONTRATACIONES:
                return 

            # CHECK 3: Emergencia de cola
            if len(self.cola_espera) >= 5:
                print(f"[GERENCIA] ⚡ Contratación Exprés. Cola: {len(self.cola_espera)}")
                
                self.registrar_taxi("Refuerzo-Flash", f"R-{random.randint(100,999)}")
                self.ultimo_refuerzo = ahora_real

    def registrar_taxi(self, modelo, placa):
        self.contador_id_taxi += 1
        nuevo_taxi = Taxi(self.contador_id_taxi, modelo, placa, float(random.uniform(0, 100)), float(random.uniform(0, 100)))
        
        with self.mutex_taxis:
            self.taxis.append(nuevo_taxi)
            self.asignar_trabajo_de_cola(nuevo_taxi)
            
        return nuevo_taxi

    def registrar_cliente(self, nombre, tarjeta):
        self.contador_id_cliente += 1
        nuevo_cliente = Cliente(self.contador_id_cliente, nombre, tarjeta)
        self.clientes.append(nuevo_cliente)
        return nuevo_cliente

    def procesar_solicitud(self, cliente_id, ox, oy, dx, dy):
        if cliente_id <= 0: return "ID_INVALIDO"
        if cliente_id in self.clientes_viajando: return "CLIENTE_OCUPADO" 

        mejor_taxi = None
        distancia_minima = float('inf')

        with self.mutex_taxis:
            for taxi in self.taxis:
                if taxi.estado == "LIBRE":
                    dist = math.sqrt((taxi.x - float(ox))**2 + (taxi.y - float(oy))**2)
                    if dist < distancia_minima:
                        distancia_minima = dist
                        mejor_taxi = taxi
            
            if mejor_taxi:
                self._asignar_viaje(mejor_taxi, cliente_id, ox, oy, dx, dy)
                return mejor_taxi
            else:
                solicitud = {"cliente_id": cliente_id, "ox": ox, "oy": oy, "dx": dx, "dy": dy}
                self.cola_espera.append(solicitud)
                self.clientes_viajando.add(cliente_id)
                return "EN_COLA"

    def _asignar_viaje(self, taxi, cliente_id, ox, oy, dx, dy):
        taxi.estado = "OCUPADO"
        taxi.destino_actual = (float(dx), float(dy))
        taxi.x = float(ox) 
        taxi.y = float(oy)
        taxi.cliente_actual = cliente_id 
        self.clientes_viajando.add(cliente_id)

    def asignar_trabajo_de_cola(self, taxi):
        if self.cola_espera:
            siguiente = self.cola_espera.pop(0) 
            print(f"[COLA] Taxi {taxi.id} rescata al Cliente {siguiente['cliente_id']}")
            self._asignar_viaje(
                taxi, siguiente["cliente_id"], 
                siguiente["ox"], siguiente["oy"], 
                siguiente["dx"], siguiente["dy"]
            )
            return True
        return False

    def finalizar_viaje(self, taxi, costo):
        if taxi.cliente_actual:
            cliente_obj = next((c for c in self.clientes if c.id == taxi.cliente_actual), None)
            if cliente_obj: cliente_obj.viajes += 1 
            if taxi.cliente_actual in self.clientes_viajando:
                self.clientes_viajando.remove(taxi.cliente_actual)
            taxi.cliente_actual = None

        with self.mutex_contabilidad:
            comision = costo * 0.20
            pago_taxi = costo - comision
            taxi.ganancias += pago_taxi
            taxi.viajes += 1 
            self.ganancia_empresa += comision
            self.viajes_totales += 1

    def eliminar_taxi(self, taxi_id):
        with self.mutex_taxis:
            taxi_a_borrar = next((t for t in self.taxis if t.id == taxi_id), None)
            if not taxi_a_borrar: return False, "Taxi no encontrado"
            if taxi_a_borrar.estado == "OCUPADO": return False, "No se puede eliminar: Ocupado."
            self.taxis.remove(taxi_a_borrar)
            return True, "Taxi eliminado."