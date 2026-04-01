//ФУНКЦИОНАЛЬНЫЙ МОДУЛЬ

#include <cmath>

const double R = 6371.0; // Радиус Земли

//Функция перевода градусов в радианы
double toRadians(double degrees) 
    {return degrees * M_PI / 180.0;}

// расчёт расстояния по прямой
double calculate_distance (double lat1,double lon1,double lat2,double lon2)
    {
        //переводим в радианы
        double lat1_rad = toRadians(lat1);
        double lon1_rad = toRadians(lon1);
        double lat2_rad = toRadians(lat2);
        double lon2_rad = toRadians(lon2);

        double dlat = lat2_rad - lat1_rad; //разница широт
        double dlon = lon2_rad - lon1_rad;   //разница долготы

        //формула Гаверсинуса
        double a = sin(dlat/2) * sin(dlat/2) +
           cos(lat1_rad) * cos(lat2_rad) *
           sin(dlon/2) * sin(dlon/2);

        //вычисление центрального угла
        double c = 2 * atan2(sqrt(a), sqrt(1-a));

        //возвращаем расстояние
        return R*c;
    } 

extern "C"    //чтобы можно было вызвать из python
{
    void calculate_trip(
        double lat1, double lon1, double lat2, double lon2,
        double avg_speed_kmh,      // средняя скорость 
        double fuel_consumption,   // расход топлива 
        double fuel_price,         // цена топлива 
        double* distance,          // расстояние 
        double* time_hours,        // время 
        double* fuel_liters,       // топливо 
        double* cost_rub           // стоимость 
    ) 
    {
        // Расчёт расстояния
        *distance = calculate_distance(lat1, lon1, lat2, lon2);
        
        // Расчёт времени (часы)
        *time_hours = *distance / avg_speed_kmh;
        
        // Расчёт топлива (литры)
        *fuel_liters = (*distance / 100.0) * fuel_consumption;
        
        // Расчёт стоимости (рубли)
        *cost_rub = *fuel_liters * fuel_price;
    }
}
