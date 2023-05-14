#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess

import pandas as pd
import requests
from scapy.layers.inet import traceroute
from subprocess import run
from utils.constants import (
    FIBER_RI,
    SPEED_OF_LIGHT
)
from utils.common_functions import (
    get_distance_from_rtt,
    get_light_factor_from_distance,
    get_time_from_distance
)


def host_traceroute_measurement_scapy():
    result_traceroute = traceroute(target="192.5.5.241")
    print(result_traceroute)


def host_traceroute_measurement_shell():
    target = "192.5.5.241"
    result_traceroute = run(["traceroute", target], stdout=subprocess.PIPE)
    hops_list = ((str(result_traceroute.stdout)).split("\\n")[1:])[:-1]
    print(hops_list)
    last_hop_info = hops_list[-2]
    print(last_hop_info)


host_traceroute_measurement_shell()
