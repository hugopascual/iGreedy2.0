#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from auxiliar import (
    dict_to_json_file
)
from load_data import (
    load_data_root_servers,
    load_data_results
)
    
# Constansts
measurements_path = "../datasets/measurement/"
results_path = "../results/"

# Variables where load the information
gt_instances = {}
results_instances = {}

gt_instances = load_data_root_servers("root_servers_A.json")
results_instances = load_data_results("test_300_198.41.0.4.json")
dict_to_json_file(results_instances, "test.json")