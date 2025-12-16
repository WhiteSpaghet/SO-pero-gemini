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

    def actualizar_posicion(self, destino_x, destino_y, velocidad=2):
        try:
            # 1. Convertimos a float por seguridad
            tx, ty = float(self.x), float(self.y)
            dx, dy = float(destino_x), float(destino_y)

            # 2. Calculamos distancia total restante
            cateto_x = dx - tx
            cateto_y = dy - ty
            distancia_total = (cateto_x**2 + cateto_y**2)**0.5

            # 3. SI YA LLEGAMOS (Distancia casi cero):
            if distancia_total < 0.5: 
                self.x = dx
                self.y = dy
                return True # ¡Llegó!

            # 4. MOVIMIENTO SUAVE (Interpolación Lineal)
            # Calculamos qué porcentaje del camino podemos recorrer en este paso.
            # Si velocidad > distancia, el ratio es 1.0 (el 100% del camino, llegar directo).
            # Si no, es una fracción (ej. 0.1 para avanzar un 10%).
            
            avance = min(velocidad, distancia_total) # Nunca avanzamos más de lo que falta
            ratio = avance / distancia_total

            # Aplicamos el movimiento
            self.x = tx + (cateto_x * ratio)
            self.y = ty + (cateto_y * ratio)

            # Si el ratio fue 1.0 (o muy cerca), es que hemos llegado
            return ratio >= 1.0

        except Exception as e:
            print(f"Error Math Taxi {self.id}: {e}")
            return True # En caso de error, forzamos llegada para no bloquear