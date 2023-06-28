#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import pandas as pd
import subprocess
import ipinfo
import socket
from shapely import from_geojson

from utils.constants import (
    KEY_FILEPATH,
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
    HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH
)
from utils.common_functions import (
    dict_to_json_file,
    json_file_to_dict,
    countries_in_EEE_set,
    get_list_files_in_path,
    get_nearest_airport_to_point
)
from hunter import Hunter


def is_IP_anycast(ip: str) -> bool:
    command = subprocess.run([
        "./igreedy.sh",
        "-m", ip,
        "-p", "datasets/probes_sets/WW_1000.json",
        "-r", "true",
        "-a", "1",
        "-t", "1",
        "-c", "PoPETs_IP_anycast_validation"
    ], stdout=subprocess.PIPE)

    if command.returncode == 0:
        return True
    else:
        return False


def check_ip(ip: str):
    try:
        addr = socket.inet_pton(socket.AF_INET6, ip)
    except socket.error: # not a valid IPv6 address
        try:
            addr = socket.inet_pton(socket.AF_INET, ip)
        except socket.error: # not a valid IPv4 address either
            return False
    return True

def check_popets_ip_list_anycast_igreedy():
    popets_filepath = "datasets/PoPETs_dynamic_results.csv"
    popets_df = pd.read_csv(popets_filepath, sep=",")

    ip_to_check_list = popets_df["ip_dest"].unique()

    try:
        ip_results_dict = json_file_to_dict(
            "datasets/PoPETs_anycast_ip_validation_igreedy.json")
    except:
        ip_results_dict = {}

    for ip_to_check in ip_to_check_list:
        if isinstance(ip_to_check, str):
            if ip_to_check not in list(ip_results_dict.keys()):
                print("Validating IP {}".format(ip_to_check))
                is_anycast = is_IP_anycast(ip_to_check)
                ip_results_dict[ip_to_check] = is_anycast
                print("IP {} result is anycast: {}".format(
                    ip_to_check, is_anycast)
                )
                dict_to_json_file(
                    dict=ip_results_dict,
                    file_path=
                    "datasets/PoPETs_anycast_ip_validation_igreedy.json"
                )


def check_popets_ip_list_anycast_ipinfo():
    popets_filepath = "datasets/PoPETs_dynamic_results.csv"
    popets_df = pd.read_csv(popets_filepath, sep=",")

    ip_to_check_list = popets_df["ip_dest"].unique()

    try:
        ip_results_dict = json_file_to_dict(
            "datasets/PoPETs_anycast_ip_validation_ipinfo.json")
    except:
        ip_results_dict = {}

    for ip_to_check in ip_to_check_list:
        ip_to_check = str(ip_to_check)
        print(ip_to_check)
        if not check_ip(ip_to_check):
            print("IP not valid")
            continue

        access_token = json_file_to_dict(KEY_FILEPATH)["key2"]
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails(ip_to_check)

        #print(json.dumps(details.all, indent=4))
        try:
            ip_results_dict[ip_to_check] = details.anycast
        except:
            ip_results_dict[ip_to_check] = False

    dict_to_json_file(
        dict=ip_results_dict,
        file_path=
        "datasets/PoPETs_anycast_ip_validation_ipinfo.json"
    )


def hunt_popets_anycast():
    popets_ip_dict = json_file_to_dict(
        "datasets/" + "PoPETs_anycast_ip_validation_ipinfo.json"
    )

    anycast_ip_list = [ip for ip in popets_ip_dict.keys()
                       if popets_ip_dict[ip]]
    print(len(anycast_ip_list))

    #countries_origin_set = countries_in_EEE_set()
    countries_origin_set = [
        #"IE", "FI", "NO", "IS", "SE", "NL", "AT",
        #"BE", "BG", "CY", "CZ", "DE",
        "ES", "EE", "DK",
        "FR", "GR", "HR", "HU", "IT", "LT", "LU", "LV",
        "MT", "PL", "PT", "SI", "SK"
    ]
    campaign_name = "PoPETs_anycast_ipinfo"
    for country in countries_origin_set:
        additional_info = connect_to_vpn_server(country)
        print("Server searched {}, VPN connected {}".format(
            country, additional_info["server_name"]
        ))

        for target in anycast_ip_list:
            output_filename = "{}{}/{}_{}.json".format(
                HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
                campaign_name, target, country)
            hunter = Hunter(
                target=target,
                check_cf_ray=False,
                output_filename=output_filename,
                additional_info=additional_info,
                validate_last_hop=False
            )
            hunter.hunt()


def connect_to_vpn_server(vpn_server: str) -> dict:
    connection_result = subprocess.run([
        "protonvpn-cli", "connect", "--cc",
        vpn_server,
        "--protocol", "tcp"], stdout=subprocess.PIPE)
    connection_status = subprocess.run([
        "protonvpn-cli", "status"], stdout=subprocess.PIPE)
    status_params_raw = (str(connection_status.stdout)
                         .split("\\n")[3:])[:-6]
    status_params = []
    for param_raw in status_params_raw:
        status_params.append((param_raw.split("\\t")[-1])[1:])
    try:
        return {
            "ip": status_params[0],
            "server_name": status_params[1],
            "country": status_params[2],
            "protocol": status_params[3],
        }
    except Exception as e:
        print(e)
        return {
            "params": status_params
        }


def generata_popets_results(validate_last_hop: bool,
                            validate_target: bool,
                            campaign_name: str):
    campaign_filepath = HUNTER_MEASUREMENTS_CAMPAIGNS_PATH + campaign_name
    countries_in_EEE = countries_in_EEE_set()
    results_filenames_list = get_list_files_in_path(campaign_filepath)

    popets_jumps_df = pd.DataFrame(columns=[
        "target", "origin_name", "origin_code", "destination_code",
        "out_of_EEE", "reason"
    ])
    for result_filename in results_filenames_list:
        print(result_filename)
        result_filepath = campaign_filepath + "/" + result_filename
        result_dict = json_file_to_dict(result_filepath)

        origin_code = result_dict["additional_info"]["server_name"].split(
            "#")[0]

        (destination_code, reason) = calculate_hunter_result_outcome(
            results=result_dict,
            validate_last_hop=validate_last_hop,
            validate_target=validate_target
        )

        if (destination_code in countries_in_EEE) or \
                destination_code == "Indeterminate":
            out_of_EEE = False
        else:
            out_of_EEE = True

        popets_jumps_df = pd.concat([pd.DataFrame([[
            result_dict["target"],
            result_dict["additional_info"]["country"],
            origin_code,
            destination_code,
            bool(out_of_EEE),
            reason
        ]], columns=popets_jumps_df.columns),
            popets_jumps_df
        ], ignore_index=True)

    popets_jumps_df.sort_values(by=["out_of_EEE",
                                    "target",
                                    "destination_code",
                                    "origin_code"],
                                ascending=[False, True, True, True],
                                inplace=True)
    if validate_target and validate_last_hop:
        validation_name = "ip_all_validation"
    elif validate_target:
        validation_name = "ip_target_validation"
    elif validate_last_hop:
        validation_name = "ip_last_hop_validation"
    else:
        validation_name = "no_ip_validation"
    popets_jumps_df.to_csv(HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
                           "{}_{}.csv".format(campaign_name, validation_name),
                           sep=",",
                           index=False)


def calculate_hunter_result_outcome(
        results: dict,
        validate_last_hop: bool = True,
        validate_target: bool = True) -> (str, str):
    result_param = "countries"
    gt_param = "country_code"

    if validate_last_hop:
        try:
            if len(results["hops_directions_list"][-2]) != 1:
                return "Indeterminate", "Multiples IP on last_hop"
            elif results["hops_directions_list"][-1] == "*":
                return "Indeterminate", "Last_hop hop do not respond"
        except:
            print("Target directions list exception")
            return "Indeterminate", "Exception in last_hop validation"

    if validate_target:
        try:
            if len(results["hops_directions_list"][-1]) != 1:
                return "Indeterminate", "Multiples IP on target hop"
            elif results["hops_directions_list"][-1] == "*":
                return "Indeterminate", "Target hop do not respond"
        except:
            print("Target directions list exception")
            return "Indeterminate", "Exception in target validation"

    # Num of results validation
    num_result_countries = len(results["hunt_results"]["countries"])
    if num_result_countries == 1:
        return results["hunt_results"][result_param][0], "Result intersection"
    elif num_result_countries == 0:
        centroid = from_geojson(results["hunt_results"]["centroid"])
        if not results["last_hop"]["ip"]:
            return "Indeterminate", "Last hop not valid"
        elif not results["last_hop"]["geolocation"]:
            return "Indeterminate", "Last hop not geolocated"
        elif not results["discs_intersect"]:
            return "Indeterminate", "Ping discs no intersection"
        elif not centroid:
            return "Indeterminate", "Centroid not found"
        else:
            nearest_airport = get_nearest_airport_to_point(centroid)
            return nearest_airport[gt_param], "Result nearest airport"
    else:
        return "Indeterminate", "Too many locations"


def get_ip_out_EEE_list(filename: str) -> list:
    jumps_popets_df = pd.read_csv(
        HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + filename,
        sep=","
    )

    jumps_popets_df = jumps_popets_df[
        jumps_popets_df["out_of_EEE"] == bool(True)]
    return list(jumps_popets_df["target"].unique())


hunt_popets_anycast()
#generata_popets_results(
#    validate_last_hop=True,
#    validate_target=True,
#    campaign_name="PoPETs_anycast_ipinfo"
#)
#generata_popets_results(
#    validate_last_hop=False,
#    validate_target=True,
#    campaign_name="PoPETs_anycast_ipinfo"
#)
#generata_popets_results(
#    validate_last_hop=True,
#    validate_target=False,
#    campaign_name="PoPETs_anycast_ipinfo"
#)
#generata_popets_results(
#    validate_last_hop=False,
#    validate_target=False,
#    campaign_name="PoPETs_anycast_ipinfo"
#)
#print(
#    len(get_ip_out_EEE_list("PoPETs_anycast_ipinfo_ip_target_validation.csv"))
#)
