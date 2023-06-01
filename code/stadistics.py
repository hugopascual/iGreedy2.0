#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
from shapely import Point
from shapely import from_geojson
# internal modules imports
from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
    HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH
)
from utils.common_functions import (
    get_list_files_in_path,
    json_file_to_dict,
    get_nearest_airport_to_point,
    dict_to_json_file
)


class Statistics:

    def __init__(self,
                 validation_campaign_directory: str,
                 output_filename: str):
        self._validation_campaign_directory = validation_campaign_directory
        self._output_filename = output_filename

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
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + "statistics_" +
            self._output_filename + ".csv",
            sep=",")

        dict_to_json_file(
            results_not_valid,
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
            "results_not_valid_" + self._output_filename + ".json")

    # Auxiliary functions
    def calculate_hunter_result_outcome_country(self, results: dict) -> \
            (str, str):
        #try:
        #    if len(results["hops_directions_list"][-1]) != 1:
        #        return "Indeterminate", "Multiples IP on target hop"
        #    elif results["hops_directions_list"][-1] == "*":
        #        return "Indeterminate", "Target hop do not respond"
        #except:
        #    print("Target directions list exception")

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
        #try:
        #    if len(results["hops_directions_list"][-1]) != 1:
        #        return "Indeterminate", "Multiples IP on target hop"
        #    elif results["hops_directions_list"][-1] == "*":
        #        return "Indeterminate", "Target hop do not respond"
        #except:
        #    print("Target directions list exception")

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

    def aggregate_hunter_statistics(self):
        statistics_files = [filename for filename in
                            get_list_files_in_path(
                                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH)
                            if "statistics" in filename]
        aggregation_df = pd.DataFrame(columns=[
            "filename",
            "country_positive_percent", "country_negative_percent",
            "country_indeterminate_percent",
            "country_positives", "country_negatives", "country_indeterminates",
            "city_positive_percent", "city_negative_percent",
            "city_indeterminate_percent",
            "city_positives", "city_negatives", "city_indeterminates"
        ])
        for statistic_file in statistics_files:
            statistic_df = pd.read_csv(
                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + statistic_file)
            total = len(statistic_df.index)

            country_positives = len(
                statistic_df[statistic_df['country_outcome'] == "Positive"])
            country_negatives = len(
                statistic_df[statistic_df['country_outcome'] == "Negative"])
            country_indeterminates = len(
                statistic_df[statistic_df['country_outcome'] ==
                             "Indeterminate"])

            city_positives = len(
                statistic_df[statistic_df['city_outcome'] == "Positive"])
            city_negatives = len(
                statistic_df[statistic_df['city_outcome'] == "Negative"])
            city_indeterminates = len(
                statistic_df[statistic_df['city_outcome'] == "Indeterminate"])

            aggregation_df = pd.concat(
                [pd.DataFrame([[
                    statistic_file,
                    100 * (country_positives / total),
                    100 * (country_negatives / total),
                    100 * (country_indeterminates / total),
                    country_positives,
                    country_negatives,
                    country_indeterminates,
                    100 * (city_positives / total),
                    100 * (city_negatives / total),
                    100 * (city_indeterminates / total),
                    city_positives,
                    city_negatives,
                    city_indeterminates,
                ]], columns=aggregation_df.columns,
                ), aggregation_df],
                ignore_index=True
            )

        aggregation_df.to_csv(HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
                              "aggregation_results.csv", sep=",")


statistics = Statistics("validation_unicast_udp_ripe_20230531_1",
                        "validation_unicast_udp_ripe_20230531_1_no_check_multi_ip_target")
#statistics.hunter_build_statistics_validation_campaign()
statistics.aggregate_hunter_statistics()


