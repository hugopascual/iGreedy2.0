#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.common_functions import (
    get_distance_from_rtt,
    get_light_factor_from_distance,
    get_time_from_distance
)

distances = list(range(0, 4520, 20))
rtt_results = []
print("Light speed reduction factor calculations")
for distance in distances:
    rtt_results.append(get_time_from_distance(distance))

print(distances)
print(rtt_results)

