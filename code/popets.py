#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import pandas as pd
import subprocess
import ipinfo
import socket

from utils.constants import (
    KEY_FILEPATH
)
from utils.common_functions import (
    dict_to_json_file,
    json_file_to_dict
)


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

