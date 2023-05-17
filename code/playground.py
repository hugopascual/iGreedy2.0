#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import re
import geocoder
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
    get_time_from_distance,
    json_file_to_dict,
    dict_to_json_file
)

result = geocoder.ip("me").geojson
dict_to_json_file(result, "test.json")
print(result)


