#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import constants as Constants
from auxiliar import (
    dict_to_json_file,
    get_alpha2_country_codes_from_file
)
from load_data import (
    load_data_root_servers,
    load_data_results
)
from stadistics import (
    print_global_gt_definitions,
    global_instances_check,
    area_intances_check
)

# Check performance
# Ground truth variables
gt_filename = "root_servers_F.json"
ip_direcction = "192.5.5.241"

# Iteration and sets
alpha_list = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
area_name = "WW"
num_probes_list = [100, 300, 500, 1000]
area_ww = get_alpha2_country_codes_from_file(Constants.ALL_COUNTRIES_FILE_PATH)
area_north_central = get_alpha2_country_codes_from_file(Constants.NORTH_CENTRAL_COUNTRIES_FILE_PATH)

results_filename_list = []

for num_probes in num_probes_list:
    for alpha in alpha_list:
        results_filename_list.append("{}_{}_{}_{}.json".format(area_name, num_probes, ip_direcction, alpha))

# Load sets of instances
gt_instances = load_data_root_servers(gt_filename)

for results_filename in results_filename_list:
    results_instances = load_data_results("campaigns/20230324/"+results_filename)
    dict_to_json_file(area_intances_check(gt_instances, results_instances, area_ww),
                      "ground_truth_metrics/"+results_filename)