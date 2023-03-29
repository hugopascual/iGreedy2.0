#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd

#base_url = "https://atlas.ripe.net/api/v2/measurements/{}/results"
#
#measurement_id = "50938774"
#
#response = requests.get(base_url.format(measurement_id)).json()
#
#print(json.dumps(response, indent=4))

def json_file_to_dict(file_path: str) -> list:
    with open(file_path) as file:
        raw_json = file.read()
    
    return json.loads(raw_json)

filepath = "gt_test.csv"
gt_df = pd.read_csv(filepath)
num_instances_near = len(gt_df[(gt_df["distance"]<100.0)])
print(gt_df)
print(num_instances_near)
