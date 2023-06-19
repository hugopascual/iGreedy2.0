#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import math
import subprocess
import re
import geocoder
import pandas as pd
import requests
import ipinfo
import datetime
from subprocess import run

import shapely
from shapely import (
    Point,
    Polygon
)
from shapely.ops import unary_union
from rtree import index
import plotly.graph_objects as go
from utils.constants import (
    FIBER_RI,
    SPEED_OF_LIGHT,
    EARTH_RADIUS_KM,
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
    VERLOC_GAP,
    VERLOC_APROX_PATH,
    RIPE_ATLAS_MEASUREMENTS_BASE_URL,
    KEY_FILEPATH,
    AREA_OF_INTEREST_FILEPATH,
    GT_VALIDATIONS_STATISTICS,
    CLOUDFARE_IPS,
    ROOT_SERVERS,
    AIRPORTS_INFO_FILEPATH,
    CLOUDFARE_PATH
)
from utils.common_functions import (
    get_distance_from_rtt,
    get_light_factor_from_distance,
    get_time_from_distance,
    json_file_to_dict,
    dict_to_json_file,
    convert_km_radius_to_degrees,
    get_list_files_in_path,
    get_nearest_airport_to_point,
    calculate_hunter_pings_intersection_area,
    get_polygon_from_section,
    get_list_folders_in_path,
    get_country_name
)
from groundtruth import get_gt_instances_locations


def get_ripe_key() -> str:
    return json_file_to_dict(KEY_FILEPATH)["key"]


def make_ripe_measurement(data: dict):
    # Start the measurement and get measurement id
    response = {}
    try:
        response = requests.post(url, json=data).json()
        measurement_id = response["measurements"][0]
        print(measurement_id)
    except Exception as e:
        print(e.__str__())
        print(response)


def get_measurement_results():
    results_measurement_url = \
        RIPE_ATLAS_MEASUREMENTS_BASE_URL + "{}/results".format(
            measurement_id
        )

    print(results_measurement_url)
    response = requests.get(results_measurement_url).json()
    dict_to_json_file(response, "http_petition.json")


url = RIPE_ATLAS_MEASUREMENTS_BASE_URL + "/?key={}".format(get_ripe_key())
traceroute_data = {
    "definitions": [
        {
            "target": "104.16.123.96",
            "description": "HTTP test to 104.16.123.96",
            "type": "http",
            "is_oneoff": True,
            "header_bytes": 2048,
            "af": 4,
        }
    ],
    "probes": [
        {
            "requested": 5,
            "type": "country",
            "value": "NL"
        }
    ]
}
#make_ripe_measurement(data=traceroute_data)

#measurement_id = 55212992
#get_measurement_results()


def some_igreedy_statistics():
    df = pd.read_csv(GT_VALIDATIONS_STATISTICS +
                     "statistics_North-Central_validation_20230410.csv",
                     sep=",")

    df_optimal = df[
        (df["probe_selection"] == "area") &
        (df["probe_set_number"] == 500) &
        (df["distance_function"] == "verloc_aprox") &
        (df["threshold"] == 1) &
        (df["alpha"] == 1)
    ]

    df_optimal = df_optimal[["target", "Accuracy", "Precision", "Recall", "F1", "gt_instances_in_region"]]
    df_optimal.to_csv(GT_VALIDATIONS_STATISTICS + "optimal_params_results.csv",
              sep=",",
              index=False)

    df_second_optimal = df[
        (df["probe_selection"] == "area") &
        (df["probe_set_number"] == 1000) &
        (df["distance_function"] == "constant_1.52") &
        (df["threshold"] == 1) &
        (df["alpha"] == 1)
    ]
    df_second_optimal = df_second_optimal[["target", "Accuracy", "Precision", "Recall", "F1", "gt_instances_in_region"]]
    df_second_optimal.to_csv(GT_VALIDATIONS_STATISTICS + "optimal_second_params_results.csv",
              sep=",",
              index=False)


cloudfare_africa = [
    "ACC", "ALG", "TNR", "CPT", "CMN", "DKR", "DAR", "JIB", "DUR", "GBE",
    "HRE", "JNB", "KGL", "LOS", "LAD", "MPM", "MBA", "NBO", "OUA", "MRU",
    "RUN", "TUN", "FIH", "ORN", "AAE"
]

cloudfare_asia = [
    "AMD", "ALA", "BLR", "BKK", "BWN", "XIY", "BBI", "CEB", "IXC", "CGD",
    "MAA", "CNX", "CGP", "CMB", "DAC", "FUO", "FUK", "FOC", "CAN", "HAK",
    "HAN", "SJW", "SGN", "HKG", "HYD", "ISB", "CGK", "JSR", "TNA", "JHB",
    "KNU", "KHH", "KHI", "KTM", "KHV", "CCU", "KJA", "KUL", "LHE", "PKX",
    "LHW", "LYA", "MFM", "MLE", "MDL", "MNL", "BOM", "NAG", "OKA", "DEL",
    "KIX", "PAT", "PNH", "TAO", "ICN", "SHA", "SIN", "URT", "TPE", "TAS",
    "PBH", "TSN", "NRT", "ULN", "VTE", "WUX", "KHN", 'RGN', 'EVN', 'JOG',
    'CGO', 'CGQ', 'WUH', 'ZGN', "CGY", 'CSX', 'TYN', 'WHU', 'HYN', 'COK',
    'NTG', 'XMN', 'DPS', 'CNN'
]

cloudfare_europe = [
    'AMS', 'ATH', 'BCN', 'BEG', 'TXL', 'BTS', 'BRU', 'OTP', 'BUD', 'KIV',
    'CPH', 'ORK', 'DUB', 'DUS', 'EDI', 'FRA', 'GVA', 'GOT', 'HAM', 'HEL',
    'IST', 'ADB', 'KBP', 'LIS', 'LHR', 'LUX', 'MAD', 'MAN', 'MRS', 'MXP',
    'MSQ', "DME", "MUC", "LCA", "OSL", "PMO", "CDG", "PRG", "KEF", "RIX",
    "FCO", "LED", "SOF", "ARN", "STR", "TLL", "TBS", "SKG", "TIA", "KLD",
    "VIE", "VNO", "WAW", "SVX", "ZAG", "ZHR", "LYS"
]

cloudfare_south_america = [
    "QWJ", "ARI", "ASU", "BEL", "CNF", "BNU", "BOG", "BSB", "EZE", "CFC",
    "VCP", "CCP", "COR", "CGB", "CWB", "FLN", "FOR", "GEO", "GYN", "GUA",
    "GYE", "ITJ", "JOI", "JDO", "LIM", "MAO", "MDE", "NQN", "PTY", "PBM",
    "POA", "PAP", "UIO", "REC", "RAO", "GIG", "SSA", "SJO", "SCL", "SDQ",
    "SJP", "SJK", "JRU", "SDO", "GND", "TGU", "NVT", "UDI", "VIX", "CUR",
    "CAW"
]

cloudfare_middle_east = [
    "AMM", "LLK", "BGW", "GYD", "BSR", "BEY", "DMM", "DOH", "DXB", "EBL",
    "HFA", "JED", "KWI", "BAH", "MCT", "NJF", "XNH", "ZDM", "RUH", "ISU",
    "TLV"
]

cloudfare_north_america = [
    "ABQ", "IAD", "ATL", "DGR", "BOS", "BUF", "YYC", "CLT", "ORD", "CMH",
    "DFW", "DEN", "DTW", "HNL", "IAH", "IND", "JAX", "MCI", "LAS", "LAX",
    "MFE", "MEM", "MEX", "MIA", "MSP", "MGM", "YUL", "BNA", "EWR", "ORF",
    "OMA", "YOW", "PHL", "PHX", "PIT", "PDX", "QRO", "RIC", "SMF", "SLC",
    "SNA", "SJC", "YXE", "SEA", "FSD", "STL", "TLH", "TPA", "YYZ", "YVR",
    "YWG", "SFO", "KIN", "BGR", "AUS", "ABQ", "GDL"

]

cloudfare_oceania = [
    "ADL", "AKL", "BNE", "CBR", "CHC", "GUM", "HBA", "MEL", "NOU", "PER",
    "SYD", "PPT"
]

cloudfare_list_codes = cloudfare_africa + cloudfare_asia + cloudfare_europe + \
                       cloudfare_south_america + cloudfare_middle_east + \
                       cloudfare_north_america + cloudfare_oceania


def get_all_cloudfare_servers():
    airports_df = pd.read_csv(AIRPORTS_INFO_FILEPATH, sep="\t")
    airports_df = airports_df[["#IATA", "country_code", "city", "lat long"]]

    airports_df.rename(columns={
        "#IATA": "IATA_code", "city": "city_name"
    }, inplace=True)


    print("Filter by cloudfare")
    cloufare_instances_df = airports_df[
        airports_df["IATA_code"].isin(cloudfare_oceania)
    ].copy()

    print("Getting country names")
    cloufare_instances_df["country_name"] = cloufare_instances_df["country_code"].apply(
        lambda country_code: get_country_name(country_code)
    )

    print("Formatting latitude and longitude")
    cloufare_instances_df["latitude"] = cloufare_instances_df["lat long"].apply(
        lambda lat_long: float(lat_long.split(" ")[0])
    )

    cloufare_instances_df["longitude"] = cloufare_instances_df["lat long"].apply(
        lambda lat_long: float(lat_long.split(" ")[1])
    )

    cloufare_instances_df.drop(columns=["lat long"], inplace=True)

    dict_to_json_file(
        file_path=CLOUDFARE_PATH + "cloudfare_servers_oceania.json",
        dict=cloufare_instances_df.to_dict("records"))


get_all_cloudfare_servers()
