#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

base_url = "https://atlas.ripe.net/api/v2/measurements/{}/results"

measurement_id = "50938774"

response = requests.get(base_url.format(measurement_id)).json()

print(json.dumps(response, indent=4))