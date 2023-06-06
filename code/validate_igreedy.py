#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import subprocess
# internal modules imports
from utils.constants import (
    CLOUDFARE_IPS,
    ROOT_SERVERS,
    PROBES_SETS_PATH,
    MEASUREMENTS_CAMPAIGNS_PATH,
    ROOT_SERVERS_PATH,
    CLOUDFARE_PATH,
    DISTANCE_FUNCTION_USED
)
from utils.common_functions import (
    get_list_files_in_path,
    json_file_to_dict
)


class iGreedyValidation:

    def __init__(self, measurement_campaign_name: str):
        self._probefile_list = [
            #"North-Central_1000.json",
            #"North-Central_500.json",
            #"North-Central_300.json",
            #"North-Central_100.json",
            #"North-Central-section_1.5.json",
            #"North-Central-section_1.json",
            #"North-Central-section_2.json",
            "Europe-countries_5.json",
            "Europe-countries_10.json",
            "Europe-countries_15.json"
        ]
        self._target_list = []
        self._target_list += CLOUDFARE_IPS
        self._target_list += list(ROOT_SERVERS.keys())

        self._alpha_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        self._threshold_list = [-1, 0.5, 1, 5, 10, 20, 30]

        self._measurement_campaign_name = measurement_campaign_name

    def generate_measurements(self):
        for target in self._target_list:
            for probe_set in self._probefile_list:
                measurement_command_result = subprocess.run(
                    [
                        "./igreedy.sh",
                        "-m", target,
                        "-p", PROBES_SETS_PATH + probe_set,
                        "-c", self._measurement_campaign_name
                    ],
                    stdout=subprocess.PIPE
                )
                print(str(measurement_command_result.stdout))

    def generate_results_and_gt_validations(self):
        measurement_files = get_list_files_in_path(
            MEASUREMENTS_CAMPAIGNS_PATH + self._measurement_campaign_name
        )

        for measurement_name in measurement_files:
            measurement_path = MEASUREMENTS_CAMPAIGNS_PATH + \
                               self._measurement_campaign_name + \
                               "/" + measurement_name
            measurement_data = json_file_to_dict(measurement_path)

            if measurement_data["target"] in ROOT_SERVERS.keys():
                gt_filepath = ROOT_SERVERS_PATH + \
                              ROOT_SERVERS[measurement_data["target"]]
            elif measurement_data["target"] in CLOUDFARE_IPS:
                gt_filepath = CLOUDFARE_PATH + "cloudfare_servers_europe.json"
            else:
                print("TARGET {} NOT IN GROUNDTRUTH".format(
                    measurement_data["target"]))
                continue

            campaign_name = self._measurement_campaign_name + \
                            "_" + DISTANCE_FUNCTION_USED

            for alpha in self._alpha_list:
                for threshold in self._threshold_list:
                    print("Analyzing {} with alpha -> {} and threshold -> {}"
                          .format(measurement_name, alpha, threshold))
                    result_and_gt_generation = subprocess.run(
                        [
                            "./igreedy.sh",
                            "-i", measurement_path,
                            "-a", str(alpha),
                            "-t", str(threshold),
                            "-g", gt_filepath,
                            "-c", campaign_name
                        ],
                        stdout=subprocess.PIPE
                    )


igreedy_validation = iGreedyValidation(
    measurement_campaign_name="North-Central_validation_20230410"
)
#igreedy_validation.generate_measurements()
igreedy_validation.generate_results_and_gt_validations()
