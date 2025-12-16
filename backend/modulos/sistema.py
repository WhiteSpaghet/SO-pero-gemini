import threading
import math
import random
from .taxi import Taxi
from .cliente import Cliente

class SistemaUnieTaxi:
    def __init__(self):
        self.taxis = []     # Lista de objetos Taxi
        self.clientes = []  # Lista de objetos Cliente
        self.ganancia_empresa = 0.0
        self.viajes_totales = 0
        
        # --- RECURSOS CRÍTICOS Y SINCRONIZACIÓN ---
        # Semáforo para la lista de taxis (evita asignar el mismo taxi a dos clientes)
        self.mutex_taxis = threading.Lock()
        # Semáforo para la contabilidad (evita errores de suma en las ganancias)
        self.mutex_contabilidad = threading.Lock()

    def registrar_taxi(self, modelo, placa):
        # Verificación de antecedentes (simulada)
        if random.random() < 0.1: return None
        
        nuevo_taxi = Taxi(
            id=len(self.taxis) + 1,
            modelo=modelo,
            placa=placa,
            x=random.uniform(0, 100),
            y=random.uniform(0, 100)
        )
        with self.mutex_taxis:
            self.taxis.append(nuevo_taxi)
        return nuevo_taxi

    def registrar_cliente(self, nombre, tarjeta):
        # Aquí podrías verificar la tarjeta
        nuevo_cliente = Cliente(len(self.clientes)+1, nombre, tarjeta)
        self.clientes.append(nuevo_cliente)
        return nuevo_cliente

    def procesar_solicitud(self, cliente_id, ox, oy, dx, dy):
        """Algoritmo de Match Cliente-Taxi con Sección Crítica"""
        mejor_taxi = None
        distancia_minima = float('inf')

        # -- INICIO SECCIÓN CRÍTICA --
        with self.mutex_taxis:
            for taxi in self.taxis:
                if taxi.estado == "LIBRE":
                    dist = math.sqrt((taxi.x - ox)**2 + (taxi.y - oy)**2)
                    
                    if dist <= 20: # Radio de cobertura 20 unidades
                        if dist < distancia_minima:
                            distancia_minima = dist
                            mejor_taxi = taxi
                        elif dist == distancia_minima:
                            # Desempate por calificación
                            if taxi.calificacion > mejor_taxi.calificacion:
                                mejor_taxi = taxi
            
            if mejor_taxi:
                mejor_taxi.estado = "OCUPADO"
                mejor_taxi.destino_actual = (dx, dy)
                # Teletransportamos al taxi al origen para iniciar el viaje
                mejor_taxi.x = ox
                mejor_taxi.y = oy
        # -- FIN SECCIÓN CRÍTICA --
        
        return mejor_taxi

    def finalizar_viaje(self, taxi, costo):
        """Cierre contable de un viaje individual"""
        with self.mutex_contabilidad:
            comision = costo * 0.20
            pago_taxi = costo - comision
            
            taxi.ganancias += pago_taxi
            self.ganancia_empresa += comision
            self.viajes_totales += 1
            
            # Auditoría aleatoria (Requisito: 5 servicios diarios)
            # Simplificado: auditamos cada 5 viajes
            if self.viajes_totales % 5 == 0:
                print(f"[AUDITORÍA CALIDAD] Revisando viaje del Taxi {taxi.placa}...")