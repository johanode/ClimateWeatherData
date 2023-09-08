# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 22:20:41 2023

@author: johode
"""

# Import libs
import pandas as pd
import smhi
import climate


# Locations
locations = pd.DataFrame([
    ['Boden', 'Bdn', 'Boden', 161940],
    ['Malmö', 'M', 'Malmö A', 52350],
    ['Göteborg', 'G', 'Göteborg A', 71420],
    ['Helsingborg', 'Hb', 'Heslingborg A', 62040],
    ['Stockholm', 'Cst', 'Stockholm-Observatoriekullen', 98210]
    ], columns=['city', 'station_id', 'weatherstation', 'weatherstation_id'])
locations.set_index('city', inplace=True)

# Specify time range
ts = ('2010-01-01', '2022-12-31')

# Get all weather parameters
all_parameters = smhi.list_parameters()
# Get all climate indicators
all_indicators = smhi.list_indicators()

# Daily average temperatures in Boden
ws = locations.at['Boden','weatherstation_id']
temperature = smhi.get_values('TemperaturePast24h' , ws, ts) #idx='Date'

# Zero crossing days per time_period in Stockholm
ws = locations.at['Stockholm','weatherstation_id']
# Time period year, i.e. number of zero crossing days per year
zero_crossings = climate.ZeroCrossingDays(ws, ts, '1y')
# Time period day, i.e. if zero crossing (0 or 1) for each day
zero_crossings = climate.ZeroCrossingDays(ws, ts, '1d')
