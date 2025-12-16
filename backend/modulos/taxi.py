import math
import random

class Taxi:
    def __init__(self, id, modelo, placa, x, y):
        self.id = id
        self.modelo = modelo
        self.placa = placa
        self.x = float(x)
        self.y = float(y)
        self.estado = "LIBRE"
        self.calificacion = round(random.uniform(3.5, 5.0), 2)
        self.ganancias = 0.0
        self.destino_actual = None
        self.cliente_actual = None

    def actualizar_posicion(self, destino_x, destino_y, velocidad):
        # 1. Calculamos vector dirección
        dx = float(destino_x) - self.x
        dy = float(destino_y) - self.y
        distancia = math.sqrt(dx**2 + dy**2)
        
        # 2. Condición de llegada ESTRICTA (Aquí está el "problema")
        # Si la velocidad es 5 y la distancia es 3, el taxi saltará a la distancia -2.
        # Nunca entrará en este 'if' si salta por encima.
        if distancia < 1.0:
            self.x = destino_x
            self.y = destino_y
            return True # Ha llegado

        # 3. Movimiento SIN frenado
        # Normalizamos el vector y multiplicamos por velocidad constante
        if distancia > 0:
            vector_x = dx / distancia
            vector_y = dy / distancia
            
            self.x += vector_x * velocidad
            self.y += vector_y * velocidad
        
        return False # Sigue viajando