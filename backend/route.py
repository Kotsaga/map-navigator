import ctypes
import os

class DistanceCalculator:
    def __init__(self):
        # Определяем путь к библиотеке
        base_path = os.path.dirname(os.path.dirname(__file__))  # путь к корню проекта
        lib_path = os.path.join(base_path, 'cpp', 'routes.dll')  # путь к c++
        
        # Загружаем библиотеку
        self.lib = ctypes.CDLL(lib_path)
        
        # Настраиваем типы аргументов
        self.lib.calculate_trip.argtypes = [
            ctypes.c_double,  # lat1
            ctypes.c_double,  # lon1
            ctypes.c_double,  # lat2
            ctypes.c_double,  # lon2
            ctypes.c_double,  # avg_speed_kmh
            ctypes.c_double,  # fuel_consumption
            ctypes.c_double,  # fuel_price
            ctypes.POINTER(ctypes.c_double),  # distance
            ctypes.POINTER(ctypes.c_double),  # time_hours
            ctypes.POINTER(ctypes.c_double),  # fuel_liters
            ctypes.POINTER(ctypes.c_double)   # cost_rub
        ]
        self.lib.calculate_trip.restype = None  # тип возвращаемого значения
    
    def calculate_trip(self, lat1, lon1, lat2, lon2, 
                       avg_speed_kmh=80,      # по умолчанию 80 км/ч
                       fuel_consumption=8.0,  # по умолчанию 8 л/100км
                       fuel_price=55.0):      # по умолчанию 55 руб/л
        """
        Рассчитывает параметры поездки
        """
        # Создаём переменные для результатов
        distance = ctypes.c_double()
        time_hours = ctypes.c_double()
        fuel_liters = ctypes.c_double()
        cost_rub = ctypes.c_double()
        
        # Вызываем C++ функцию
        self.lib.calculate_trip(
            ctypes.c_double(lat1),
            ctypes.c_double(lon1),
            ctypes.c_double(lat2),
            ctypes.c_double(lon2),
            ctypes.c_double(avg_speed_kmh),
            ctypes.c_double(fuel_consumption),
            ctypes.c_double(fuel_price),
            ctypes.byref(distance),
            ctypes.byref(time_hours),
            ctypes.byref(fuel_liters),
            ctypes.byref(cost_rub)
        )
        
        # Форматируем время в часы и минуты
        hours = int(time_hours.value)
        minutes = int((time_hours.value - hours) * 60)
        time_str = f"{hours} ч {minutes} мин" if hours > 0 else f"{minutes} мин"
        
        return {
            "distance_km": round(distance.value, 1),
            "time_hours": round(time_hours.value, 1),
            "time_str": time_str,
            "fuel_liters": round(fuel_liters.value, 1),
            "cost_rub": round(cost_rub.value, 0)
        }

# Создаём глобальный экземпляр
trip_calc = DistanceCalculator()
