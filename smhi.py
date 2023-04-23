#See also https://github.com/thebackman/SMHI

import api_endpoints
import helpers
import requests
import pandas as pd
import json
import logging
import numbers
import csv


def list_stations(param, ts=None):
    # validate parameter input
    param = get_param_value(param)
    
    # create the API adress
    adr = api_endpoints.ADR_PARAMETER
    adr_full = adr.format(parameter=param)

    # send request and get data
    data = helpers.api_return_data(adr_full)

    # -- gather and wrangle the data about avaliable stations
    # convert the JSON data to a pandas DF
    df = pd.DataFrame(data["station"])
    
    # fix the date and time variables into something readable
    for col in ['from', 'to', 'updated']:
        df[col] = pd.to_datetime(df[col], unit="ms")

    if ts is None:
        return(df)
    else:
        # filter based on timestamp
        qrstr = "`from` <= '{0}' and `to` >= '{0}'".format(pd.to_datetime(ts).isoformat())
        return df.query(qrstr)


def list_parameters():
    df_parameters = pd.DataFrame(helpers.get_parameters())
    return df_parameters

def list_indicators():
    df_indicators = pd.DataFrame(helpers.get_indicators())
    return df_indicators

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

def isin_station(parameter, station):
    # Validate paramter input
    parameter_id = get_param_value(parameter)
    
    # check if parameter is available on station
    df_stations = list_stations(parameter_id)
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

def get_corrected(param, station, translate=True):
    # validate input weather parameter (param)
    param = get_param_value(param)
    
    # create the API adress
    adr = api_endpoints.ADR_CORRECTED
    adr_full = adr.format(parameter = param, station = station)
    
    # download the csv data
    if param in [1, 26, 27, 39]: #[TemperaturePast1h]        
        k_value = 2        
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)']], keep_date_col=True)
        # df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        # k_value = 2
        # df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])        
    elif param in [2, 19, 20]: #[TemperaturePast24h, TemperatureMinPast24h, TemperatureMaxPast24h]        
        k_value = 3
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2], dtype={k_value:'numeric'})  
        
        
    elif param in [3,4,21]: #[Windspeed, WindDirection, WindGust]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)']], keep_date_col=True)
        # df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        # k_value = 2
        # df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    
    elif param in [5, 23]: #[PrecipPast24hAt06, PrecipPastMonth]        
        k_value = 3
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2], dtype={k_value:'numeric'})  
        
    elif param in [6]: #[Humidity]
        k_value = 2    
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)']], keep_date_col=True)
        # df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        # k_value = 2
        # df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])

    elif param in [7]: #[PrecioPast1h]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)']], keep_date_col=True)
        # df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        # k_value = 2
        # df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
        
    elif param in [8]: #[SnowDepthPast24h]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)']], keep_date_col=True)
        # df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        # k_value = 2
        # df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    
    elif param in [9, 12, 13]: #[Pressure, Visibility, CurrentWeather]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
    
    elif param in [16, 28, 29, 30, 31, 32, 33, 36]: #[ CloudCover]
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
    elif param in [18]: #[PrecipTypePast24h] 
        k_value = 3
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2])
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3,4], delimiter=";", parse_dates=[0,1,2])
        # k_value = 3        
            
    elif param in [40]: #GroundCondition
        k_value = 2
        df = read_csv(adr_full, usecols=[0,1,2,3], parse_dates={'Datum (UTC)': ['Datum', 'Tid (UTC)']}, keep_date_col=['Datum'], dtype={k_value:'numeric'})
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)']], keep_date_col=True)
        # df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        # k_value = 2
        # df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    else:
        k_value = 3
        df = read_csv(adr_full, usecols=[0,1,2,3,4], parse_dates=[0,1,2], dtype={k_value:'numeric'})
        
        # df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3,4], delimiter=";", parse_dates=[0,1,2])
        # k_value = 3
        # df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
  
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

def get_values(param, station, ts=None, time_period=None, idx='Date', col='Value', check_station=False, direction=None):
    # validate input weather parameter (param)
    parameter_id = get_param_value(param)
    
    if check_station:
        # Also check if parameter is available for input weather station (station)
        if isin_station(parameter_id, station):
           print('Paramater not avaiable for selected station') 
        
    # Download corrected historical data (last 3 months not available)
    data = get_corrected(parameter_id, station)
    
    # if timestamp in input filter data based on timestamp and time period
    # idx specified index column and col data column
    if ts is not None:
        values = helpers.filter_time(data, ts, time_period, idx=idx, col=col, direction=direction)
    else:
        values = data[col]
        
    return values
