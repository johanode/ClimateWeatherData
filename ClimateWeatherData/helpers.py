import datetime
# import sys
# import logging
import json
import requests
import pandas as pd
import csv


climate_weather_parameters = {
    'temperature' : [
        'TemperatureMeanPastMonth',    
        'TemperatureMaxPast24h',
        'TemperatureMinPast24h',
        'TemperaturePast24h'
        ],
    'precipitation' : [
        'PrecipPast24hAt06',
        'PrecipTypePast24h'
        ],
    'wind' : [
        'WindSpeed',
        'WindGust'
        ]
    }
climate_weather_parameters['combination'] = climate_weather_parameters['temperature'] + climate_weather_parameters['precipitation']

# functions
def api_return_data(adr):
    # initiate the call
    req_obj = requests.get(adr)
    # try to get the json data (exceptions will be catched later)
    json_data = req_obj.json()
    return json_data

def validatestring(inputStr, validStrings, only_forward=False):
    # matchedStr = validatestring(inputStr,validStrings) 
    # checks the validity of inputStr against validStrings. 
    # The text is valid if it is an unambiguous, 
    # case-insensitive match to any element in validStrings.
    
    outputStrings = set()
    checkStr = inputStr.lower()
    validStrings = set(validStrings)
    compareStrings = [x.lower() for x in validStrings]
    for compareStr, validStr in zip(compareStrings, validStrings):
        if checkStr == compareStr:
            outputStrings = {validStr}
            break
        elif only_forward:
            if compareStr.startswith(checkStr) or checkStr.startswith(compareStr):
                outputStrings.update({validStr})               
        # elif compareStr.startswith(checkStr) or compareStr.endswith(checkStr): 
            # outputStrings.update({validStr})
        elif checkStr in compareStr or compareStr in checkStr:
            outputStrings.update({validStr})
            
    
    if len(outputStrings)==0:
        raise ValueError('The input did not match any of the valid values.')
    elif len(outputStrings)>1:
        raise ValueError('The input matched more than one valid value.')
     
    return outputStrings.pop()

def get_season(ts):
    # Define month for the seasons
    s1 = [12, 1, 2]
    s2 = [3, 4, 5]
    s3 = [6, 7, 8]
    s4 = [9, 10, 11]

    m = []
    for s in [s1, s2, s3, s4]:
        if ts.month in s:
            m = s
            break
    return m


def get_climate_parameters(parameter_type='all'):
    """
    Returns the list of parameters based on the specified type.
    
    :param parameter_type: Type of climate parameter ('temperature', 'precipitation', 'wind', 'combination', 'all').
                           If 'all', it includes all climate parameters.
    :return: A list of climate parameter strings.
    """
    if parameter_type.lower() == 'all':
        # Return all climate parameters
        parameters = []
        for param_type in climate_weather_parameters:
            parameters += climate_weather_parameters[param_type]
    else:
        # Validate and return specific type of parameters
        ty = validatestring(parameter_type, climate_weather_parameters.keys())
        parameters = climate_weather_parameters[ty]
    
    return list(set(parameters))  # Return unique parameters


def get_filter(ts, time_period):
    """
    Returns the time range in ISO format to be used for filtering a DataFrame's time index.
    For 'year', 'month', and 'season', returns a simplified filter like '2024', '2024-09', or a seasonal range.

    Parameters:
    - ts: A tuple containing the start and end timestamps (already processed).
    - time_period: The period for which the range should be formatted ('d', 'w', 'm', 's', 'y') or ('day', 'week', 'month', 'season', 'year').

    Returns:
    - time_filter: A single string or tuple of (start_time_iso, end_time_iso) in ISO format.
    """

    # Shorthand for 'day', 'week', 'month', 'season', 'year'
    shorthand_map = {'d': 'day', 'w': 'week', 'm': 'month', 's': 'season', 'y': 'year'}
    
    # Map the shorthand to the full word
    if time_period in shorthand_map:
        time_period = shorthand_map[time_period]

    # For 'year', return just the year
    if time_period == 'year':
        return (str(ts[0].year),)
    
    # For 'month', return just the year and month
    if time_period == 'month':
        return (ts[0].strftime('%Y-%m'),)
    
    # For 'day', return the full date
    if time_period == 'day':
        return (ts[0].strftime('%Y-%m-%d'),)

    # For 'season' or other ranges, return the range in ISO format
    return (ts[0].isoformat(), ts[1].isoformat()) if len(ts) > 1 else (ts[0].isoformat(),)



def get_time_range(ts, time_period):
    """
    Returns the start and end of a date range based on the provided time period and timestamp.
    Allows for flexible time_period inputs like '-1d', '2w', '48h', etc., using pd.DateOffset-style inputs.
    Also supports shorthand inputs for 'day' ('d'), 'week' ('w'), 'month' ('m'), 'season' ('s'), and 'year' ('y').
    
    Parameters:
    - ts: The starting timestamp (can be a pd.Timestamp, datetime, or string).
    - time_period: A period filter ('d', 'w', 'm', 's', 'y' or pd.DateOffset-style string like '48h', '-1d').
    
    Returns:
    - A tuple (start_ts, end_ts) of pd.Timestamp objects representing the start and end of the range.
    """
    
    # Shorthand for 'day', 'week', 'month', 'season', 'year'
    shorthand_map = {'d': 'day', 'w': 'week', 'm': 'month', 's': 'season', 'y': 'year'}

    # Check if the time period is shorthand and map to the corresponding full word
    if isinstance(time_period, str) and time_period in shorthand_map:
        time_period = shorthand_map[time_period]
    
    # Handle direct time offsets like '48h', '-2w', etc.
    try:
        if isinstance(time_period, str) and not time_period.isalpha():
            offset = pd.to_timedelta(time_period)
            if time_period.startswith('-'):
                start_ts = ts + offset
                end_ts = ts
            else:
                start_ts = ts
                end_ts = ts + offset
            return start_ts, end_ts
    except ValueError:
        raise ValueError(f"Invalid time_period format: {time_period}")
    
    # Handle standard time periods like 'day', 'week', 'month', etc.
    if time_period == 'day':
        start_ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)
        end_ts = ts.replace(hour=23, minute=59, second=59, microsecond=999999)

    elif time_period == 'week':
        start_ts = ts - pd.DateOffset(days=ts.weekday())  # Start of week (Monday)
        end_ts = start_ts + pd.DateOffset(days=6)         # End of week (Sunday)
        start_ts = start_ts.replace(hour=0, minute=0, second=0, microsecond=0)
        end_ts = end_ts.replace(hour=23, minute=59, second=59, microsecond=999999)

    elif time_period == 'month':
        start_ts = ts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = start_ts + pd.DateOffset(months=1)
        end_ts = next_month.replace(day=1) - pd.Timedelta(microseconds=1)

    elif time_period == 'season':
        m = get_season(ts)
        if 12 in m:
            start_ts = ts.replace(year=ts.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_ts = ts.replace(month=m[0], day=1, hour=0, minute=0, second=0, microsecond=0)
        end_ts = ts.replace(month=m[-1], day=1) + pd.DateOffset(months=1) - pd.Timedelta(microseconds=1)

    elif time_period == 'year':
        start_ts = ts.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_ts = ts.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

    else:
        raise ValueError(f"Invalid time period: {time_period}")

    return start_ts, end_ts



def get_types(cat):
    PrecitipationTypes = ['snowfall',
                'regn',
                'duggregn',
                'regnskurar',
                'kornsnö',
                'snöblandat regn',
                'snöbyar',
                'Obestämd nederbördstyp',
                'isnålar',
                'underkyld nederbörd',
                'iskorn',
                'småhagel',
                'byar av snöblandat regn',
                'snöhagel',
                'ishagel']
    
    if cat.lower()=='rain':
        return ['regn', 'duggregn', 'regnskurar']
    elif cat.lower()=='snow':
        return ['snowfall', 'kornsnö', 'snöbyar', 'snöhagel']
    elif cat.lower()=='snowslush':
        return ['snöblandat regn', 'byar av snöblandat regn']
    elif cat.lower()=='supercooledrain':
        return ['underkyld nederbörd']
    else: 
        return []
    
def download_and_parse_csv(adr_full, delimiter=';', usecols=None):
    response = requests.get(adr_full).text
    lines = response.splitlines()
    
    # Find header row
    header_row = 8
    for k, line in enumerate(lines):
        if k >= header_row and 'Datum' in line:
            header_row = k
            break
    
    skip_rows = header_row + 1
    cols = lines[header_row].split(delimiter)
    
    # Filter columns if usecols is specified
    if usecols is not None:
        cols = [col for k, col in enumerate(cols) if k in usecols or col in usecols]
    
    d = csv.DictReader(lines[skip_rows:], delimiter=delimiter, fieldnames=cols)
    df = pd.DataFrame(data=list(d), columns=cols)
    
    return df

def parse_dates_columns(df, parse_dates, keep_date_col=True):
    """
    Parse date columns in the DataFrame.
    
    :param df: The DataFrame to modify.
    :param parse_dates: List, dictionary, or index specifying the columns to parse as dates.
    :param keep_date_col: Whether to keep the original date columns after parsing.
    """
    # Handle case where parse_dates is a dictionary
    if isinstance(parse_dates, dict):
        parse_dates = parse_dates.items()
    
    for parse_date in parse_dates:
        if isinstance(parse_date, tuple):
            # When it's a dictionary-like item
            result = parse_date[0]
            parse_date = parse_date[1]
        elif isinstance(parse_date, list):
            result = '_'.join(parse_date)
        elif isinstance(parse_date, int):
            result = df.columns[parse_date]
        else:
            result = parse_date

        # If it's numeric, translate indices to column names
        if isinstance(parse_date, list):
            # Handle list of column indices/names for concatenating
            parse_date = [df.columns[col] if isinstance(col, int) else col for col in parse_date]
            s = pd.to_datetime(df[parse_date[0]].str.cat(df[parse_date[1]], sep=' '))
        elif isinstance(parse_date, int):
            # Handle individual numeric index
            col_name = df.columns[parse_date]
            s = pd.to_datetime(df[col_name])
        else:
            # Handle column name or list of names
            s = pd.to_datetime(df[parse_date])

        # Insert the parsed date into the DataFrame
        df[result] = s

        # Optionally drop the original date columns
        if not keep_date_col:
            if isinstance(parse_date, str):
                parse_date = [parse_date]
            for col in parse_date:
                if isinstance(keep_date_col, str):
                    if col != keep_date_col:
                        df.drop(labels=col, axis=1, inplace=True)
                elif isinstance(keep_date_col, list):
                    if col not in keep_date_col:
                        df.drop(labels=col, axis=1, inplace=True)
                else:
                    df.drop(labels=col, axis=1, inplace=True)

    return df


def convert_columns_to_dtype(df, dtype):
    """
    Convert columns to a specific data type.
    """
    if isinstance(dtype, dict):
        for key, ty in dtype.items():
            if not isinstance(key, str):
                key = df.columns[key]
            df[key] = pd.to_numeric(df[key], errors='coerce' if ty == 'numeric' else None)
    return df

def rename_columns_to_english(df, k_value, translate=True):
    """
    Rename the columns to English for easier use.
    """
    if not translate:
        return df
    
    columns = {
        'Från Datum Tid (UTC)': 'From Date (UTC)',
        'Till Datum Tid (UTC)': 'To Date (UTC)',
        'Representativt dygn': 'Date',
        'Datum (UTC)': 'Date (UTC)',
        'Datum': 'Date',
        'Kvalitet': 'Quality'
    }
    columns[df.columns[k_value]] = 'Value'
    df.rename(columns=columns, inplace=True)
    
    return df

def read_csv(adr_full, delimiter=';', usecols=None, parse_dates=None, keep_date_col=True, dtype=None):
    # Download and parse CSV
    df = download_and_parse_csv(adr_full, delimiter=delimiter, usecols=usecols)
    
    # Parse date columns if specified
    if parse_dates is not None:
        df = parse_dates_columns(df, parse_dates, keep_date_col=keep_date_col)
    
    # Convert columns to the appropriate data type
    if dtype is not None:
        df = convert_columns_to_dtype(df, dtype)
    
    return df

   

def format_ts(ts, isoformat=False, time_period=None):
    """
    Formats a timestamp (ts) into both a datetime object and, optionally, an ISO format string.
    If a time period is provided, converts the timestamp into a date range based on the period.
    
    Parameters:
    - ts: The timestamp(s) to format (can be a single date, a tuple for a range, or a pd.DatetimeIndex).
    - isoformat: If True, returns the timestamp(s) in ISO format.
    - time_period: Optional, a period filter ('y', 'm', 's', etc.) for year, month, or season.   
    
    Returns:
    - Tuple of (datetime_object_start, datetime_object_end) or (ISO_string_start, ISO_string_end).
      If it's a single date, both will be returned as (ts,) or (ts.isoformat(),).
    """
    # Ensure ts is in datetime format
    if isinstance(ts, str):
        ts = (pd.to_datetime(ts),)
    elif isinstance(ts, (list, tuple)):
        ts = tuple(pd.to_datetime(t) for t in ts)
    elif isinstance(ts, pd.DatetimeIndex):
        # Handle pandas DatetimeIndex
        ts = (ts[0], ts[1])
    else:
        ts = (pd.to_datetime(ts),)

    # Handle the time_period if provided
    if time_period is not None:        
        ts_for_filter = ts[0]  # Use the first date for filtering
        ts = get_time_range(ts_for_filter, time_period)        

    # Convert to ISO format if requested
    if isoformat:
        return tuple(t.isoformat() for t in ts)
    
    return ts



def query_time_range(df, ts, idx):
    """
    Constructs and applies a query for time ranges when direct timestamp lookup fails.
    """
    i1 = df.columns.str.startswith('From Date')
    i2 = df.columns.str.startswith('To Date')

    if i1.any() and i2.any():
        idx1 = df.columns[i1.argmax()]
        idx2 = df.columns[i2.argmax()]

        if len(ts) == 1:
            qrstr = "`{0}` <= '{2}' and `{1}` >= '{2}'".format(idx1, idx2, ts[0])
        else:
            qrstr = "`{0}` <= '{1}' and `{2}` >= '{3}'".format(idx1, ts[0], idx2, ts[1])
    elif len(ts) == 1:
        qrstr = "{0} == '{1}'".format(idx, ts[0])
    else:
        qrstr = "`{0}` >= '{1}' and `{0}` <= '{2}'".format(idx, ts[0], ts[1])

    return df.query(qrstr)


def filter_time(df, ts, time_period, idx, col=None):
    """
    Filters data in a DataFrame based on a timestamp (ts) and optionally a time period.
    
    Parameters:
    - df: The DataFrame to filter.
    - ts: The timestamp or range of timestamps to filter.
    - time_period: Optional time period ('day', 'month', etc.).
    - idx: The column to use for filtering (e.g., 'Date').
    - col: Optional. The column to return after filtering.
    
    Returns:
    - The filtered column (as a Series) or DataFrame.
    """
    # Convert ts into the appropriate time filter (ISO format or range)
    time_filter = get_filter(ts, time_period)

    # Try filtering the DataFrame using the time filter
    try:
        if len(time_filter) == 1:
            # For a single timestamp
            filtered_data = df.set_index(idx).loc[time_filter[0]]
        else:
            # For a timestamp range
            filtered_data = df.set_index(idx).loc[time_filter[0]:time_filter[1]]
    except KeyError:
        # If direct timestamp lookup fails, query the range using broader date columns if available
        filtered_data = query_time_range(df, time_filter, idx)
    
    # Ensure that the filtered result is always a DataFrame, even if it's a single row
    if isinstance(filtered_data, pd.Series):
        filtered_data = filtered_data.to_frame().T

    # If a specific column is requested and exists in the data, return it as a Series
    if col is not None:
        if col in filtered_data.columns:
            return filtered_data[col]
        else:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")

    # Return the filtered DataFrame
    return filtered_data
        
    
def get_parameters(return_format=None):
    # See https://opendata.smhi.se/apidocs/metobs/parameter.html
    # Thanks also to https://github.com/LasseRegin/smhi-open-data
    
    # with open('parameters.json', encoding='utf-8') as fp:
    #     parameters = json.load(fp)
    
    parameters = [
        {'label' : 'TemperaturePast1h', 'key' : 1          , 'name' : 'Lufttemperatur'                        , 'Note' : 'Momentanvärde, 1 gång/tim'},
        {'label' : 'TemperaturePast24h', 'key' : 2         , 'name' : 'Lufttemperatur'                        , 'Note' : 'Medelvärde 1 dygn, 1 gång/dygn, kl 00'},
        {'label' : 'WindDirection', 'key' : 3              , 'name' : 'Vindriktning'                          , 'Note' : 'Medelvärde 10 min, 1 gång/tim'},
        {'label' : 'WindSpeed', 'key' : 4                  , 'name' : 'Vindhastighet'	                      , 'Note' : '  Medelvärde 10 min, 1 gång/tim'},
        {'label' : 'PrecipPast24hAt06', 'key' : 5          , 'name' : 'Nederbördsmängd'                       , 'Note' : 'Summa 1 dygn, 1 gång/dygn, kl 06'},
        {'label' : 'Humidity', 'key' : 6                   , 'name' : 'Relativ Luftfuktighet'	              , 'Note' : 'Momentanvärde, 1 gång/tim'},
        {'label' : 'PrecipPast1h', 'key' : 7               , 'name' : 'Nederbördsmängd'                       , 'Note' : 'Summa 1 timme, 1 gång/tim'},
        {'label' : 'SnowDepthPast24h', 'key' : 8           , 'name' : 'Snödjup'                               , 'Note' : 'Momentanvärde, 1 gång/dygn, kl 06'},
        {'label' : 'Pressure', 'key' : 9                   , 'name' : 'Lufttryck reducerat havsytans nivå'    , 'Note' : 'Vid havsytans nivå, momentanvärde, 1 gång/tim'},
        {'label' : 'SunLast1h', 'key' : 10                 , 'name' : 'Solskenstid'                           , 'Note' : 'Summa 1 timme, 1 gång/tim'},
        {'label' : 'RadiaGlob', 'key' : 11                 , 'name' : 'Global Irradians (svenska stationer)'  , 'Note' : 'Medelvärde 1 timme, 1 gång/tim'},
        {'label' : 'Visibility', 'key' : 12                , 'name' : 'Sikt'                                  , 'Note' : 'Momentanvärde, 1 gång/tim'},
        {'label' : 'CurrentWeather', 'key' : 13            , 'name' : 'Rådande väder'                         , 'Note' : 'Momentanvärde, 1 gång/tim resp 8 gånger/dygn'},
        {'label' : 'PrecipPast15m', 'key' : 14             , 'name' : 'Nederbördsmängd'                       , 'Note' : 'Summa 15 min, 4 gånger/tim'},
        {'label' : 'PrecipMaxPast15m', 'key' : 15          , 'name' : 'Nederbördsintensitet'                  , 'Note' : 'Max under 15 min, 4 gånger/tim'},
        {'label' : 'CloudCover', 'key' : 16                , 'name' : 'Total molnmängd'                       , 'Note' : 'Momentanvärde, 1 gång/tim'},
        {'label' : 'PrecipPast12h', 'key' : 17             , 'name' : 'Nederbörd'                             , 'Note' : '2 gånger/dygn, kl 06 och 18'},
        {'label' : 'PrecipTypePast24h', 'key' : 18         , 'name' : 'Typ av nederbörd'                      , 'Note' : '4 gång/dygn'},
        {'label' : 'TemperatureMinPast24h', 'key' : 19     , 'name' : 'Lufttemperatur'                        , 'Note' : 'Min, 1 gång per dygn'},
        {'label' : 'TemperatureMaxPast24h', 'key' : 20     , 'name' : 'Lufttemperatur'                        , 'Note' : 'Max, 1 gång per dygn'},
        {'label' : 'WindGust', 'key' : 21             , 'name' : 'Byvind'                                , 'Note' : 'Max, 1 gång/tim'},
        {'label' : 'TemperatureMeanPastMonth', 'key' : 22  , 'name' : 'Lufttemperatur'                        , 'Note' : 'Medel, 1 gång per månad'},
        {'label' : 'PrecipPastMonth', 'key' : 23           , 'name' : 'Nederbördsmängd'                       , 'Note' : 'Summa, 1 gång per månad'},
        {'label' : 'LongwaveIrradians', 'key' : 24         , 'name' : 'Långvågs-Irradians'                    , 'Note' : 'Långvågsstrålning, medel 1 timme, varje timme'},
        {'label' : 'WindSpeedMaxMeanPast3h', 'key' : 25    , 'name' : 'Max av MedelVindhastighet'             , 'Note' : 'Maximum av medelvärde 10 min, under 3 timmar,...'},
        {'label' : 'TemperatureMinPast12h', 'key' : 26     , 'name' : 'Lufttemperatur'                        , 'Note' : 'Min, 2 gånger per dygn, kl 06 och 18'},
        {'label' : 'TemperatureMaxPast12h', 'key' : 27	   , 'name' : 'Lufttemperatur'                        , 'Note' : 'Max, 2 gånger per dygn, kl 06 och 18'},
        {'label' : 'CloudLayerLowest', 'key' : 28          , 'name' : 'Molnbas'                               , 'Note' : 'Lägsta molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudAmountLowest', 'key' : 29         , 'name' : 'Molnmängd'                             , 'Note' : 'Lägsta molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudLayerOther', 'key' : 30           , 'name' : 'Molnbas'                               , 'Note' : 'Andra molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudAmountOther', 'key' : 31          , 'name' : 'Molnmängd'                             , 'Note' : 'Andra molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudLayer3rd', 'key' : 32             , 'name' : 'Molnbas'                               , 'Note' : 'Tredje molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudAmount3rd', 'key' : 33            , 'name' : 'Molnmängd'                             , 'Note' : 'Tredje molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudLayer4th', 'key' : 34             , 'name' : 'Molnbas'                               , 'Note' : 'Fjärde molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudAmount4th', 'key' : 35            , 'name' : 'Molnmängd'                             , 'Note' : 'Fjärde molnlager, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudStorageLowest', 'key' : 36        , 'name' : 'Molnbas'                               , 'Note' : 'Lägsta molnbas, momentanvärde, 1 gång/tim'},
        {'label' : 'CloudStorageLowestMin', 'key' : 37     , 'name' : 'Molnbas'                               , 'Note' : 'Lägsta molnbas, min under 15 min, 1 gång/tim'},
        {'label' : 'PrecipIntensityMaxMeanPast15m', 'key' : 38, 'name' : 'Nederbördsintensitet'               , 'Note' : 'Max av medel under 15 min, 4 gånger/tim'},
        {'label' : 'TemperatureDew', 'key' : 39            , 'name' : 'Daggpunktstemperatur'                  , 'Note' : 'Momentanvärde, 1 gång/tim'},
        {'label' : 'GroundCondition', 'key' : 40           , 'name' : 'Markens tillstånd'                     , 'Note' : 'Momentanvärde, 1 gång/dygn, kl 06'},
        ]
    
    if return_format == 'df':
        return pd.DataFrame(parameters)
    else:
        return parameters

def get_indicators(return_format=None):
    with open('indicators.json', encoding='utf-8') as fp:
        indicators = json.load(fp)
    if return_format == 'df':
        return pd.DataFrame(indicators)
    else:
        return indicators