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

    def __init__(self, tool: str, validation_campaign_directory: str):
        self._validation_campaign_directory = validation_campaign_directory

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
            HUNTER_MEASUREMENTS_CAMPAIGNS_PATH +
            self._validation_campaign_directory)
        validation_results_df = pd.DataFrame(columns=[
            "target", "filename", "from_host", "num_countries", "num_cities",
            "num_airports", "country_outcome", "country_outcome_reason",
            "city_outcome", "city_outcome_reason"
        ])

        results_not_valid = []

        for result_filename in results_filenames:
            #print(result_filename)
            result_dict = json_file_to_dict("{}/{}".format(
                HUNTER_MEASUREMENTS_CAMPAIGNS_PATH +
                self._validation_campaign_directory, result_filename)
            )

            if result_dict["gt_info"] == {}:
                results_not_valid.append(result_filename)
                continue

            outcome_country = self.calculate_hunter_result_outcome_country(
                result_dict)
            outcome_city = self.calculate_hunter_result_outcome_city(
                result_dict)

            validation_results_df = pd.concat(
                [pd.DataFrame([[
                    result_dict["target"],
                    result_filename,
                    result_dict["traceroute_from_host"],
                    len(result_dict["hunt_results"]["countries"]),
                    len(result_dict["hunt_results"]["cities"]),
                    len(result_dict["hunt_results"]["airports_located"]),
                    outcome_country[0],
                    outcome_country[1],
                    outcome_city[0],
                    outcome_city[1]
                ]], columns=validation_results_df.columns,
                ), validation_results_df],
                ignore_index=True
            )

        validation_results_df.to_csv(
            HUNTER_MEASUREMENTS_CAMPAIGNS_PATH +
            self._validation_campaign_directory + "_statistics.csv",
            sep=",")

        dict_to_json_file(
            results_not_valid,
            HUNTER_MEASUREMENTS_CAMPAIGNS_PATH +
            self._validation_campaign_directory + "_results_not_valid.json")

    # Auxiliary functions
    def calculate_hunter_result_outcome_country(self, results: dict) -> \
            (str, str):

        try:
            if len(results["hops_directions_list"][-1]) != 1:
                return "Indeterminate", "Multiples IP on target hop"
        except:
            print("Target directions list exception")

        num_result_countries = len(results["hunt_results"]["countries"])
        if num_result_countries == 1:
            if results["gt_info"]["country_code"] == \
                    results["hunt_results"]["countries"][0]:
                return "Positive", "Same country airport"
            else:
                return "Negative", "Different country airport"
        elif num_result_countries == 0:
            centroid = from_geojson(results["hunt_results"]["centroid"])
            if centroid:
                nearest_airport = get_nearest_airport_to_point(centroid)
                if results["gt_info"]["country_code"] == \
                        nearest_airport["country_code"]:
                    return "Positive", "Same country in nearest airport"
                else:
                    return "Negative", "Different country in nearest airport"
            else:
                if results["discs_intersect"]:
                    return "Indeterminate", "Ping discs no intersection"
                else:
                    return "Indeterminate", "Shapely dont intersect"
        else:
            return "Indeterminate", "Too many countries"

    def calculate_hunter_result_outcome_city(self, results: dict) -> \
            (str, str):
        try:
            if len(results["hops_directions_list"][-1]) != 1:
                return "Indeterminate", "Multiples IP on target hop"
        except:
            print("Target directions list exception")

        num_result_cities = len(results["hunt_results"]["cities"])
        if num_result_cities == 1:
            if results["gt_info"]["city"] == \
                    results["hunt_results"]["cities"][0]:
                return "Positive", "Same city airport"
            else:
                return "Negative", "Different city airport"
        elif num_result_cities == 0:
            centroid = from_geojson(results["hunt_results"]["centroid"])
            if centroid:
                nearest_airport = get_nearest_airport_to_point(centroid)
                if results["gt_info"]["city"] == \
                        nearest_airport["city"]:
                    return "Positive", "Same city in nearest airport"
                else:
                    return "Negative", "Different country in nearest airport"
            else:
                if results["discs_intersect"]:
                    return "Indeterminate", "Ping discs no intersection"
                else:
                    return "Indeterminate", "Shapely dont intersect"
        else:
            return "Indeterminate", "Too many cities"


Statistics("hunter", "validation_anycast_udp_cloudfare_20230529_1")



