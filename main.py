# Import libs
import pandas as pd
import smhi
import climate


# Get weather parameters
parameters = smhi.list_parameters()
print(parameters.head())

# Find stations with certain parameter
param = 'TemperaturePast1h'
param_id = smhi.get_param_value(param)
stations = smhi.list_stations(param_id)
print(stations.head())

# Print selected weather station
station = 162860
station_name = stations.set_index('id').loc[station,'name']
print(station_name)

# Download historical data from station for parameter
data = smhi.get_corrected(param_id, station)
print(data.head())

# Check if data available for parameter for station
if smhi.isin_station(param_id, station):
    print('%s (id=%d) is avalable in station %s (id=%d)' % (param, param_id, station_name, station))
else:
    print('%s (id=%d) is NOT avalable in station %s (id=%d)' % (param, param_id, station_name, station))


# Get parameter values for a station at a certain time
ts = pd.to_datetime('2012-04-03 11:00') #.date()
values = smhi.get_values(param_id, station, ts, idx='Date (UTC)')
print(values)


# Get parameter values for a station at a certain time period
time_period = 'w' #('y' : year, 's' : season, 'm' : month)
values = smhi.get_values(param_id, station, ts, time_period)
print(values)


# Get climate feature/indicator for a station at a certain time, e.g. failure time
# List indicators
indicators = smhi.list_indicators()
print(indicators.head())

# List stations where climate data is available
# This will be update with an time period
valid_stations = climate.list_stations()

# Check if data avaiable for station to compute indicators
# This will be update with an time period
if climate.isin_station(station): # station in valid_stations['id'].to_list()
    print('Data for all climate indicators is avalable for station %s (id=%d)' % (station_name, station))
else:
    print('Climate data is NOT avalable for station %s (id=%d)' % (station_name, station))


# e.g. WarmDays (Days with temperature more than 20 deg)
# defualut time period is 'y'
indicator_value = climate.WarmDays(station, ts)
print('Warm days = %d' % indicator_value)

# e.g. ConWarmDays (Days in a row with temperature more than 20 deg)
# defualut time period is 'y'
indicator_value = climate.ConWarmDays(station, ts)
print('Con. warm days = %d' % indicator_value)

# get time period 
ts = pd.to_datetime('2012-04-03').date()
for time_period in ['m','s','y']:
   print(smhi.get_time_period(ts, time_period)) 

# e.g. ZeroCrossingDays
time_period = 's'
ts = pd.to_datetime('2012-01-03').date()
indicator_value = climate.ZeroCrossingDays(station, ts)
print('%s-%s: ' % smhi.get_time_period(ts, time_period) + 'Zero crossing days = %d' % indicator_value)

ts = pd.to_datetime('2020-01-03').date()
# defualut time period is 's', will be Dec 2020 - Feb 2020
indicator_value = climate.ZeroCrossingDays(station, ts)
print('%s-%s: ' % smhi.get_time_period(ts, time_period) + 'Zero crossing days = %d' % indicator_value)