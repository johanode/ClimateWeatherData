# -*- coding: utf-8 -*-
from ClimateWeatherData import smhi, climate


# Find stations with certain parameter
param = 'TemperaturePast24h'
stations = smhi.list_stations(param)
print(stations.head())

# Find stations with certain parameter at a certain date
stations = smhi.list_stations(param, ts='2012-04-05')
print(stations.head())

# Find stations with certain parameter at a certain date interval
stations = smhi.list_stations(param, ts=('2000-01-01','2024-06-30'), full_period=True)
print(stations.head())


# List stations where temperature climate data is available at a certain date
valid_stations = climate.list_stations('temperature', ts=('2000-01-01','2024-06-03'), full_period=True)


# Select weather station
station_id = 162860
station_name = smhi.get_station_info(station_id)
print(station_name)

# Check if data available for parameter for station
param_id = smhi.get_param_value(param)
if smhi.isin_station(param, station_id):
    print('%s (id=%d) is avalable in station %s (id=%d)' % (param, param_id, station_name, station_id))
else:
    print('%s (id=%d) is NOT avalable in station %s (id=%d)' % (param, param_id, station_name, station_id))   


# Closest weather station to a point (lat, lon), TemperaturePast24h will be used as default parameter
latlon = (65.640928, 22.026005)
station = smhi.closest_station(latlon)
print(f"Closets station to ({latlon[0]},{latlon[1]}) is {station['name']} (id={station['id']})")

# You can add params, ts and period similar to list_stations
station = smhi.closest_station(latlon, parameters=param, ts=('2000-01-01','2024-06-30'), full_period=True)

# or have the station list as input
station = smhi.closest_station(latlon, stations=stations)

# You can  convert stations to geodataframe and for example plot the stations
stations = smhi.stations_geo(stations)
stations.plot()


# You can also add distance method to stations or station that can handle inputs as lat lon 
from ClimateWeatherData import helpers
stations = helpers.add_distance_method(stations)
distances = stations.distance([65.640928, 22.026005])

station = helpers.add_distance_method(station)
distance = station.distance([65.640928, 22.026005])


