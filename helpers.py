
import datetime
import sys
import logging
import json
import requests

# -- logging

FORMAT = '%(asctime)s %(levelname)s: %(module)s: %(funcName)s(): %(message)s'
logging.basicConfig(level=logging.DEBUG, format = FORMAT, filename = "smhi.log", filemode = "w")
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# -- functions

def write_json(json_obj, file_name = 'file.json'):
    """ write a json file to wd/file.json"""
    with open(file_name, 'w') as outfile:
        json.dump(json_obj, outfile)

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
    
    
def parameters():
    # See https://opendata.smhi.se/apidocs/metobs/parameter.html
    # Thanks also to https://github.com/LasseRegin/smhi-open-data
    return [
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

def indicators():
    return [{'Name':"TAS","Climate parameter":"Temperatur","Climate index":"Medeltemperatur","Time period":"s, y"},
            {'Name':"TX","Climate parameter":"Temperatur","Climate index":"Dygnsmaxtemperatur","Time period":"m, s, y"},
            {'Name':"TN","Climate parameter":"Temperatur","Climate index":"Dygnsminimitemperatur","Time period":"m, s, y"},
            {'Name':"DTR","Climate parameter":"Temperatur","Climate index":"Dygnsamplitud (varmast minus kallast)","Time period":"m"},
            {'Name':"WarmDays","Climate parameter":"Temperatur","Climate index":"Varma dagar\/högsommardagar (Maxtemperatur >20 ºC) *","Time period":"s, y"},
            {'Name':"ConWarmDays","Climate parameter":"Temperatur","Climate index":"Värmebölja (dagar i följd med maxtemperatur > 20ºC)","Time period":"y"},
            {'Name':"ZeroCrossingDays","Climate parameter":"Temperatur","Climate index":"Nollgenomgångar (Antal dagar med högsta temp > 0ºC och lägsta temp < 0ºC)","Time period":"s"},
            {'Name':"VegSeasonDayEnd-5","Climate parameter":"Temperatur","Climate index":"Vegetationsperiodens slut (sista dag i sammanhängande 4-dags period med medeltemp > 5ºC","Time period":"y"},
            {'Name':"VegSeasonDayStart-5","Climate parameter":"Temperatur","Climate index":"Vegetationsperiodens början (sista dag i sammanhängande 4-dags period med medeltemp > 5 ºC)","Time period":"y"},
            {'Name':"VegSeasonLentgh-5","Climate parameter":"Temperatur","Climate index":"Vegetationsperiodens längd (medeltemp > 5ºC)","Time period":"y"},
            {'Name':"VegSeasonLentgh-2","Climate parameter":"Temperatur","Climate index":"Vegetationsperiodens längd (medeltemp > 2ºC)","Time period":"y"},
            {'Name':"FrostDays","Climate parameter":"Temperatur","Climate index":"Frostdagar (minimitemperatur < 0ºC )","Time period":"s"},
            {'Name':"ColdDays","Climate parameter":"Temperatur","Climate index":"Kalla dagar (maxtemperatur < -7ºC)","Time period":"y"},
            {'Name':"PR","Climate parameter":"Nederbörd","Climate index":"Summa nederbörd","Time period":"m, s, y"},
            {'Name':"PRRN","Climate parameter":"Nederbörd","Climate index":"Summa regn","Time period":"s, y"},
            {'Name':"PRSN","Climate parameter":"Nederbörd","Climate index":"Summa snö","Time period":"s, y"},
            {'Name':"SuperCooledPR","Climate parameter":"Nederbörd","Climate index":"Underkylt regn","Time period":"y"},
            {'Name':"PR7Dmax","Climate parameter":"Nederbörd","Climate index":"Högsta nederbörd under 7 dagar","Time period":"y"},
            {'Name':"Prmax","Climate parameter":"Nederbörd","Climate index":"Maximal nederbördsintensitet","Time period":"y"},
            {'Name':"PRSNmax","Climate parameter":"Nederbörd","Climate index":"Maximal snöfallsintensitet","Time period":"y"},
            {'Name':"PRgt10Days","Climate parameter":"Nederbörd","Climate index":"Kraftig nederbörd > 10 mm\/dygn","Time period":"s, y"},
            {'Name':"PRgt25Days","Climate parameter":"Nederbörd","Climate index":"Extrem nederbörd > 25 mm\/dygn","Time period":"s, y"},
            {'Name':"DryDays","Climate parameter":"Nederbörd","Climate index":"Torra dagar (med nederbörd < 1 mm)","Time period":"m"},
            {'Name':"LnstDryDays","Climate parameter":"Nederbörd","Climate index":"Längsta torrperiod (med <1 mm\/dag)","Time period":"s"},
            {'Name':"SncDays","Climate parameter":"Snö på marken","Climate index":"Snötäcke","Time period":"y"},
            {'Name':"SNWmax","Climate parameter":"Snö på marken","Climate index":"Maximalt snödjup (räknat som vatteninnehåll)","Time period":"y"},
            {'Name':"SfcWind","Climate parameter":"Vind och densitet","Climate index":"Medelvindhastighet i 10m-nivå","Time period":"s, y"},
            {'Name':"WindGustMax","Climate parameter":"Vind och densitet","Climate index":"Maximal byvind (10m-nivå)","Time period":"y"},
            {'Name':"WindyDays","Climate parameter":"Vind och densitet","Climate index":"Antal dagar med byvind >21 m\/s (10m-nivå)","Time period":"y"},
            {'Name':"ColdRainDays","Climate parameter":"Kombinationsindex","Climate index":"Nederbörd när temperaturen ligger mellan 0.58 och 2 grader","Time period":"y"},
            {'Name':"ColdRainGT10Days","Climate parameter":"Kombinationsindex","Climate index":"Nederbörd ( > 10 mm\/dygn) när temperaturen ligger mellan 0.58 och 2 grader","Time period":"y"},
            {'Name':"ColdRainGT20Days","Climate parameter":"Kombinationsindex","Climate index":"Nederbörd ( > 20 mm\/dygn) när temperaturen ligger mellan 0.58 och 2 grader","Time period":"y"},
            {'Name':"WarmSnowDays","Climate parameter":"Kombinationsindex","Climate index":"Nederbörd när temperaturen ligger mellan -2 och 0.58 grader","Time period":"y"},
            {'Name':"WarmSnowGT10Days","Climate parameter":"Kombinationsindex","Climate index":"Nederbörd (> 10 mm\/dygn) när temperaturen ligger mellan -2 och 0.58 grader","Time period":"y"},
            {'Name':"WarmSnowGT20Days","Climate parameter":"Kombinationsindex","Climate index":"Nederbörd (> 20 mm\/dygn) när temperaturen ligger mellan -2 och 0.58 grader","Time period":"y"},
            {'Name':"ColdPRRNdays","Climate parameter":"Kombinationsindex","Climate index":"Regn när temperaturen är under 2 grader","Time period":"y"},
            {'Name':"ColdPRRNgt10Days","Climate parameter":"Kombinationsindex","Climate index":"Regn ( > 10 mm\/dygn) när temperaturen är under 2 grader","Time period":"y"},
            {'Name':"ColdPRRNgt20Days","Climate parameter":"Kombinationsindex","Climate index":"Regn ( > 20 mm\/dygn) när temperaturen är under 2 grader","Time period":"y"},
            {'Name':"WarmPRSNdays","Climate parameter":"Kombinationsindex","Climate index":"Snö när temperaturen är över -2 grader","Time period":"y"},
            {'Name':"WarmPRSNgt10Days","Climate parameter":"Kombinationsindex","Climate index":"Snö ( > 10 mm\/dygn) när temperaturen är över -2 grader","Time period":"y"},
            {'Name':"WarmPRSNgt20Days","Climate parameter":"Kombinationsindex","Climate index":"Snö ( > 20 mm\/dygn) när temperaturen är över -2 grader","Time period":"y"}]