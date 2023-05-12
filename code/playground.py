#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import requests
from utils.constants import (
    FIBER_RI,
    SPEED_OF_LIGHT
)
from utils.common_functions import (
    get_distance_from_rtt,
    get_light_factor_from_distance,
    get_time_from_distance
)


target = "192.5.5.241"
results = {}


def obtain_cf_ray(target: str, results: dict):
    url = "http://{}".format(target)
    print(url)
    headers = requests.get(url).headers
    print(headers)
    try:
        cf_ray_iata_code = headers["cf-ray"].split("-")[1]
    except:
        print("NO CF-RAY IN HEADERS")
        cf_ray_iata_code = ""
    results["cf_ray_iata_code"] = cf_ray_iata_code


obtain_cf_ray(target, results)

print(results)
