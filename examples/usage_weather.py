# -*- coding: utf-8 -*-
from ClimateWeatherData import smhi

# Get weather parameters
parameters = smhi.list_parameters()
print(parameters.head())

# Select weather station
station = 'Luleå-Kallax Flygplats'

# Select weather parameter
param = 'TemperaturePast24h'

# Download data from station for parameter
# historical data up to 3 month from now are quality corrected data retrieved using smhi.get_corrected
# latest 4 month data are retrieved using smhi.get_latest_months
data = smhi.get_weather_data(param, station)
print(data.head())
    
# Get parameter values for a station at a certain time
# 24h data 
ts = '2024-09-03'
data = smhi.get_weather_data(param, station, ts)
print(data)

# Get parameter values for a station at a certain time interval
# 24h data 
ts = ('2001-01-01', '2024-06-30')
data = smhi.get_weather_data(param, station, ts)
print(data)

# Get parameter values for a station at a certain time period
ts = '2024-04-03'
time_period = 'm' #('y' : year, 's' : season, 'm' : month)
data = smhi.get_weather_data(param, station, ts, time_period)
print(data)

# Hourly data
param = 'TemperaturePast1h'
ts = '2012-04-03 11:00'
data = smhi.get_weather_data(param, station, ts)
print(data)

# Specify time range
ts = ('2022-04-01 07:00', '2022-04-03 21:00')
data = smhi.get_weather_data(param, station, ts)
print(data)
