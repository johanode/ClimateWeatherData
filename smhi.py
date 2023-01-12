#See also https://github.com/thebackman/SMHI

import api_endpoints
import helpers
import requests
import pandas as pd
import json
import logging
import numbers


def list_stations(param, col=None):
    # validate parameter input
    param = get_param_value(param)
    
    # create the API adress
    adr = api_endpoints.ADR_PARAMETER
    adr_full = adr.format(parameter=param)

    # send request and get data
    data = helpers.api_return_data(adr_full)

    if col is not None:
        data_list = [s[col] for s in data["station"]]
        return data_list
    else:
        # -- gather and wrangle the data about avaliable stations
        # convert the JSON data to a pandas DF
        df = pd.DataFrame(data["station"])
        
        # fix the date and time variables into something readable
        for col in ['from', 'to', 'updated']:
            df[col] = pd.to_datetime(df[col], unit="ms")

        return(df)


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
    valid_stations = list_stations(parameter_id, col='id')
    
    return station in valid_stations

def get_time_period(ts, time_period):
    return tuple(helpers.get_filter(ts, time_period))

def get_corrected(param, station, translate=True):
    # create the API adress
    adr = api_endpoints.ADR_CORRECTED
    adr_full = adr.format(parameter = param, station = station)
    
    # validate input weather parameter (param)
    param = get_param_value(param)
    
    # download the csv data
    if param in [3,4,21]: #[Windspeed, WindDirection, WindGust]
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)'],'Datum'], keep_date_col=True)
        df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        k_value = 2
        df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    elif param in [8]: #[SnowDepthPast24h]
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)'],'Datum'], keep_date_col=True)
        df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        k_value = 2
        df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    elif param in [18]: #[PrecipTypePast24h] 
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3,4], delimiter=";", parse_dates=[1,2,3])
        k_value = 3
    else:
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3,4], delimiter=";", parse_dates=[1,2,3])
        k_value = 3
        df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
  
    # Rename columns to english
    if df.shape[0]>0 and translate:
        columns = {}
        if k_value==3:
            columns[df.columns[0]] = 'From Date (UTC)'
            columns[df.columns[1]] = 'To Date (UTC)'    
            columns[df.columns[2]] = 'Date'
        elif k_value==2:
            columns[df.columns[0]] = 'Date (UTC)'
            columns[df.columns[1]] = 'Date' 
        columns[df.columns[k_value]] = 'Value'
        columns[df.columns[k_value+1]] = 'Quality'
        df.rename(columns = columns, inplace=True)
        
    # if label is not None:
        # df.rename(columns = {df.columns[k_value] : label}, inplace=True)
        
    return df

def get_values(param, station, ts=None, time_period='day', idx='Date', col='Value', check_station=False, direction=None):
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
        values = data['Values']
        
    return values
