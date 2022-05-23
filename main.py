
# -- import the libs and some reload 

import pandas as pd
import smhi as smhi
import importlib
importlib.reload(smhi)


 
station = 162860
data = pd.read_pickle('data/ofelia_data.pkl')
ts = data.loc[20,'Anmält datum']

# -- listing the parameters that are avaliable

smhi.list_params()

# -- for one parameter, see what stations have it and in what timeframe, lon lat area etc.

# all stations 
df_stations = smhi.list_stations(param = 5)

# list one station
df_stations.loc[df_stations["key"] == "159880"]

# limit the stations further to those that have been online in recent years
df_stations = df_stations.loc[(df_stations["starting"] >= '2000-01-01')]

# take a random sample of stations
df_random = df_stations.sample(n = 10, random_state= 11)
df_random

# TODO:

# limit the stations to within a geographical area
# fix the order of data frame columns so that they match
# add some examples and actually do something with the data


# -- get the actual data

# create a tuple to try out stations
# 97250: not active, no latest months data, only historical
# 158820: active, both latest months and historical data

station = (97250,)
station = (158820,)
stations = (97250, 158820)

# download for station(s)
dict_df = smhi.get_stations(param = 5, station_keys = station)
dict_df = smhi.get_stations(param = 5, station_keys = stations)

# access the data
dict_df["df_latest"]
dict_df["df_corrected"]
