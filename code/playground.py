#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from utils.common_functions import (
    json_file_to_list,
    dict_to_json_file
)


def generate_new_probes_set_using_countries():
    probes_set = {"probes": []}
    num_probes_per_country = [5, 10, 15]
    countries_array = json_file_to_list(
        "../datasets/countries_sets/North-Central_countries.json")
    alpha2_codes = []
    for country in countries_array:
        alpha2_codes.append(country["alpha-2"])

    for num_probes in num_probes_per_country:
        for code in alpha2_codes:
            probes_set["probes"].append({
                "requested": num_probes,
                "type": "country",
                "value": code
            })

        dict_to_json_file(
            dict=probes_set,
            file_path="../datasets/probes_sets/Europe_countries_{}.json".
            format(num_probes))
        probes_set = {"probes": []}
