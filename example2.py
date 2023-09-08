# -*- coding: utf-8 -*-
"""
Created on Tue May  9 12:22:31 2023

@author: johode
"""

# Import libs
import pandas as pd
import smhi


# Get weather parameters
parameters = smhi.list_parameters()

# Specify time range
ts = ('2018-01-01 00:00', '2023-05-08 23:30')

# Find stations with certain parameter at a certain date
stations = smhi.list_stations('TemperaturePast1h', ts=ts[0])

# Print selected weather station
station = 97120
station_name = stations.set_index('id').loc[station,'name']
print(station_name)

#%% Valid parameters for station
valid_parameters = []
for idx, row in parameters.iterrows():
    param_id = row['key']
    param = row['label']

    # Check if data available for parameter for station
    if smhi.isin_station(param_id, station, ts=ts[0]):
         print('%s (id=%d) is avalable in station %s (id=%d)' % (param, param_id, station_name, station))
         valid_parameters.append(param)
    else:
        print('%s (id=%d) is NOT avalable in station %s (id=%d)' % (param, param_id, station_name, station))        

#%% Get data and save to list
df_list = []
parameter_list = []
for param in valid_parameters:
    param_id = smhi.get_param_value(param)    
    if param in ['TemperaturePast1h']:
        values = smhi.get_values(param_id, station, ts, idx='Date (UTC)', col=None) 
        df = values.reset_index().reindex(columns=['Date', 'Date (UTC)', 'Value', 'Quality'])
        if df['Date (UTC)'].max()<pd.to_datetime(ts[1]):
            values = smhi.get_latest_months(param_id, station)
            values['Date'] = values['Date (UTC)'].dt.date
            df = pd.merge(df, values, on=df.columns.tolist(), how='outer')
        
    elif param in ['PrecipPast12h', 'SnowDepthPast24h']:
        values = smhi.get_values(param_id, station, ts, idx='Date (UTC)', col=None)        
        df = values.reset_index().reindex(columns=['Date', 'Date (UTC)', 'Value', 'Quality'])
        if df['Date (UTC)'].max()<pd.to_datetime(ts[1]):
            values = smhi.get_latest_months(param_id, station)
            values['Date'] = values['Date (UTC)'].dt.date
            df = pd.merge(df, values, on=df.columns.tolist(), how='outer')
        
    elif param in ['PrecipPast24hAt06']:
        values = smhi.get_values(param_id, station, ts, idx='Date', col=None) 
        df = values.reset_index().reindex(columns=['Date', 'From Date (UTC)', 'To Date (UTC)', 'Value', 'Quality'])
        df['Date'] = df['Date'].dt.date
        
        if df['From Date (UTC)'].max()<pd.to_datetime(ts[1]):
            values = smhi.get_latest_months(param_id, station) 
            df = pd.merge(df, values, on=df.columns.tolist(), how='outer')
        
    else:
        values = None
    if values is not None:
        print(param)
        print(df.shape)
        df_list.append(df)
        parameter_list.append(param)
        

#%% Excel
# Create a Pandas Excel writer using XlsxWriter as the 
p = 'C:/Users/johode/Documents/Python Scripts/climaint/'
writer = pd.ExcelWriter(p+f"smhi_{station}.xlsx", engine='xlsxwriter')

# Loop over each series and write to a separate sheet
for sheet_name, df in zip(parameter_list, df_list):            
    df.to_excel(writer, sheet_name=sheet_name, index=False)

# Save the Excel file
writer.save()

