# -- globals

# Default version used for the SMHI API
DEFAULT_VERSION = "1.0" #latest

# Base version URL
ADR_VERSION = "http://opendata-download-metobs.smhi.se/api/version/1.0.json"

# Base parameter URL (use to list available parameters)
ADR_PARAMETER = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/{parameter}.json"

# Specific station URL for a given parameter
ADR_STATION = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/{parameter}/station/{station}.json"

# Latest months data (default is JSON)
ADR_LATEST_MONTHS = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/{parameter}/station/{station}/period/latest-months/data.json"

# Corrected historical archive data (default format is CSV)
ADR_CORRECTED = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/{parameter}/station/{station}/period/corrected-archive/data.csv"


# -- Functions for dynamic URLs

def get_period_url(parameter, station, period, file_format="json", version=DEFAULT_VERSION):
    """
    Dynamically generates the URL for a given period, parameter, and station.
    
    :param parameter: The weather parameter ID (e.g., 1 for air temperature)
    :param station: The station ID (e.g., 162860 for Luleå-Kallax Flygplats)
    :param period: The period to fetch data for (e.g., 'latest-hour', 'latest-day', 'latest-months')
    :param file_format: The format of the data ('json', 'xml', 'csv')
    :param version: The API version to use (defaults to DEFAULT_VERSION)
    :return: The full API URL for the given period
    """
    base_url = "http://opendata-download-metobs.smhi.se/api/version/{version}/parameter/{parameter}/station/{station}/period/{period}.{file_format}"
    return base_url.format(version=version, parameter=parameter, station=station, period=period, file_format=file_format)


def get_corrected_data_url(parameter, station, file_format="csv", version=DEFAULT_VERSION):
    """
    Dynamically generates the URL for corrected archive data.
    
    :param parameter: The weather parameter ID (e.g., 1 for air temperature)
    :param station: The station ID
    :param file_format: The format of the data ('json', 'xml', 'csv')
    :param version: The API version to use (defaults to DEFAULT_VERSION)
    :return: The full API URL for the corrected archive data
    """
    base_url = "http://opendata-download-metobs.smhi.se/api/version/{version}/parameter/{parameter}/station/{station}/period/corrected-archive/data.{file_format}"
    return base_url.format(version=version, parameter=parameter, station=station, file_format=file_format)


# Example: Dynamic URL for base version endpoint
def get_version_url(version=DEFAULT_VERSION):
    """
    Dynamically generates the URL for the API version metadata.
    
    :param version: The API version to use (defaults to DEFAULT_VERSION)
    :return: The full API URL for the version metadata
    """
    return ADR_VERSION.format(version=version)
