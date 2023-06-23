#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import subprocess

from utils.common_functions import (
    dict_to_json_file
)


def is_IP_anycast(ip: str) -> bool:
    command = subprocess.run([
        "./igreedy.sh",
        "-m", ip,
        "-p", "datasets/probes_sets/WW_1000.json",
        "-r", "true",
        "-a", 1,
        "-t", 1,
        "-c", "PoPETs_IP_anycast_validation"
    ])
    if command.returncode == 0:
        return True
    else:
        return False


popets_filepath = "datasets/PoPETs_dynamic_results.csv"
popets_df = pd.read_csv(popets_filepath, sep=",")

ip_to_check_list = popets_df["ip_dest"].unique()

ip_results_dict = {}
for ip_to_check in ip_to_check_list:
    ip_results_dict[ip_to_check] = is_IP_anycast(ip_to_check_list)

dict_to_json_file(
    dict=ip_results_dict,
    file_path="datasets/PoPETs_anycast_ip_validation"
)
