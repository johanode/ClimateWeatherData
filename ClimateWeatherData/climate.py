# -*- coding: utf-8 -*-
"""
Created on Sun May 22 15:10:49 2022

@author: Johan Odelius
"""
from ClimateWeatherData import smhi, helpers

# sub functions
def list_indicators():    
    df_indicators = helpers.get_indicators('df')
    return df_indicators


def list_stations(parameter_type='all', ts=None, full_period=False):
    """
    Returns a list of stations where all relevant data for climate indicators are available.
    
    :param parameter_type: Type of climate parameter ('temperature', 'precipitation', 'wind', 'combination', 'all').
                           If 'all', it includes all climate parameters.
    :param ts: Timestamp or range of timestamps (list or tuple) to filter stations based on data availability.
    :param full_period: If True, ensures that the station has data available for the entire specified period.
    :return: DataFrame containing stations with available data for all relevant parameters.
    """
    # Fetch the list of parameters based on the parameter_type
    params = helpers.get_climate_parameters(parameter_type)
    
    # Call the SMHI function to fetch stations for the specified parameters and timestamp
    df_stations = smhi.list_stations(params=params, ts=ts, full_period=full_period)

    if df_stations.empty:
        print("No stations found with data for all parameters.")
    
    return df_stations


def isin_station(station, parameter_type='all', ts=None, full_period=False):
    """
    Checks if the station has data for all relevant climate parameters.
    
    :param station: The station ID or name.
    :param parameter_type: Type of climate parameter ('temperature', 'precipitation', 'wind', etc.).
    :param ts: Optional timestamp or range of timestamps (list or tuple).
    :param full_period: If True, ensures data availability for the entire period.
    :return: True if all climate data is available for the station, False otherwise.
    """
    # Get the list of stations with available data for the given parameters
    df_stations = list_stations(parameter_type, ts=ts, full_period=full_period)
    
    # Check if the station is present in the list
    return smhi.get_station_value(station) in df_stations['id'].to_list()



# %% Temperature

# Medeltemperatur
def TAS(station, ts, time_period='y'):
    # Medeltemperatur (TAS)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp ('2020-01-10')
    #   time_period     : time period ('y','s'), default 'y'
    
    weather_parameter = 'TemperatureMeanPastMonth'
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Mean of TemperatureMeanPastMonth
    value = parameter_values.mean()

    return value

# Dygnsmaxtemperatur
def TX(station, ts, time_period='y'):
    # Dygnsmaxtemperatur (TX)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y','s','m'), default 'y'
    
    weather_parameter = 'TemperatureMaxPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Max of TemperatureMaxPast24h
    value = parameter_values.max()

    return value


# Dygnsminimitemperatur
def TN(station, ts, time_period='y'):
    # Dygnsminimitemperatur (TN)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y','s','m'), default 'y'
    
    weather_parameter = 'TemperatureMinPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Min of TemperatureMinPast24h
    value = parameter_values.min()

    return value


# Dygnsamplitud (varmast minus kallast)
def DTR(station, ts, time_period='m'):
    # Dygnsamplitud (varmast minus kallast) (DTR)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('m'), default 'm'

    weather_parameter = 'TemperatureMinPast24h'
    # Filter based on failure time and time period
    temperature_min = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'TemperatureMaxPast24h'
    # Filter based on failure time and time period
    temperature_max = smhi.get_weather_data(weather_parameter, station, ts, time_period)
   
    # Amplitude: max temperature - min temperature
    amplitude = temperature_max-temperature_min

    # Max of daily amplitude values
    value = amplitude.max()

    return value


# Varma dagar/högsommardagar (Maxtemperatur >20 ºC)
def WarmDays(station, ts, time_period='y'):
    # Varma dagar (WarmDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y','s'), default 'y'
    
    weather_parameter = 'TemperatureMaxPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Number of days over 20 deg
    value = (parameter_values > 20).sum()

    return value


# Värmebölja (dagar i följd med maxtemperatur > 20ºC)
def ConWarmDays(station, ts, time_period='y'):
    # Värmebölja (ConWarmDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'TemperatureMaxPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Days in a row with temperature more than 20 deg
    number_of_days = 0
    max_number_of_days = 0
    temperature_threshold = 20
    for value in parameter_values:
        if value > temperature_threshold:
            number_of_days += 1
            max_number_of_days = max(max_number_of_days, number_of_days)
        else:
            number_of_days = 0
    
    return max_number_of_days

# Nollgenomgångar (Antal dagar med högsta temp > 0ºC och lägsta temp < 0ºC)
def ZeroCrossingDays(station, ts, time_period='s'):
    # Nollgenomgångar (ZeroCrossingDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('s'), default 's'

    weather_parameter = 'TemperatureMinPast24h'
    # Filter based on failure time and time period
    temperature_min = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'TemperatureMaxPast24h'
    # Filter based on failure time and time period
    temperature_max = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Min temperature less than 0 and max temperature more than 0
    if temperature_min.size>0:
        if isinstance(ts, (list, tuple)):
            if time_period == 's':
                time_period = '3M'
            value = ((temperature_min < 0) & (temperature_max > 0)).resample(time_period).sum()
        else:
            value = ((temperature_min < 0) & (temperature_max > 0)).sum()
    else:
        value = float('NaN')

    return value

# Vegetationsperioden
def VegSeason(ser, temperature=5, days=4):
    # 4 days in a row with temperature more than 5 deg

    # Initialize variables
    number_of_days_above = 0
    veg_start = ser.iloc[-1]
    
    for idx, value in ser.iteritems():
        if value > temperature:
            number_of_days_above += 1
            if number_of_days_above >= days:
                veg_start = idx  # Vegperiod start
                break
        else:
            number_of_days_above = 0
    
    # Initialize variables
    number_of_days_below = 0
    previous = ser.loc[[veg_start]].index
    for idx, value in ser.loc[veg_start:].iteritems():
        # if start of vegperiod set and after 1 July 
        if idx.month >= 7 and value <= temperature:
            number_of_days_below += 1
            if number_of_days_below >= days:
                veg_end = previous  # Vegperiod slut
                break
        else:
            number_of_days_below = 0
            previous = idx
    
    return veg_start, veg_end

# Vegetationsperiodens slut (sista dag i sammanhängande 4-dags period med medeltemp > 5ºC
def VegSeasonDayEnd(station, ts, time_period='y'):
    # Vegetationsperiodens slut (VegSeasonDayEnd-5)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Vegperiod
    _,veg_end = VegSeason(parameter_values)

    # Returning last date of vegperiod
    return veg_end


# Vegetationsperiodens början (sista dag i sammanhängande 4-dags period med medeltemp > 5 ºC)
def VegSeasonDayStart(station, ts, time_period='y'):
    # Vegetationsperiodens början (VegSeasonDayStart-5)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Vegperiod
    veg_start,_ = VegSeason(parameter_values)

    # Returning first date of vegperiod
    return veg_start


# Vegetationsperiodens längd (medeltemp > 2/5ºC)
def VegSeasonLentgh(station, ts, time_period='y', temperature=5):
    # Vegetationsperiodens längd (VegSeasonLentgh-2/VegSeasonLentgh-5)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    #   temperature     : temperature definition of vegseason (2,5), default is 5

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Vegperiod
    veg_start,veg_end = VegSeason(parameter_values)

    # Returning length in days of vegperiod
    return (veg_end-veg_start).days


# Frostdagar (minimitemperatur < 0ºC )
def FrostDays(station, ts, time_period='s'):
    # Frostdagar (FrostDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('s'), default 's'


    weather_parameter = 'TemperatureMinPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Count days where min temperature is less than 0
    value = (parameter_values < 0).sum()

    return value


# Kalla dagar (maxtemperatur < -7ºC)
def ColdDays(station, ts, time_period='s'):
    # Kalla dagar (ColdDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('s'), default 's'

    weather_parameter = 'TemperatureMaxPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Days with max temperature less than -7
    value = (parameter_values < -7).sum()

    return value

# %% Nederbörd

# Summa nederbörd
def PR(station, ts, time_period='y'):
    # Summa nederbörd (PR)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('m','y','s'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Sum of PrecipPast24hAt06
    value = parameter_values.sum()

    return value


# Summa regn
def PRRN(station, ts, time_period='y'):
    # Summa nederbörd (PRRN)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period (y','s'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Join precipitation values with type of precipitation
    precip_data = precip_values.to_frame().join(precip_types.rename('Type'))
    
    # Data for days with rain
    valid_types = helpers.get_types('Rain')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types),'Value'].groupby(level=0).first()
    
    # Sum up all during time period
    value = precip_valid.sum()
                        
    return value


# Summa snö
def PRSN(station, ts, time_period='y'):
    # Summa snö (PRSN)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period (y','s'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Join precipitation values with type of precipitation
    precip_data = precip_values.to_frame().join(precip_types.rename('Type'))
     
    # Data for days with valid precipitation
    valid_types = helpers.get_types('Snow')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types),'Value'].groupby(level=0).first()
    
    # Sum up all during time period
    value = precip_valid.sum()  
    
    return value


# Summa underkylt regn
def SuperCooledPR(station, ts, time_period='y'):
    # Underkylt regn (SuperCooledPR)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Join precipitation values with type of precipitation
    precip_data = precip_values.to_frame().join(precip_types.rename('Type'))
     
    # Cooled rain types
    valid_types = helpers.get_types('SuperCooledRain')
    
    # Data for days with valid precipitation
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types),'Value'].groupby(level=0).first()
    
    # Sum up all during time period
    value = precip_valid.sum()

    return value


# Högsta nederbörd under 7 dagar
def PR7Dmax(station, ts, time_period='y'):
    # Högsta nederbörd  (PR7Dmax)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Sum of PrecipPast24hAt06 for rolling window of 7 days (sum or max??)
    values = parameter_values.rolling(7).sum()

    # Max of sum of precipitation
    return values.max()


# Maximal nederbördsintensitet
def PRmax(station, ts, time_period='y'):
    # Maximal nederbörd  (PRmax)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Max of PrecipPast24hAt06
    value = parameter_values.max()

    return value


# Maximal snöfallsintensitet
def PRSNmax(station, ts, time_period='y'):
    # Maximal snöfall  (PRSNmax)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Join precipitation values with type of precipitation
    precip_data = precip_values.to_frame().join(precip_types.rename('Type'))
  
    # Snow types
    valid_types = helpers.get_types('Snow') 
    
    # precip_data.loc[precip_data['Type'].isin(valid_types)].groupby('Type').max()
    
    # Data for days with valid precipitation
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types),'Value'].groupby(level=0).first()
    
    # Max during time period
    value = precip_valid.max()

    return value


# Kraftig nederbörd > 10 mm/dygn
def PRgt10Days(station, ts, time_period='y'):
    # Kraftig nederbörd  (PRgt10Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('s','y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Days of more than 10 mm precip
    value = (parameter_values > 10).sum()

    return value

# Extrem nederbörd > 25 mm/dygn
def PRgt25Days(station, ts, time_period='y'):
    # Extrem nederbörd  (PRgt25Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('s','y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Days of more than 25 mm precip
    value = (parameter_values > 25).sum()

    return value


# Torra dagar (med nederbörd < 1 mm)
def DryDays(station, ts, time_period='m'):
    # Torra dagar  (DryDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('m'), default 'm'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Days of less than 1 mm precip
    if parameter_values.size>0:
        value = (parameter_values < 1).sum()
    else:
        value = float('NaN')

    return value

# %% Snö på marken
# Snötäcke
def SncDays(station, ts, time_period='y'):
    # Snötäcke  (SncDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'SnowDepthPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Number of days with snow
    if parameter_values.size>0:
        value = (parameter_values > 0).sum()
    else:
        value = float('NaN')
        
    return value

# Maximalt snödjup (räknat som vatteninnehåll)
def SNWmax(station, ts, time_period='y'):
    # Maximalt snödjup  (SNWmax)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'SnowDepthPast24h'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    # Maximum snow depth
    value = parameter_values.max()

    return value

# %% Vind och densitet

# Medelvindhastighet i 10m-nivå
def SfcWind(station, ts, time_period='y'):
    # Medelvindhastighet  (SfcWind)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('s','y'), default 'y'

    weather_parameter = 'WindSpeed'
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, ts, time_period, idx='Date (UTC)')
    
    # Daily max of mean windspeed observations
    values = parameter_values.resample('1D').max()

    # Max of daily max during time period
    return values.max()

# Maximal byvind (10m-nivå)


def WindGustMax(station, ts, time_period='y'):
    # Maximal byvind  (WindGustMax)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'WindGust'  # Wind Gust
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, ts, time_period, idx='Date (UTC)')
    
    # Daily max of wind gust (byvind) observations
    values = parameter_values.resample('1D').max()

    # Max of daily max during time period
    return values.max()


# Antal dagar med byvind >21 m/s (10m-nivå)
def WindyDays(station, ts, time_period='y'):
    # Antal dagar med hård byvind  (WindyDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'WindGust'  # Wind Gust
    # Filter based on failure time and time period
    parameter_values = smhi.get_weather_data(weather_parameter, ts, time_period, idx='Date (UTC)')
    
    # Number of days with daily max of wind gust (byvind) above 21
    if parameter_values.size>0:
        value = (parameter_values.resample('1D').max() > 21).sum()
    else:
        value = float('NaN')

    return value

#%% Kombinationsindex

# Nederbörd när temperaturen ligger mellan 0.58 och 2 grader
def ColdRainDays(station, ts, time_period='y'):
    # Dagar kall nederbörd  (ColdRainDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # weather_parameter = 'PrecipTypePast24h'
    # # Filter based on failure time and time period
    # precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # precip_data = precip_data.join(precip_types.rename('Type'))
    # valid_types = helpers.get_types('Rain')
    # precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)]
    
    # Days with precip given temperature interval
    if precip_values.size>0:
        temperature_threshold = [.58, 2]
        i_temperature = (precip_data['Temperature']>temperature_threshold[0]) & (precip_data['Temperature']<temperature_threshold[1])
        value = (precip_data.loc[i_temperature,'Value']>0).sum()
    else:
        value = float('NaN')

    return value


# Nederbörd ( > 10 mm/dygn) när temperaturen ligger mellan 0.58 och 2 grader
def ColdRainGT10Days(station, ts, time_period='y'):
    # Dagar mkt kall nederbörd  (ColdRainGT10Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # weather_parameter = 'PrecipTypePast24h'
    # # Filter based on failure time and time period
    # precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # precip_data = precip_data.join(precip_types.rename('Type'))
    # valid_types = helpers.get_types('Rain')
    # precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)]
    
    # Number of days of precip > 10 given temperature interval
    if precip_values.size>0:
        temperature_threshold = [.58, 2]
        i_temperature = (precip_data['Temperature']>temperature_threshold[0]) & (precip_data['Temperature']<temperature_threshold[1])
        precip_threshold = 10
        value = (precip_data.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value


# Nederbörd ( > 20 mm/dygn) när temperaturen ligger mellan 0.58 och 2 grader
def ColdRainGT20Days(station, ts, time_period='y'):
    # Dagar kraftig kall nederbörd  (ColdRainGT20Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
   # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # weather_parameter = 'PrecipTypePast24h'
    # # Filter based on failure time and time period
    # precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # precip_data = precip_data.join(precip_types.rename('Type'))
    # valid_types = helpers.get_types('Rain')
    # precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)]
    
    # Number of days of precip > 20 given temperature interval
    if precip_values.size>0:
        temperature_threshold = [.58, 2]
        i_temperature = (precip_data['Temperature']>temperature_threshold[0]) & (precip_data['Temperature']<temperature_threshold[1])
        precip_threshold = 20
        value = (precip_data.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value

# Nederbörd när temperaturen ligger mellan -2 och 0.58 grader
def WarmSnowDays(station, ts, time_period='y'):
    # Dagar varm snö  (WarmSnowDays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # weather_parameter = 'PrecipTypePast24h'
    # # Filter based on failure time and time period
    # precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # precip_data = precip_data.join(precip_types.rename('Type'))
    # valid_types = helpers.get_types('Snow')
    # precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)]
    
    # Days with precip given temperature interval
    if precip_values.size>0:
        temperature_threshold = [-2, .58]
        i_temperature = (precip_data['Temperature']>temperature_threshold[0]) & (precip_data['Temperature']<temperature_threshold[1])
        value = (precip_data.loc[i_temperature,'Value']>0).sum()
    else:
        value = float('NaN')

    return value


# Nederbörd (> 10 mm/dygn) när temperaturen ligger mellan -2 och 0.58 grader
def WarmSnowGT10Days(station, ts, time_period='y'):
    # Dagar mkt varm snö  (WarmSnowGT10Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # weather_parameter = 'PrecipTypePast24h'
    # # Filter based on failure time and time period
    # precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # precip_data = precip_data.join(precip_types.rename('Type'))
    # valid_types = helpers.get_types('Snow')
    # precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)]
    
    # Number of days of precip > 10 given temperature interval
    if precip_values.size>0:
        temperature_threshold = [-2, .58]
        i_temperature = (precip_data['Temperature']>temperature_threshold[0]) & (precip_data['Temperature']<temperature_threshold[1])
        precip_threshold = 10
        value = (precip_data.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value


# Nederbörd (> 20 mm/dygn) när temperaturen ligger mellan -2 och 0.58 grader
def WarmSnowGT20Days(station, ts, time_period='y'):
    # Dagar kraft varm snö  (WarmSnowGT20Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # weather_parameter = 'PrecipTypePast24h'
    # # Filter based on failure time and time period
    # precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # precip_data = precip_data.join(precip_types.rename('Type'))
    # valid_types = helpers.get_types('Snow')
    # precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)]
    
    # Number of days of precip > 20 given temperature interval
    if precip_values.size>0:
        temperature_threshold = [-2, .58]
        i_temperature = (precip_data['Temperature']>temperature_threshold[0]) & (precip_data['Temperature']<temperature_threshold[1])
        precip_threshold = 20
        value = (precip_data.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value


# Regn när temperaturen är under 2 grader
def ColdPRRNdays(station, ts, time_period='y'):
    # Regn under 2 grader  (ColdPRRNdays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # Add precipitaion type
    precip_data = precip_data.join(precip_types.rename('Type'))
    # Filter out days with rain
    valid_types = helpers.get_types('Rain')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)].groupby(level=0).first()
    
    # Number of days of rain given temperature interval
    if precip_valid.size>0:
        temperature_threshold = 2
        i_temperature = precip_data['Temperature']<temperature_threshold
        value = (precip_valid.loc[i_temperature,'Value']>0).sum()
    else:
        value = float('NaN')

    return value


# Regn ( > 10 mm/dygn) när temperaturen är under 2 grader
def ColdPRRNgt10Days(station, ts, time_period='y'):
    # Regn under 2 grader  (ColdPRRNgt10Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # Add precipitaion type
    precip_data = precip_data.join(precip_types.rename('Type'))
    # Filter out days with rain
    valid_types = helpers.get_types('Rain')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)].groupby(level=0).first()
    
    # Number of days of rain more than 10 mm given temperature interval
    if precip_valid.size>0:
        temperature_threshold = 2
        i_temperature = precip_valid['Temperature']<temperature_threshold
        precip_threshold = 10
        value = (precip_valid.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value

# Regn ( > 20 mm/dygn) när temperaturen är under 2 grader
def ColdPRRNgt20Days(station, ts, time_period='y'):
    # Regn under 2 grader  (ColdPRRNgt20Days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
   
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # Add precipitaion type
    precip_data = precip_data.join(precip_types.rename('Type'))
    # Filter out days with rain
    valid_types = helpers.get_types('Rain')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)].groupby(level=0).first()
    
    # Number of days of rain more than 20 mm given temperature threshold
    if precip_valid.size>0:
        temperature_threshold = 2
        i_temperature = precip_valid['Temperature']<temperature_threshold
        precip_threshold = 20
        value = (precip_valid.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value


# Snö när temperaturen är över -2 grader
def WarmPRSNdays(station, ts, time_period='y'):
    # Snö över -2 grader  (WarmPRSNdays)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # Add precipitaion type
    precip_data = precip_data.join(precip_types.rename('Type'))
    # Filter out days with snow
    valid_types = helpers.get_types('Snow')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)].groupby(level=0).first()
    
    # Number of days of rain given temperature interval
    if precip_valid.size>0:
        temperature_threshold = -2
        i_temperature = precip_valid['Temperature']>temperature_threshold
        value = (precip_valid.loc[i_temperature,'Value']>0).sum()
    else:
        value = float('NaN')

    return value


# Snö ( > 10 mm/dygn) när temperaturen är över -2 grader
def WarmPRSNgt10days(station, ts, time_period='y'):
    # Snö över -2 grader  (WarmPRSNgt10days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'
    
    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # Add precipitaion type
    precip_data = precip_data.join(precip_types.rename('Type'))
    # Filter out days with snow
    valid_types = helpers.get_types('Snow')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)].groupby(level=0).first()
    
    # Number of days of rain given temperature threshold
    if precip_valid.size>0:
        temperature_threshold = -2
        i_temperature = precip_valid['Temperature']>temperature_threshold
        precip_threshold = 10
        value = (precip_valid.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value

# Snö ( > 20 mm/dygn) när temperaturen är över -2 grader
def WarmPRSNgt20days(station, ts, time_period='y'):
    # Snö över -2 grader  (WarmPRSNgt20days)
    # Input
    #   station         : station id [int]
    #   ts              : timestamp
    #   time_period     : time period ('y'), default 'y'

    weather_parameter = 'PrecipPast24hAt06'
    # Filter based on failure time and time period
    precip_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    weather_parameter = 'PrecipTypePast24h'
    # Filter based on failure time and time period
    precip_types = smhi.get_weather_data(weather_parameter, station, ts, time_period)

    weather_parameter = 'TemperaturePast24h'
    # Filter based on failure time and time period
    temperature_values = smhi.get_weather_data(weather_parameter, station, ts, time_period)
    
    # Add temperture values to the precipitaion values
    precip_data = precip_values.to_frame().join(temperature_values.rename('Temperature'))
    # Add precipitaion type
    precip_data = precip_data.join(precip_types.rename('Type'))
    # Filter out days with snow
    valid_types = helpers.get_types('Snow')
    precip_valid = precip_data.loc[precip_data['Type'].isin(valid_types)].groupby(level=0).first()
    
    # Number of days of rain given temperature interval
    if precip_valid.size>0:
        temperature_threshold = -2
        i_temperature = precip_valid['Temperature']>temperature_threshold
        precip_threshold = 20
        value = (precip_valid.loc[i_temperature,'Value']>precip_threshold).sum()
    else:
        value = float('NaN')

    return value