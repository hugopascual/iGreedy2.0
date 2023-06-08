#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# folders paths
__DATASETS_PATH = "datasets/"

# Countries sets
COUNTRIES_SETS_PATH = __DATASETS_PATH + "countries_sets/"
ALL_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH + "all_countries.json"
EU_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH + "EU_countries.json"
EEE_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH + "EEE_countries.json"
NORTH_CENTRAL_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH + \
                                    "North-Central_countries.json"
ADEQUATE_INTERNATIONAL_TRANSFER_COUNTRIES_FILE_PATH = \
    COUNTRIES_SETS_PATH + "adequate_international_transfer_countries.json"
AREA_OF_INTEREST_FILEPATH = NORTH_CENTRAL_COUNTRIES_FILE_PATH
# AREA_OF_INTEREST_FILEPATH = ALL_COUNTRIES_FILE_PATH

# Ground Truth
__GROUND_TRUTH_PATH = __DATASETS_PATH + "ground-truth/"
ROOT_SERVERS_PATH = __GROUND_TRUTH_PATH + "root_servers/"
CLOUDFARE_PATH = __GROUND_TRUTH_PATH + "cloudfare/"
GROUND_TRUTH_VALIDATIONS_PATH = \
    __GROUND_TRUTH_PATH + "groundtruth_validations/"
GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH = \
    GROUND_TRUTH_VALIDATIONS_PATH + "campaigns/"
GT_VALIDATIONS_STATISTICS = \
    GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH + "statistics/"

# Measurements
MEASUREMENTS_PATH = __DATASETS_PATH + "measurements/"
MEASUREMENTS_CAMPAIGNS_PATH = MEASUREMENTS_PATH + "campaigns/"

# Hunter Measurements
HUNTER_MEASUREMENTS_PATH = __DATASETS_PATH + "hunter_measurements/"
HUNTER_MEASUREMENTS_CAMPAIGNS_PATH = HUNTER_MEASUREMENTS_PATH + "campaigns/"
HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH = \
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH + "statistics/"

# Results
RESULTS_PATH = __DATASETS_PATH + "results/"
RESULTS_CAMPAIGNS_PATH = RESULTS_PATH + "campaigns/"

# Probes
PROBES_SETS_PATH = __DATASETS_PATH + "probes_sets/"
DEFAULT_PROBES_PATH = PROBES_SETS_PATH + "WW_10.json"

# Metrics comparison
METRICS_CSV_PATH = __DATASETS_PATH + "ploted_metrics_csv/"

# Alone files
AIRPORTS_INFO_FILEPATH = __DATASETS_PATH + "airports.csv"
KEY_FILEPATH = __DATASETS_PATH + "key.json"
COUNTRY_BORDERS_GEOJSON_FILEPATH = \
    __DATASETS_PATH + \
    "UIA_Latitude_Longitude_Graticules_and_World_Countries_Boundaries.geojson"
VERLOC_APROX_PATH = __DATASETS_PATH + "verloc_aprox.json"
VERLOC_GAP = 5

###############################################################################

# URLs
ROOT_SERVERS_URL = "https://root-servers.org/root/"
RIPE_ATLAS_API_BASE_URL = "https://atlas.ripe.net/api/v2/"
RIPE_ATLAS_MEASUREMENTS_BASE_URL = RIPE_ATLAS_API_BASE_URL + "measurements/"
RIPE_ATLAS_PROBES_BASE_URL = RIPE_ATLAS_API_BASE_URL + "probes/"

# Others
ROOT_SERVERS_NAMES = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"
]
ROOT_SERVERS = {
    "198.41.0.4": "root_servers_A.json",
    "199.9.14.201": "root_servers_B.json",
    "192.33.4.12": "root_servers_C.json",
    "199.7.91.13": "root_servers_D.json",
    "192.203.230.10": "root_servers_E.json",
    "192.5.5.241": "root_servers_F.json",
    "192.112.36.4": "root_servers_G.json",
    "198.97.190.53": "root_servers_H.json",
    "192.36.148.17": "root_servers_I.json",
    "192.58.128.30": "root_servers_J.json",
    "193.0.14.129": "root_servers_K.json",
    "199.7.83.42": "root_servers_L.json",
    "202.12.27.33": "root_servers_M.json"
}
CLOUDFARE_IPS = ["104.16.123.96"]
EARTH_RADIUS_KM = 6371
NEAR_CITY_TP_KM = 100

#DISTANCE_FUNCTION_USED = "constant_1.52"
DISTANCE_FUNCTION_USED = "verloc_aprox"
FIBER_RI = 1/1.52
FACTOR_5000 = 1/2.5
FACTOR_3000 = 1/2.86
FACTOR_2000 = 1/3.3
FACTOR_1000 = 1/4
FACTOR_500 = 1/5.56
SPEED_OF_LIGHT = 299792.458 # km/s

ASCIIART = """
180 150W  120W  90W   60W   30W  000   30E   60E   90E   120E  150E 180
|    |     |     |     |     |    |     |     |     |     |     |     |
+90N-+-----+-----+-----+-----+----+-----+-----+-----+-----+-----+-----+
|          . _..::__:  ,-"-"._       |7       ,     _,.__             |
|  _.___ _ _<_>`!(._`.`-.    /        _._     `_ ,_/  '  '-._.---.-.__|
|.{     " " `-==,',._\{  \  / {)     / _ ">_,-' `                mt-2_|
+ \_.:--.       `._ )`^-. "'      , [_/( G        e      o     __,/-' +
|'"'     \         "    _L       0o_,--'                )     /. (|   |
|         | A  n     y,'          >_.\\._<> 6              _,' /  '   |
|         `. c   s   /          [~/_'` `"(   l     o      <'}  )      |
+30N       \\  a .-.t)          /   `-'"..' `:._        c  _)  '      +
|   `        \  (  `(          /         `:\  > \  ,-^.  /' '         |
|             `._,   ""        |           \`'   \|   ?_)  {\         |
|                `=.---.       `._._ i     ,'     "`  |' ,- '.        |
+000               |a    `-._       |     /          `:`<_|h--._      +
|                  (      l >       .     | ,          `=.__.`-'\     |
|                   `.     /        |     |{|              ,-.,\     .|
|                    |   ,'          \ z / `'            ," a   \     |
+30S                 |  /             |_'                |  __ t/     +
|                    |o|                                 '-'  `-'  i\.|
|                    |/                                        "  n / |
|                    \.          _                              _     |
+60S                            / \   _ __  _   _  ___ __ _ ___| |_   +
|                     ,/       / _ \ | '_ \| | | |/ __/ _` / __| __|  |
|    ,-----"-..?----_/ )      / ___ \| | | | |_| | (_| (_| \__ \ |_ _ |
|.._(                  `----'/_/   \_\_| |_|\__, |\___\__,_|___/\__| -|
+90S-+-----+-----+-----+-----+-----+-----+--___/ /--+-----+-----+-----+
     Based on 1998 Map by Matthew Thomas   |____/ Hacked on 2015 by 8^/  
"""
