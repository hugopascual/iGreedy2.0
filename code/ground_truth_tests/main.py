#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from auxiliar import (
    dict_to_json_file
)
from load_data import (
    load_data_root_servers,
    load_data_results
)
from stadistics import (
    print_global_gt_definitions,
    global_instances_check
)
    
# Constansts
#gt_filename = "root_servers_.json"
#results_filename = "North-Central_1000_192.203.230.10.json"

# Load the information about GT and Results
#gt_instances = load_data_root_servers(gt_filename)
#results_instances = load_data_results(results_filename)

# Check performance
gt_filename = "root_servers_F.json"
ip_direcction = "192.5.5.241"
alpha_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
measurement_filename_list=[
  "North-Central_100_192.5.5.241",
  "North-Central_300_192.5.5.241",
  "North-Central_500_192.5.5.241",
  "North-Central_1000_192.5.5.241", 
  "WW_100_192.5.5.241",
  "WW_300_192.5.5.241",
  "WW_500_192.5.5.241",
  "WW_1000_192.5.5.241"
]

gt_instances = load_data_root_servers(gt_filename)
print_global_gt_definitions()
for measurement_filename in measurement_filename_list:
    for alpha in alpha_list:
        results_filename = "{}_{}.json".format(measurement_filename, alpha)
        results_instances = load_data_results(results_filename)
        print(results_filename)
        global_instances_check(gt_instances, results_instances)