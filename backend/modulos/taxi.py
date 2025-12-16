import math
import random

class Taxi:
    def __init__(self, id, modelo, placa, x, y):
        self.id = id
        self.modelo = modelo
        self.placa = placa
        self.x = float(x) # Aseguramos que sea número
        self.y = float(y)
        self.estado = "LIBRE"
        self.calificacion = round(random.uniform(3.5, 5.0), 2)
        self.ganancias = 0.0
        self.destino_actual = None
        self.cliente_actual = None

    def actualizar_posicion(self, destino_x, destino_y, velocidad=2):
        """
        Mueve el taxi de forma segura. 
        Retorna True si llegó, False si sigue moviéndose.
        """
        try:
            # Aseguramos que tratamos con floats
            dx = float(destino_x) - self.x
            dy = float(destino_y) - self.y
            distancia = math.sqrt(dx**2 + dy**2)
            
            # 1. Si la distancia es ridículamente pequeña, ya llegamos.
            # (Evita división por cero)
            if distancia < 0.01:
                self.x = destino_x
                self.y = destino_y
                return True

            # 2. Lógica anti-vibración:
            # Si estoy más cerca que la velocidad de mi paso, salto al final.
            if distancia <= velocidad:
                self.x = destino_x
                self.y = destino_y
                return True
            
            # 3. Movimiento normal (Vector unitario)
            factor = velocidad / distancia
            self.x += dx * factor
            self.y += dy * factor
            
            return False

        except Exception as e:
            print(f"[ERROR MATEMÁTICO EN TAXI {self.id}]: {e}")
            # En caso de error, forzamos la llegada para no bloquear
            return True