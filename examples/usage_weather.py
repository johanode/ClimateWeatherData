# -*- coding: utf-8 -*-
from ClimateWeatherData import smhi

# Get weather parameters
parameters = smhi.list_parameters()
print(parameters.head())

# Select weather station
station = 'Luleå-Kallax Flygplats'
station_id = smhi.get_station_info(station)

# Select weather parameter
param = 'TemperaturePast24h'
param_id = smhi.get_param_value(param)

# Download historical data from station for parameter
data = smhi.get_corrected(param_id, station_id)
print(data.head())
    
# Get parameter values for a station at a certain time
# 24h data 
ts = '2012-04-03'
values = smhi.get_values(param_id, station_id, ts)
print(values)
# Hourly data
ts = '2012-04-03 11:00'
values = smhi.get_values(param_id, station_id, ts, idx='Date (UTC)')
print(values)

# Get parameter values for a station at a certain time period
ts = '2012-04-03'
time_period = 'm' #('y' : year, 's' : season, 'm' : month)
values = smhi.get_values(param_id, station_id, ts, time_period)
print(values)

# Specify time range
param = 'TemperaturePast1h'
param_id = smhi.get_param_value(param)
ts = ('2012-04-01 11:00', '2012-04-03 11:00')
values = smhi.get_values(param_id, station_id, ts, idx='Date (UTC)')
print(values)
