#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# folders paths
####
__DATASETS_PATH = "datasets/"

COUNTRIES_SETS_PATH = __DATASETS_PATH+"countries_sets/"
ALL_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH+"all_countries.json"
EU_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH+"EU_countries.json"
EEE_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH+"EEE_countries.json"
NORTH_CENTRAL_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH+"North-Central_countries.json"
ADECUATE_INTERNACIONAL_TRANSFERS_COUNTRIES_FILE_PATH = COUNTRIES_SETS_PATH+"adecuate_internacional_trasnfer_countries.json"

__GROUND_TRUTH_PATH = __DATASETS_PATH+"ground-truth/"
ROOT_SERVERS_PATH = __GROUND_TRUTH_PATH+"root_servers/"

PROBES_SETS_PATH = __DATASETS_PATH+"probes_sets/"
DEFAULT_PROBES_PATH = PROBES_SETS_PATH+"WW_10.json"

AIRPORTS_INFO_FILEPATH = __DATASETS_PATH+"airports.csv"
####
MEASUREMENTS_PATH = "measurements/"
CAMPAIGNS_PATH = MEASUREMENTS_PATH+"campaigns/"
####
RESULTS_PATH = "results/"
####

# URLs
ROOT_SERVERS_URL = "https://root-servers.org/root/"

# others
ROOT_SERVERS_NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
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
