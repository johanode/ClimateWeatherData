#See also https://github.com/thebackman/SMHI

from ClimateWeatherData import api_endpoints, helpers
import requests
import pandas as pd
#import json
#import logging
import numbers
import csv


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
    df_parameters = pd.DataFrame(helpers.get_parameters())
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
        param_id = get_param_value(param)
    
    # Get all stations for the given parameter and optional timestamp
    stations = list_stations(param_id, ts)

    # If the input is a station ID (int), return the corresponding station name
    if isinstance(station_input, int):
        try:
            station_name = stations.set_index('id').loc[station_input, 'name']
            return station_name
        except KeyError:
            raise ValueError(f"Station ID {station_input} not found.")
    
    # If the input is a station name (str), return the corresponding station ID
    elif isinstance(station_input, str):
        try:
            station_id = stations.set_index('name').loc[station_input, 'id']
            return station_id
        except KeyError:
            raise ValueError(f"Station name '{station_input}' not found.")
    
    else:
        raise ValueError("station_input must be either a station name (str) or station ID (int).")


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

def isin_station(parameter, station, ts=None):
    # Validate paramter input
    parameter_id = get_param_value(parameter)
    
    # check if parameter is available on station
    df_stations = list_stations(parameter_id, ts=ts)
    valid_stations = df_stations['id'].to_list()
    return station in valid_stations

def get_time_period(ts, time_period):
    if isinstance(time_period, str):
        ts = pd.to_datetime(ts)
    return tuple(helpers.get_filter(ts, time_period))

def read_csv(adr_full, delimiter=';', usecols=None, parse_dates=None, keep_date_col=True, dtype=None):    
    response = requests.get(adr_full).text
    lines = response.splitlines()
    header_row = 8
    for k, line in enumerate(lines):
        if k>=header_row and 'Datum' in line:
            header_row = k
            break
    
    skip_rows = header_row+1
    
    cols = lines[header_row].split(delimiter)
    # print(cols)
    
    if usecols is not None:
        cols=[col for k,col in enumerate(cols) if k in usecols or col in usecols]
    d = csv.DictReader(lines[skip_rows:], delimiter=delimiter, fieldnames=cols)
    df = pd.DataFrame(data=list(d), columns=cols)
    
    if parse_dates is not None:
        # [['Datum', 'Tid (UTC)']]
        if isinstance(parse_dates, dict):            
            parse_dates = parse_dates.items()
            # parse_dates = [{key : value} for key, value in parse_dates.items()]
            
        for parse_date in parse_dates:
            if isinstance(parse_date, tuple):
                result = parse_date[0]
                parse_date = parse_date[1]
            elif isinstance(parse_date, list):
                result = '_'.join(parse_date)     
            elif isinstance(parse_date, str):            
                result = parse_date
            else: #numeric
                parse_date = df.columns[parse_date]
                result = parse_date
                
            if isinstance(parse_date, list):
                # s = pd.to_datetime(df[parse_date].astype(str).agg(' '.join, axis=1))
                s = pd.to_datetime(df[parse_date[0]].str.cat(df[parse_date[1]], sep=' '))
            else:
                s = pd.to_datetime(df[parse_date])
            
            if result==parse_date:
                df[result] = s                
            else:
                df.insert(0, result, s)  
            
            if keep_date_col==False:
                df.drop(labels=parse_date, axis=1, inplace=True)     
            else:
                if isinstance(parse_date, str):
                    parse_date = [parse_date]
                for col in parse_date:
                    if isinstance(keep_date_col, str):
                            if not col==keep_date_col:
                                df.drop(labels=col, axis=1, inplace=True)
                    elif isinstance(keep_date_col, list):
                        if not col in keep_date_col:
                            df.drop(labels=col, axis=1, inplace=True)
                      
    if dtype is not None:
        if isinstance(dtype, dict):
            for key, ty in dtype.items():
                if not isinstance(key, str):
                    key = df.columns[key]
                if ty == 'numeric':
                    df[key] = pd.to_numeric(df[key], errors='coerce')
                else:
                    df[key] = pd.to_numeric(df[key], downcast=ty, errors='coerce')
                    # df[key] = df[key].astype(ty)
        else:
            for k, ty in enumerate(dtype):
                key = df.columns[k]
                if ty == 'numeric':
                    df[key] = pd.to_numeric(df[key], errors='coerce')
                else:
                    df[key] = pd.to_numeric(df[key], downcast=ty, errors='coerce')
                    # df[key] = df[key].astype(ty)  
    return df

def get_corrected(param, station, translate=True, json=False):
    # validate input weather parameter (param)
    param = get_param_value(param)
    
    # create the API adress
    adr = api_endpoints.ADR_CORRECTED
    adr_full = adr.format(parameter = param, station = station)  
    print(adr_full)
    
    # download the csv data
    if param in [1, 26, 27, 39]: #[TemperaturePast1h]        
        k_value = 2        
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})      
    elif param in [2, 19, 20]: #[TemperaturePast24h, TemperatureMinPast24h, TemperatureMaxPast24h]        
        k_value = 3
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2], dtype={k_value:'numeric'})  
        
    elif param in [3,4,21]: #[Windspeed, WindDirection, WindGust]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
    
    elif param in [5, 23]: #[PrecipPast24hAt06, PrecipPastMonth]        
        k_value = 3
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2], dtype={k_value:'numeric'})  
        
    elif param in [6]: #[Humidity]
        k_value = 2    
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        

    elif param in [7]: #[PrecioPast1h]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
        
    elif param in [8]: #[SnowDepthPast24h]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
    
    elif param in [9, 12, 13]: #[Pressure, Visibility, CurrentWeather]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
    
    elif param in [16, 28, 29, 30, 31, 32, 33, 36]: #[ CloudCover]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
    elif param in [18]: #[PrecipTypePast24h] 
        k_value = 3        
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2])
    
        
    elif param in [17]: #[PrecipPast12h] 
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'])
        
    elif param in [40]: #[GroundCondition]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
    
    else:
        k_value = 3
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2], dtype={k_value:'numeric'})

  
    # Rename columns to english
    if df.shape[0]>0 and translate:
        columns = {
            'Från Datum Tid (UTC)' : 'From Date (UTC)',
            'Till Datum Tid (UTC)' : 'To Date (UTC)',
            'Representativt dygn' : 'Date',
            'Datum (UTC)' : 'Date (UTC)',
            'Datum' : 'Date',
            'Kvalitet' : 'Quality'
            }
        # if k_value==3:
        #     columns[df.columns[0]] = 'From Date (UTC)'
        #     columns[df.columns[1]] = 'To Date (UTC)'    
        #     columns[df.columns[2]] = 'Date'
        # elif k_value==2:
        #     columns[df.columns[0]] = 'Date (UTC)'
        #     columns[df.columns[1]] = 'Date' 
        columns[df.columns[k_value]] = 'Value'
        # columns[df.columns[k_value+1]] = 'Quality'
        df.rename(columns = columns, inplace=True)
        
    return df


def get_latest_months(param, station):
    # validate input weather parameter (param)
    param = get_param_value(param)    
    # create the API adress
    adr = api_endpoints.ADR_LATEST_MONTHS
    adr_full = adr.format(parameter = param, station = station)    
    # print(adr_full)
    
    # initiate the call
    response = requests.get(adr_full)    
    # try to get the json data (exceptions will be catched later)    
    df = pd.DataFrame(response.json()['value'])
    
    df.rename(columns = {'Value':'value'}, inplace=True)
    
    if param in [5]: #PrecipPast24hAt06
        date_cols = ['from', 'to', 'ref']
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


def get_values(param, station, ts=None, time_period=None, idx='Date', col='Value', check_station=False, direction=None):
    # validate input weather parameter (param)
    parameter_id = get_param_value(param)
    
    if check_station:
        # Also check if parameter is available for input weather station (station)
        if isin_station(parameter_id, station):
           print('Paramater not avaiable for selected station') 
        
    # Download corrected historical data (last 3 months not available)
    data = get_corrected(parameter_id, station, json=True)
    
    # if timestamp in input filter data based on timestamp and time period
    # idx specified index column and col data column
    if ts is not None:
        values = helpers.filter_time(data, ts, time_period, idx=idx, col=col, direction=direction)
    else:
        values = data.set_index(idx)[col]
        
    return values
