#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import subprocess
# internal modules imports
from utils.constants import (
    CLOUDFARE_IPS,
    ROOT_SERVERS,
    PROBES_SETS_PATH
)


class iGreedyValidation:

    def __init__(self):
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

        self._measurement_campaign_name = \
            "North-Central_validation_20230410"

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
        return

igreedy_validation = iGreedyValidation()
#igreedy_validation.generate_measurements()
