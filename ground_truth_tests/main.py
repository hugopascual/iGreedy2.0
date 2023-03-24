#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import constants as Constants
from auxiliar import (
    dict_to_json_file,
    json_file_to_dict,
    list_to_json_file,
    get_alpha2_country_codes_from_file,
    list_of_dicts_to_csv
)
from load_data import (
    load_data_root_servers,
    load_data_results,
    get_countries_set_from_root_servers,
    get_countries_set_from_results
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
#area_name = "WW"
area_name = "North-Central"
num_probes_list = [100, 300, 500, 1000]
area_ww = get_alpha2_country_codes_from_file(Constants.ALL_COUNTRIES_FILE_PATH)
area_north_central = get_alpha2_country_codes_from_file(Constants.NORTH_CENTRAL_COUNTRIES_FILE_PATH)

results_filename_list = []

for num_probes in num_probes_list:
    for alpha in alpha_list:
        results_filename_list.append("{}_{}_{}_{}.json".format(area_name, num_probes, ip_direcction, alpha))

# Load sets of instances
gt_instances = get_countries_set_from_root_servers(gt_filename)
gt_stadistics = []
gt_stadistics_filename = "ground_truth_metrics/{}_campaign_20230324".format(area_name)

for results_filename in results_filename_list:
    results = json_file_to_dict("../results/campaings/20230324/"+results_filename)
    results_instances = get_countries_set_from_results("campaings/20230324/"+results_filename)
    stadistics_dict = area_intances_check(gt_instances, results_instances, area_ww)
    stadistics_dict["num_probes"] = int(results_filename.split("_")[1])
    stadistics_dict["alpha"] = results["alpha"]
    stadistics_dict["threshold"] = results["threshold"]
    stadistics_dict["noise"] = results["noise"]
    stadistics_dict["probes_filename"] = results["probes_filename"].split("/")[-1]
    stadistics_dict["target"] = results["target"]
    stadistics_dict["result_filename"] = results_filename
    stadistics_dict["gt_namefile"] = gt_filename
    gt_stadistics.append(stadistics_dict)
    
list_to_json_file(gt_stadistics, gt_stadistics_filename+".json")
list_of_dicts_to_csv(gt_stadistics, gt_stadistics_filename+".csv")
