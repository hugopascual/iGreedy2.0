#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
# internal modules imports
from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH
)
from utils.common_functions import (
    get_list_files_in_path,
    json_file_to_dict
)


class Statistics:

    def __init__(self, tool: str, validation_campaign_directory: str,
                 output_filename: str):
        self._validation_campaign_directory = validation_campaign_directory
        self._output_filename = output_filename

        if tool.lower() == "hunter":
            self.hunter_build_statistics_validation_campaign()
        elif tool.lower() == "igreedy":
            self.igreedy_build_statistics_validation_campaign()
        else:
            print("No proper tool solicited")
            return

    def igreedy_build_statistics_validation_campaign(self):
        return

    def hunter_build_statistics_validation_campaign(self):
        results_filenames = get_list_files_in_path(
            self._validation_campaign_directory)
        validation_results_df = pd.DataFrame(columns=[
            "target", "filename", "from_host", "num_countries", "num_cities",
            "num_airports", "country_outcome", "city_outcome"
        ])
        for result_filename in results_filenames:
            result_dict = json_file_to_dict("{}/{}".format(
                self._validation_campaign_directory, result_filename)
            )

            if result_dict["gt_info"] == {}:
                print("No ground-truth info to compare in {}".format(
                    result_filename))
                continue

            validation_results_df = pd.concat(
                [pd.DataFrame([[
                    result_dict["target"],
                    result_filename,
                    result_dict["traceroute_from_host"],
                    len(result_dict["hunt_results"]["countries"]),
                    len(result_dict["hunt_results"]["cities"]),
                    len(result_dict["hunt_results"]["airports_located"]),
                    self.calculate_hunter_result_outcome(
                        "country", result_dict),
                    self.calculate_hunter_result_outcome(
                        "city", result_dict)
                ]], columns=validation_results_df.columns
                ), validation_results_df],
                ignore_index=True
            )

        validation_results_df.to_csv(self._output_filename + ".csv",
                                     sep=",")

    # Auxiliary functions
    def calculate_hunter_result_outcome(self, decisive_param: str,
                                        results: dict) -> str:
        if decisive_param == "city":
            if len(results["hunt_results"]["cities"]) == 1:
                city_result = results["hunt_results"]["cities"][0]
                city_gt = results["gt_info"]["city"]
                if city_gt == city_result:
                    return "TP"
                else:
                    return "FP"
            else:
                return "MR"
        elif decisive_param == "country":
            if len(results["hunt_results"]["countries"]) == 1:
                city_result = results["hunt_results"]["countries"][0]
                city_gt = results["gt_info"]["country_code"]
                if city_gt == city_result:
                    return "TP"
                else:
                    return "FP"
            else:
                return "MR"
        else:
            print("Decisive parameter not valid")

    def add_row_to_dataframe(self, df: pd.DataFrame, value_list: list):
        return


Statistics("hunter",
           "{}{}".format(
               HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
               "20230522_validation_anycast_cloudfare"),
           "statistics_validation_anycast_cloudfare"
           )



