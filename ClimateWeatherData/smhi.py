#See also https://github.com/thebackman/SMHI

from ClimateWeatherData import api_endpoints, helpers
import requests
import pandas as pd
#import json
#import logging
import numbers
#import csv


def list_stations(params, ts=None, full_period=False):
    """
    Returns a list of stations that have data for all specified parameters.
    
    :param params: A single parameter or a list of parameters to filter stations.
                   Can be a string or a list of parameter strings (e.g., ['TemperaturePast24h', 'PrecipPast12h']).
    :param ts: Timestamp or range of timestamps (list or tuple) to filter stations based on data availability.
    :param full_period: If True, ensures that the station has data available for the entire specified period.
    :return: A DataFrame of stations that have data for all parameters, with no columns specified (full station info).
    """
    
    # Convert a single parameter to a list if it's not already
    if not isinstance(params, (list, tuple)):
        params = [params]
    
    # Validate and get parameter IDs
    param_ids = [get_param_value(param) for param in params]
    
    # Initialize with stations for the first parameter
    df_stations = list_stations_for_param(param_ids[0], ts=ts, full_period=full_period)
    
    # If no stations are found for the first parameter, return an empty result
    if df_stations.empty:
        print(f"No stations found for parameter {params[0]}.")
        return df_stations
    
    # Create a set of station IDs for the first parameter
    stations = set(df_stations['id'])
    
    # Loop through the rest of the parameters and find intersections of stations
    for param_id in param_ids[1:]:
        df = list_stations_for_param(param_id, ts=ts, full_period=full_period)
        
        # If no stations are found for the parameter, return an empty result
        if df.empty:
            print(f"No stations found for parameter ID {param_id}.")
            return df
        
        # Update the station list by intersecting with the new parameter's stations
        stations = stations.intersection(df['id'].to_list())
        
        # If no common stations are left, return an empty result
        if not stations:
            print("No common stations found with data for all parameters.")
            return pd.DataFrame(columns=df_stations.columns)
    
    # Return the full station data, filtered by the station IDs that have data for all parameters
    return df_stations[df_stations['id'].isin(stations)]


def list_stations_for_param(param, ts=None, full_period=False):
    """
    Helper function to list stations for a single parameter.
    
    :param param: The weather parameter ID to list stations for.
    :param ts: Timestamp or range of timestamps (list or tuple) to filter stations.
    :param full_period: If True, ensures that the station has data available for the entire specified period.
    :return: DataFrame of stations for the given parameter.
    """
    # Create the API address
    adr = api_endpoints.ADR_PARAMETER
    adr_full = adr.format(parameter=param)

    # Send request and get data
    data = helpers.api_return_data(adr_full)

    # Gather and wrangle the data about available stations
    df = pd.DataFrame(data["station"])

    # Fix the date and time variables into something readable
    for col in ['from', 'to', 'updated']:
        df[col] = pd.to_datetime(df[col], unit="ms")
    
    # If no timestamp is provided, return the full list
    if ts is None:
        return df
    
    # If a single timestamp is provided
    if isinstance(ts, str):
        ts = pd.to_datetime(ts).isoformat()
        qrstr = "`from` <= '{0}' and `to` >= '{0}'".format(ts)
        return df.query(qrstr)
    
    # If a list or tuple of two timestamps is provided, filter based on the range
    elif isinstance(ts, (tuple, list)) and len(ts) == 2:
        start_ts = pd.to_datetime(ts[0]).isoformat()
        end_ts = pd.to_datetime(ts[1]).isoformat()

        if full_period:
            # Ensure stations have data for the entire period
            qrstr = "`from` <= '{0}' and `to` >= '{1}'".format(start_ts, end_ts)
        else:
            # Filter stations that were available at some point during the period
            qrstr = "`from` <= '{1}' and `to` >= '{0}'".format(start_ts, end_ts)
        
        return df.query(qrstr)
    
    else:
        raise ValueError("Invalid timestamp format. Must be a string, list, or tuple of two timestamps.")



def list_parameters():
    df_parameters = helpers.get_parameters('df')
    return df_parameters


def get_station_info(station_input, param_id=None, ts=None):
    """
    Return station ID if station name is provided, or station name if station ID is provided.
    
    Parameters:
    - station_input: Either the station name (str) or station ID (int).
    - param_id: Optional parameter ID to filter stations by. If not provided, defaults to 'TemperaturePast24h'.
    - ts: Optional timestamp to filter stations by date.

    Returns:
    - station_name (str) if station ID is provided.
    - station_id (int) if station name is provided.
    """
    # If no param_id is provided, use 'TemperaturePast24h' as the default
    if param_id is None:
        param = 'TemperaturePast24h'        
    
    # Get all stations for the given parameter and optional timestamp
    stations = list_stations(param, ts)

    # If the input is a station ID (int), return the corresponding station name
    if isinstance(station_input, numbers.Number):
        try:
            station_name = stations.set_index('id').loc[station_input, 'name']
            return station_name
        except KeyError:
            raise ValueError(f"Station ID {station_input} not found.")
    
    # If the input is a station name (str), return the corresponding station ID
    elif isinstance(station_input, str):
        try:
            valid_station = helpers.validatestring(station_input, stations['name'].to_list())
            station_id = stations.set_index('name').loc[valid_station, 'id']
            return station_id
        except KeyError:
            raise ValueError(f"Station name '{station_input}' not found.")
    
    else:
        raise ValueError("station_input must be either a station name (str) or station ID (int).")

def get_station_value(station):
    # check if parameter isnumeric
    if isinstance(station,numbers.Number):
        station_id = station
    else:
        station_id = get_station_info(station)
    return station_id    
    

def get_param_name(parameter):    
    # Load parameters
    df_parameters = pd.DataFrame(helpers.get_parameters())
    
    # Get parameter ID (normalizes whether input is name or ID)
    parameter_id = get_param_value(parameter)
    
    try:
        # Retrieve the corresponding parameter name
        parameter_name = df_parameters.set_index('key').loc[parameter_id, 'label']
        return parameter_name
    except KeyError:
        raise ValueError(f"Parameter {parameter} not found.")



def get_param_value(parameter):
    # check if parameter isnumeric
    if isinstance(parameter,numbers.Number):
        parameter_id = parameter
    else:
        # Load parameters
        df_parameters = pd.DataFrame(helpers.get_parameters())
        # Validate string input
        valid_param = helpers.validatestring(parameter, df_parameters['label'].to_list())
        # Get id
        parameter_id = df_parameters.set_index('label').loc[valid_param, 'key']
    
    return parameter_id        

def isin_station(param, station, ts=None):   
    # check if parameter is available on station
    df_stations = list_stations(param, ts=ts)
    valid_stations = df_stations['id'].to_list()
    return get_station_value(station) in valid_stations

def get_time_period(ts, time_period, time_format='%Y-%m-%d %H:%M'):
    # Get the start and end timestamps for the period, formatted as datetime objects
    if time_format == 'isoformat':
        return helpers.format_ts(ts, time_period=time_period, isoformat=True)    
    else:
        ts_period = helpers.format_ts(ts, time_period=time_period, isoformat=False)    
        # Return a tuple of formatted dates as strings    
        return tuple(t.strftime(time_format) for t in ts_period)




def get_corrected(param, station, translate=True):
    """
    Get corrected data from the SMHI API for a specific weather parameter and station.
    
    :param param: The weather parameter ID or name.
    :param station: The station ID.
    :param translate: Whether to translate the column names to English.
    :return: A DataFrame with the corrected data.
    """
    # Validate the input weather parameter (param)
    param = get_param_value(param)
    
    # Validate the input station
    station = get_station_value(station)
    
    # Create the API address
    adr_full = api_endpoints.ADR_CORRECTED.format(parameter=param, station=station)
    
    # Define configurations for each parameter or parameter group
    default_config = {'usecols': [0, 1, 2, 3, 4], 'k_value': 3, 'parse_dates': [0, 1, 2]}
    param_configs = {
        1:  {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # TemperaturePast1h
        26: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # TemperatureMinPast24h
        27: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # TemperatureMaxPast24h
        39: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # DewPointTempPast1h
        2:  {'usecols': [0, 1, 2, 3, 4], 'parse_dates': [0, 1, 2], 'k_value': 3},                           # TemperaturePast24h
        19: {'usecols': [0, 1, 2, 3, 4], 'parse_dates': [0, 1, 2], 'k_value': 3},                           # TemperatureMinPast24h
        20: {'usecols': [0, 1, 2, 3, 4], 'parse_dates': [0, 1, 2], 'k_value': 3},                           # TemperatureMaxPast24h
        3:  {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # Windspeed
        4:  {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # WindDirection
        21: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # WindGust
        5:  {'usecols': [0, 1, 2, 3, 4], 'parse_dates': [0, 1, 2], 'k_value': 3},                           # PrecipPast24hAt06
        23: {'usecols': [0, 1, 2, 3, 4], 'parse_dates': [0, 1, 2], 'k_value': 3},                           # PrecipPastMonth
        6:  {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # Humidity
        7:  {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # PrecioPast1h
        8:  {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # SnowDepthPast24h
        9:  {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # Pressure
        12: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # Visibility
        13: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # CurrentWeather
        16: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # CloudCover
        28: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # Second CloudLayer
        29: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # CloudAmount
        18: {'usecols': [0, 1, 2, 3, 4], 'parse_dates': [0, 1, 2], 'k_value': 3},                           # PrecipTypePast24h
        17: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}, # PrecipPast12h
        40: {'usecols': [0, 1, 2, 3], 'parse_dates': {'Datum (UTC)': ['Datum', 'Tid (UTC)']}, 'k_value': 2}  # GroundCondition
    }
    
    # Get the configuration for the given parameter, or apply a default configuration
    config = param_configs.get(param, default_config)
    
    # Download the CSV data
    df = helpers.read_csv(
        adr_full,
        usecols=config['usecols'],
        parse_dates=config['parse_dates'],
        dtype={config['k_value']: 'numeric'}
    )
    
    # Rename columns to English if required
    df = helpers.rename_columns_to_english(df, config['k_value'], translate=translate)
    
    return df



def get_latest_months(param, station):
    # validate input weather parameter (param)
    param = get_param_value(param)   
    
    # Validate the input station
    station = get_station_value(station)
    
    # create the API adress
    adr = api_endpoints.ADR_LATEST_MONTHS
    adr_full = adr.format(parameter = param, station = station)    
    # print(adr_full)
    
    # initiate the call
    response = requests.get(adr_full)    
    # try to get the json data (exceptions will be catched later)    
    df = pd.DataFrame(response.json()['value'])
    
    df.rename(columns = {'Value':'value'}, inplace=True)

    date_cols = ['from', 'to', 'ref']
    if param in [2,5] or all([key in df for key in date_cols]):    
        df['value'] = pd.to_numeric(df['value'])
    elif param in [17]: #PrecipPast12h
        date_cols = ['date']
    else:
        date_cols = ['date']
        df['value'] = pd.to_numeric(df['value'])
    
    for col in date_cols:
        if col=='ref':
            df[col] = pd.to_datetime(df[col]).dt.date
        else:
            df[col] = pd.to_datetime(df[col]*1e6)
    
    
    columns = {
        'date' : 'Date (UTC)',
        'from' : 'From Date (UTC)',
        'to' : 'To Date (UTC)',
        'ref' : 'Date',
        'value' : 'Value',
        'quality' : 'Quality'
        }
    # columns[df.columns[k_value]] = 'Value'    
    df.rename(columns = columns, inplace=True)
    
    return df


def get_values(param, station, ts=None, time_period=None, idx=None, col='Value', check_station=False):
    """
    Get weather parameter values for a given station, parameter, and timestamp or time period.
    
    :param param: The weather parameter (either ID or name).
    :param station: The station ID or name.
    :param ts: Timestamp or tuple of timestamps.
    :param time_period: Time period ('y', 'm', 's') for yearly, monthly, or seasonal data.
    :param col: The column name to extract (default is 'Value').
    :param check_station: Check if the parameter is available for the station.    
    :return: Filtered weather data.
    """
        
    # Optional: Check if the parameter is available in the station
    if check_station and not isin_station(param, station):
        raise ValueError(f"Parameter {param} is not available for station {station}")

    # Ensure ts is in datetime format for comparison, if provided
    if ts is not None:
        ts = helpers.format_ts(ts, time_period=time_period)

    data_frames = []
    
    # If ts is not provided or goes beyond the historical range, get the corrected historical data
    if ts is None or min(ts) <= (pd.Timestamp.now() - pd.DateOffset(months=3)):
        # Download corrected historical data (last 3 months not available)
        data_historical = get_corrected(param, station)
        data_historical['Date'] = pd.to_datetime(data_historical['Date'], errors='coerce')
        data_frames.append(data_historical)

    # If ts is not provided or goes beyond the historical range, get the latest data as well
    if ts is None or max(ts) > (pd.Timestamp.now() - pd.DateOffset(months=4)):
        # Download latest 4 month data
        data_latest = get_latest_months(param, station)
        data_latest['Date'] = pd.to_datetime(data_latest['Date'], errors='coerce')
        data_frames.append(data_latest)

    # Concatenate historical and latest data
    data = pd.concat(data_frames)

    # Automatically detect the correct index column if idx is not provided
    if idx is None:
        if 'Date (UTC)' in data.columns:
            idx = 'Date (UTC)'  # Use 'Date (UTC)' if available (for hourly data)
        elif 'Date' in data.columns:
            idx = 'Date'  # Use 'Date' for daily data
        else:
            raise ValueError("Neither 'Date' nor 'Date (UTC)' columns found in the data.")
    
    # Remove duplicates, keeping historical data for overlapping dates
    data = data.drop_duplicates(subset=idx, keep='first')
   
    # Sort by the selected index for clean chronological ordering
    data = data.sort_values(by=idx).reset_index(drop=True)
    
    # Filter data based on ts and time_period if provided
    if ts is not None:
        values = helpers.filter_time(data, ts, time_period, idx=idx, col=col)
    else:
        values = data.set_index(idx)[col]

    values.name = get_param_name(param)
    return values


