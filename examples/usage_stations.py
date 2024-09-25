# -*- coding: utf-8 -*-
from ClimateWeatherData import smhi


# Find stations with certain parameter
param = 'TemperaturePast24h'
param_id = smhi.get_param_value(param)
stations = smhi.list_stations(param_id)
print(stations.head())

# Find stations with certain parameter at a certain date
stations = smhi.list_stations(param_id, ts='2012-04-05')
print(stations.head())

# Select weather station
station_id = 162860
station_name = smhi.get_station_info(station_id)
print(station_name)

# Check if data available for parameter for station
if smhi.isin_station(param_id, station_id):
    print('%s (id=%d) is avalable in station %s (id=%d)' % (param, param_id, station_name, station_id))
else:
    print('%s (id=%d) is NOT avalable in station %s (id=%d)' % (param, param_id, station_name, station_id))        
