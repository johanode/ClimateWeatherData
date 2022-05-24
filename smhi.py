#See also https://github.com/thebackman/SMHI

import api_endpoints
import helpers
import requests
import pandas as pd
import json
import logging
import numbers


def list_stations(param, col=None):
    """ list stations that have a certain wheather parameter """

    # -- API call

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

def get_param_value(parameter, station=None):
    if isinstance(parameter,numbers.Number):
        parameter_id = parameter
    else:
        df_parameters = pd.DataFrame(helpers.get_parameters())
        parameter_id = None
        if parameter in df_parameters['label'].to_list():
            parameter_id = df_parameters.set_index('label').loc[parameter, 'key']
        
    if station is not None:
        valid_stations = list_stations(parameter_id, col='id')
        if not station in valid_stations:
            parameter_id = None
    return parameter_id

def get_time_period(ts, time_period):
    return tuple(helpers.get_filter(ts, time_period))

def get_corrected(param, station, translate=True):
    """ get corrected archive via CSV download """
    
    # -- API call
    
    # create the API adress
    adr = api_endpoints.ADR_CORRECTED
    adr_full = adr.format(parameter = param, station = station)
    
    # download the csv data
    if param in [3,4,21]:
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)']], keep_date_col=True)
        df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        k_value = 2
        df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    elif param in [8]:
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3], delimiter=";", parse_dates=[['Datum', 'Tid (UTC)'],'Datum'], keep_date_col=True)
        df.drop(labels='Tid (UTC)', axis=1, inplace=True)
        # df.iloc[:,1] = df.iloc[:,1]-pd.to_timedelta(1,unit='day')
        k_value = 2
        df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    elif param in [18]:
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3,4], delimiter=";", parse_dates=[1,2,3])
        k_value = 3
    elif param is not None:
        df = pd.read_csv(filepath_or_buffer= adr_full, skiprows= 9, usecols=[0,1,2,3,4], delimiter=";", parse_dates=[1,2,3])
        k_value = 3
        df.iloc[:,k_value] = pd.to_numeric(df.iloc[:,k_value])
    else:
        df = pd.DataFrame()
  
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

def get_values(param, station, ts=None, time_period='day', idx='Date', col='Value'):
    parameter_id = get_param_value(param, station)
    data = get_corrected(parameter_id, station)
    if ts is not None:
        values = helpers.filter_time(data, ts, time_period, idx=idx, col=col)
    else:
        values = data['Values']
    return values
