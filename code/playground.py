#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from utils.constants import (
    FIBER_RI,
    SPEED_OF_LIGHT
)
from utils.common_functions import (
    get_distance_from_rtt,
    get_light_factor_from_distance,
    get_time_from_distance
)

distances = list(range(0, 4520, 20))
trip_time_ms_results = {}
print("Light speed reduction factor calculations")
for distance in distances:
    trip_time_ms = get_time_from_distance(distance) * 1000
    trip_time_ms_results[trip_time_ms] = distance

#results = pd.DataFrame()
#results["distances"] = distances
#results["trip_time_ms"] = trip_time_ms_results
#results.to_csv("light.csv", sep=",")

rtt = 7.062529
nearest_value = min(trip_time_ms_results, key=lambda x: abs(x - (rtt / 2)))
print("Real trip time: ", rtt/2)
print("Nearest value: ", nearest_value)
print("Distance approximated: ", trip_time_ms_results[nearest_value])
distance_constant = ((rtt/2)*0.001) * (FIBER_RI*SPEED_OF_LIGHT)
print("Distance constant: ", distance_constant)
