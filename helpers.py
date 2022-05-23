
import datetime
import sys
import logging
import json
import requests


# functions
def api_return_data(adr):
    """ initate API call and return the JSON data """
    # initiate the call
    req_obj = requests.get(adr)
    # try to get the json data (exceptions will be catched later)
    json_data = req_obj.json()
    return json_data

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


def get_filter(ts, time_period):
    if time_period == 'm':
        time_filter = ['%d-%02d' % (ts.year, ts.month)]
    elif time_period == 's':
        m = get_season(ts)
        if 12 in m:
            m1 = '%d-%02d' % (ts.year-1, 12)
        else:
            m1 = '%d-%02d' % (ts.year, m[0])
        m2 = '%d-%02d' % (ts.year, m[-1])
        time_filter = [m1, m2]
    elif time_period == 'y':
        time_filter = [str(ts.year)]
    elif isinstance(ts,datetime.date):
        time_filter = [str(ts)]
    else:
        time_filter = [str(ts.date())]
        
    return time_filter

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
    
def filter_time(df, ts, time_period, idx='Date', col='Value'):
    time_filter = get_filter(ts, time_period)

    if len(time_filter)>=2:
        df_filter = df.set_index(idx).loc[time_filter[0]:time_filter[-1]]
    else:
        df_filter = df.set_index(idx).loc[time_filter[0]]
    if col is not None:
        return df_filter[col]
    else:
        return df_filter
    
    
def get_parameters():
    # See https://opendata.smhi.se/apidocs/metobs/parameter.html
    # Thanks also to https://github.com/LasseRegin/smhi-open-data
    
    # with open('parameters.json') as fp:
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
        {'label' : 'PrecipPast24hAt18', 'key' : 18         , 'name' : 'Nederbörd'                             , 'Note' : '1 gång/dygn, kl 18'},
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
    return parameters

def get_indicators():
    with open('indicators.json') as fp:
        indicators = json.load(fp)
    return indicators