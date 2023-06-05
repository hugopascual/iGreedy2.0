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
                 validation_campaign_directory: str = None,
                 output_filename: str = None,
                 validate_target: bool = True):
        self._validation_campaign_directory = validation_campaign_directory
        self._output_filename = output_filename,
        self._validate_target = validate_target

    def igreedy_build_statistics_validation_campaign(self):
        if (not self._validation_campaign_directory) or (
                not self._output_filename):
            print("No campaign name or output filename provided")
            return
        return

    def hunter_build_statistics_validation_campaign(self):
        if (not self._validation_campaign_directory) or (
                not self._output_filename):
            print("No campaign name or output filename provided")
            return

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
            "results_not_valid/results_not_valid_" +
            self._output_filename + ".json")

    # Auxiliary functions
    def calculate_hunter_result_outcome_country(self, results: dict) -> \
            (str, str):
        if self._validate_target:
            try:
                if len(results["hops_directions_list"][-1]) != 1:
                    return "Indeterminate", "Multiples IP on target hop"
                elif results["hops_directions_list"][-1] == "*":
                    return "Indeterminate", "Target hop do not respond"
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
        if self._validate_target:
            try:
                if len(results["hops_directions_list"][-1]) != 1:
                    return "Indeterminate", "Multiples IP on target hop"
                elif results["hops_directions_list"][-1] == "*":
                    return "Indeterminate", "Target hop do not respond"
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

    def aggregate_hunter_statistics_country(self):
        statistics_files = [filename for filename in
                            get_list_files_in_path(
                                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH)
                            if "statistics" in filename]
        aggregation_df = pd.DataFrame(columns=[
            "filename",
            "country_positives", "country_negatives", "country_indeterminates"
        ])
        for statistic_file in statistics_files:
            statistic_df = pd.read_csv(
                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + statistic_file)

            country_positives = len(
                statistic_df[statistic_df['country_outcome'] == "Positive"])
            country_negatives = len(
                statistic_df[statistic_df['country_outcome'] == "Negative"])
            country_indeterminates = len(
                statistic_df[statistic_df['country_outcome'] ==
                             "Indeterminate"])

            aggregation_df = pd.concat(
                [pd.DataFrame([[
                    statistic_file,
                    country_positives,
                    country_negatives,
                    country_indeterminates
                ]], columns=aggregation_df.columns,
                ), aggregation_df],
                ignore_index=True
            )

        aggregation_df.to_csv(HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
                              "aggregation_results.csv", sep=",")


hunter_campaigns = [
    "validation_anycast_udp_cloudfare_20230525_0_no_check_multi_ip_last_hop",
    "validation_anycast_udp_cloudfare_20230529_1",
    "validation_anycast_udp_cloudfare_20230529_2",
    "validation_anycast_udp_cloudfare_20230530_3_no_check_multi_ip_last_hop",
    "validation_unicast_udp_ripe_20230531_0_no_check_multi_ip_last_hop",
    "validation_unicast_udp_ripe_20230531_1"
]

for hunter_campaign in hunter_campaigns:
    for validate_target in [True, False]:
        campaign_name = "_".join(map(str, hunter_campaign.split("_")[:6]))
        additional_to_name = "_".join(map(str, hunter_campaign.split("_")[6:]))
        if validate_target:
            if not additional_to_name:
                validation_name = "ip_target_validation"
            else:
                validation_name = "ip_all_validation"
        else:
            if not additional_to_name:
                validation_name = "no_ip_validation"
            else:
                validation_name = additional_to_name

        output_filename = campaign_name + validation_name
        hunter_campaign_statistics = Statistics(
            validation_campaign_directory=hunter_campaign,
            output_filename=output_filename,
            validate_target=validate_target
        )
        hunter_campaign_statistics.\
            hunter_build_statistics_validation_campaign()

#statistics = Statistics()
#statistics.aggregate_hunter_statistics_country()


