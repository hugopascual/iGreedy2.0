#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import pandas as pd
import subprocess
import ipinfo
import socket

from utils.constants import (
    KEY_FILEPATH,
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH
)
from utils.common_functions import (
    dict_to_json_file,
    json_file_to_dict,
    countries_in_EEE_set
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
        "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
        "FR", "GR", "HR", "HU", "IE", "IS", "IT", "LT", "LU", "LV",
        "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK"
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


hunt_popets_anycast()
