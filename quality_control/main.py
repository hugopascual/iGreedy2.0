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
    global_instances_check
)
    
# Constansts
gt_filename = "root_servers_A.json"
results_filename = "test_300_198.41.0.4.json"

# Load the information about GT and Results
gt_instances = load_data_root_servers(gt_filename)
results_instances = load_data_results(results_filename)

# Check performance
global_instances_check(gt_instances, results_instances)