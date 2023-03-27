#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

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

filepath = "ground_truth_tests/ground_truth_metrics/North-Central_campaign_20230324.csv"

import plotly.express as px
df = px.data.gapminder().query("country=='Canada'")
fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
fig.show()


import pandas as pd
df = pd.read_csv(filepath)
