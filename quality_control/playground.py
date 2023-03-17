#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import constants as Constants
import auxiliar
from stadistics import (
    area_intances_check
)
import load_data

gt_filename = "root_servers_F.json"
results_filename = "North-Central_1000_192.5.5.241_1.json"
north_central_area = auxiliar.get_alpha2_country_codes("EU_countries.json")
all_countries = auxiliar.get_alpha2_country_codes(Constants.ALL_COUNTRIES_FILE_PATH)

area_intances_check(load_data.load_data_root_servers(gt_filename), 
                    load_data.load_data_results(results_filename), 
                    north_central_area)
