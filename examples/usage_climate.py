# Import libs
from ClimateWeatherData import smhi, climate

# Get climate feature/indicator for a station at a certain time
# List indicators
indicators = climate.list_indicators()
print(indicators.head())

# List station with temperature climate indicators available between specified time range
stations = climate.list_stations(parameter_type='Temperature', ts=('2000','2023'), full_period=True)

# Select weather station
station = 'Luleå-Kallax Flygplats'

# Check if data avaiable for station to compute indicators
if climate.isin_station(station):
    print('Data for all climate indicators is avalable for station %s (id=%d)' % (station, smhi.get_station_value(station)))
else:
    print('Climate data is NOT avalable for station %s (id=%d)' % (station, smhi.get_station_value(station)))

# Time period can also be added
if climate.isin_station(station, parameter_type='Temperature', ts=('2010','2020'), full_period=True):
    print('Data for climate indicators is avalable for station %s (id=%d)' % (station, smhi.get_station_value(station)))
else:
    print('Climate data is NOT avalable for station %s (id=%d)' % (station, smhi.get_station_value(station)))
    

# e.g. WarmDays (Days with temperature more than 20 deg)
# defualut time period is 'y'
ts = '2012'
indicator_value = climate.WarmDays(station, ts)
print('Warm days during %s = %d' % (ts, indicator_value))

# e.g. ConWarmDays (Days in a row with temperature more than 20 deg)
# defualut time period is 'y'
ts = '2024'
indicator_value, values = climate.ConWarmDays(station, ts, return_parameter_values=True)
print('Con. warm days %s = %d' % (ts, indicator_value))

# e.g. ZeroCrossingDays
ts = '2020-01'
# default time period is 's', will be Dec 2019 - Feb 2020
indicator_value = climate.ZeroCrossingDays(station, ts, 's')

# Use f-string for printing time period and indicator value
start_ts, end_ts = smhi.get_time_period(ts, 's', '%Y-%m-%d')
print(f'{start_ts} - {end_ts}: Zero crossing days = {indicator_value}')

# For the 'month' time period
time_period = 'm'
ts = '2012-01-03'
indicator_value = climate.ZeroCrossingDays(station, ts, time_period)

# Use f-string for printing month-based period and indicator value
start_ts = smhi.get_time_period(ts, time_period, '%Y-%m-%d')[0]
print(f'{start_ts}: Zero crossing days = {indicator_value}')

