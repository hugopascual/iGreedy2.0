#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
from shapely import Point
from shapely import from_geojson
# internal modules imports
from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH
)
from utils.common_functions import (
    get_list_files_in_path,
    json_file_to_dict,
    get_nearest_airport_to_point,
    dict_to_json_file
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

        results_not_valid = []

        for result_filename in results_filenames:
            result_dict = json_file_to_dict("{}/{}".format(
                self._validation_campaign_directory, result_filename)
            )

            if result_dict["gt_info"] == {}:
                results_not_valid.append(result_filename)
                continue

            validation_results_df = pd.concat(
                [pd.DataFrame([[
                    result_dict["target"],
                    result_filename,
                    result_dict["traceroute_from_host"],
                    len(result_dict["hunt_results"]["countries"]),
                    len(result_dict["hunt_results"]["cities"]),
                    len(result_dict["hunt_results"]["airports_located"]),
                    self.calculate_hunter_result_outcome_country(result_dict),
                    self.calculate_hunter_result_outcome_city(result_dict)
                ]], columns=validation_results_df.columns,
                ), validation_results_df],
                ignore_index=True
            )

        validation_results_df.to_csv(self._output_filename + ".csv", sep=",")
        dict_to_json_file(results_not_valid, "results_not_valid.json")

    # Auxiliary functions
    def calculate_hunter_result_outcome_country(self, results: dict) -> str:
        num_result_countries = len(results["hunt_results"]["countries"])
        if num_result_countries == 1:
            if results["gt_info"]["country_code"] == \
                    results["hunt_results"]["countries"][0]:
                return "Positive"
            else:
                return "Negative"
        elif num_result_countries == 0:
            try:
                centroid = from_geojson(results["hunt_results"]["centroid"])
            except Exception as e:
                print("Exception:")
                print(e)
                return "Indeterminate"
            nearest_airport = get_nearest_airport_to_point(centroid)
            if results["gt_info"]["country_code"] == \
                    nearest_airport["country_code"]:
                return "Positive"
            else:
                return "Negative"
        else:
            return "Indeterminate"

    def calculate_hunter_result_outcome_city(self, results: dict):
        num_result_cities = len(results["hunt_results"]["cities"])
        if num_result_cities == 1:
            if results["gt_info"]["city"] == \
                    results["hunt_results"]["cities"][0]:
                return "Positive"
            else:
                return "Negative"
        elif num_result_cities == 0:
            try:
                centroid = from_geojson(results["hunt_results"]["centroid"])
            except Exception as e:
                print(e)
                return "Indeterminate"
            nearest_airport = get_nearest_airport_to_point(centroid)
            if results["gt_info"]["city"] == \
                    nearest_airport["city"]:
                return "Positive"
            else:
                return "Negative"
        else:
            return "Indeterminate"


Statistics("hunter",
           "{}{}".format(
               HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
               "validation_anycast_cloudfare_20230525"),
           "statistics_validation_anycast_cloudfare_20230525"
           )



