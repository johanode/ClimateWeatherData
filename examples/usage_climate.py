# Import libs
from ClimateWeatherData import smhi, climate

# Get climate feature/indicator for a station at a certain time
# List indicators
indicators = climate.list_indicators()
print(indicators.head())

# List stations where climate data is available
valid_stations = climate.list_stations()
# List stations where climate data is available at a certain date
valid_stations = climate.list_stations(ts='2010-01-23')

# Select weather station
station_name = 'Luleå-Kallax Flygplats'
station_id = smhi.get_station_info(station_name)

# Check if data avaiable for station to compute indicators
# This will be update with an time period
if climate.isin_station(station_id): # station in valid_stations['id'].to_list()
    print('Data for all climate indicators is avalable for station %s (id=%d)' % (station_name, station_id))
else:
    print('Climate data is NOT avalable for station %s (id=%d)' % (station_name, station_id))


# e.g. WarmDays (Days with temperature more than 20 deg)
# defualut time period is 'y'
ts = '2012'
indicator_value = climate.WarmDays(station_id, ts)
print('Warm days during %s = %d' % (ts, indicator_value))

# e.g. ConWarmDays (Days in a row with temperature more than 20 deg)
# defualut time period is 'y'
indicator_value = climate.ConWarmDays(station_id, ts)
print('Con. warm days %s = %d' % (ts, indicator_value))

# get time period 
ts = '2012-04-03'
for time_period in ['m','s','y']:
   print(smhi.get_time_period(ts, time_period)) 

# e.g. ZeroCrossingDays
ts = '2020-01-03'
# defualut time period is 's', will be Dec 2020 - Feb 2020
indicator_value = climate.ZeroCrossingDays(station_id, ts)
print('%s-%s: ' % smhi.get_time_period(ts, 's') + 'Zero crossing days = %d' % indicator_value)

time_period = 'm'
ts = '2012-01-03'
indicator_value = climate.ZeroCrossingDays(station_id, ts, time_period)
print('%s: ' % smhi.get_time_period(ts, time_period) + 'Zero crossing days = %d' % indicator_value)
