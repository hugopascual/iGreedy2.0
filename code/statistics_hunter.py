#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
from shapely import Point
from shapely import from_geojson
# internal modules imports
from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
    HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH,
    GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH,
    GT_VALIDATIONS_STATISTICS,
    DISTANCE_FUNCTION_USED
)
from utils.common_functions import (
    get_list_files_in_path,
    json_file_to_dict,
    get_nearest_airport_to_point,
    dict_to_json_file,
    get_list_folders_in_path,
    countries_set_in_EEE
)


class HunterStatistics:

    def __init__(self,
                 validation_campaign_directory: str = None,
                 validation: str = "no_ip_validation"):
        self._validation_campaign_directory = validation_campaign_directory
        self._validation = validation
        if self._validation_campaign_directory:
            campaing_directory_split = validation_campaign_directory.split("_")
            campaing_directory_split.insert(-2, self._validation)
            self._output_filename = "_".join(
                map(str, campaing_directory_split)
            )
        else:
            self._output_filename = "no_campaign_name"
        # Possible values for validation
        # ip_all_validation, ip_target_validation, ip_last_hop_validation, no_ip_validation
        self._validate_target = (validation == "ip_target_validation")
        self._validate_last_hop = (validation == "ip_last_hop_validation")
        self._validate_none = (validation == "no_ip_validation")

        if validation == "ip_all_validation":
            self._validate_target = True
            self._validate_last_hop = True

    def hunter_build_statistics_validation_campaign(self):
        if not self._validation_campaign_directory:
            print("No campaign name or output filename provided")
            return

        results_filenames = get_list_files_in_path(
            HUNTER_MEASUREMENTS_CAMPAIGNS_PATH +
            self._validation_campaign_directory)
        validation_results_df = pd.DataFrame(columns=[
            "filename",
            "num_countries", "num_cities", "num_airports",
            "country_outcome", "country_outcome_reason",
            "city_outcome", "city_outcome_reason",
            "from_host", "target",
            "origin_country", "gt_country", "gt_city",
            "result_country", "result_city"
        ])

        results_not_gt = []

        for result_filename in results_filenames:
            result_dict = json_file_to_dict("{}/{}".format(
                HUNTER_MEASUREMENTS_CAMPAIGNS_PATH +
                self._validation_campaign_directory, result_filename)
            )

            if not result_dict["gt_info"]:
                results_not_gt.append(result_filename)
                continue

            outcome_country = self.calculate_hunter_result_outcome(
                result_dict, "country")
            outcome_city = self.calculate_hunter_result_outcome(
                result_dict, "city")

            origin_country = result_filename.split("_")[-1].split(".")[0]
            gt_country = result_dict["gt_info"]["country_code"]
            gt_city = result_dict["gt_info"]["city"]

            validation_results_df = pd.concat(
                [pd.DataFrame([[
                    result_filename,
                    len(result_dict["hunt_results"]["countries"]),
                    len(result_dict["hunt_results"]["cities"]),
                    len(result_dict["hunt_results"]["airports_located"]),
                    outcome_country[0],
                    outcome_country[1],
                    outcome_city[0],
                    outcome_city[1],
                    result_dict["traceroute_from_host"],
                    result_dict["target"],
                    origin_country,
                    gt_country,
                    gt_city,
                    outcome_country[2],
                    outcome_city[2]
                ]], columns=validation_results_df.columns,
                ), validation_results_df],
                ignore_index=True
            )

        validation_results_df.sort_values(
            by=["country_outcome", "country_outcome_reason", "filename"],
            inplace=True)
        validation_results_df.to_csv(
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + "statistics_" +
            self._output_filename + ".csv",
            sep=",",
            index=False
        )

        dict_to_json_file(
            results_not_gt,
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
            "results_not_valid/results_not_gt_" +
            self._validation_campaign_directory + ".json")

    def calculate_hunter_result_outcome(self, results: dict, param: str) -> \
            (str, str, str):
        if param == "city":
            result_param = "cities"
            gt_param = "city"
        elif param == "country":
            result_param = "countries"
            gt_param = "country_code"
        else:
            print("Outcome param not valid")
            return "Indeterminate", "Not calculated"

        if self._validate_last_hop:
            try:
                if len(results["hops_directions_list"][-2]) != 1:
                    return "Indeterminate", "Multiples IP on last_hop", \
                        "No result"
                elif results["hops_directions_list"][-1] == "*":
                    return "Indeterminate", "Last_hop hop do not respond", \
                        "No result"
            except:
                print("Target directions list exception")
                return "Indeterminate", "Exception in last_hop validation", \
                    "No result"

        if self._validate_target:
            try:
                if len(results["hops_directions_list"][-1]) != 1:
                    return "Indeterminate", "Multiples IP on target hop", \
                        "No result"
                elif results["hops_directions_list"][-1] == "*":
                    return "Indeterminate", "Target hop do not respond", \
                        "No result"
            except:
                print("Target directions list exception")
                return "Indeterminate", "Exception in target validation", \
                    "No result"

        # Num of results validation
        num_result_countries = len(results["hunt_results"]["countries"])
        if num_result_countries == 1:
            if results["gt_info"][gt_param] == \
                    results["hunt_results"][result_param][0]:
                return "Positive", "Same result airport", \
                    results["hunt_results"][result_param][0]
            else:
                return "Negative", "Different result airport", \
                    results["hunt_results"][result_param][0]
        elif num_result_countries == 0:
            centroid = from_geojson(results["hunt_results"]["centroid"])
            if not results["last_hop"]["ip"]:
                return "Indeterminate", "Last hop not valid", "No result"
            elif not results["last_hop"]["geolocation"]:
                return "Indeterminate", "Last hop not geolocated", "No result"
            elif not results["discs_intersect"]:
                return "Indeterminate", "Ping discs no intersection", \
                    "No result"
            elif not centroid:
                return "Indeterminate", "Centroid not found", "No Result"
            else:
                nearest_airport = get_nearest_airport_to_point(centroid)
                if results["gt_info"][gt_param] == \
                        nearest_airport[gt_param]:
                    return "Positive", "Same result in nearest airport", \
                        nearest_airport[gt_param]
                else:
                    return "Negative", "Different result in nearest airport", \
                        nearest_airport[gt_param]
        else:
            return "Indeterminate", "Too many locations", "No result"

    def aggregate_hunter_statistics_country(self):
        statistics_files = [filename for filename in
                            get_list_files_in_path(
                                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH)
                            if "statistics" in filename]
        aggregation_df = pd.DataFrame(columns=[
            "validation",
            "country_positives", "country_negatives", "country_indeterminates",
            "moment_of_campaign", "filename"
        ])
        for statistic_file in statistics_files:
            statistic_df = pd.read_csv(
                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + statistic_file)

            campaign_moment_split_list = statistic_file.split("_")[-2:]
            campaign_hour = campaign_moment_split_list[1].split(".")[0]
            campaign_date = "{}_{}".format(
                campaign_moment_split_list[0],
                campaign_hour
            )

            country_positives = len(
                statistic_df[statistic_df['country_outcome'] == "Positive"])
            country_negatives = len(
                statistic_df[statistic_df['country_outcome'] == "Negative"])
            country_indeterminates = len(
                statistic_df[statistic_df['country_outcome'] ==
                             "Indeterminate"])

            if "ip_target_validation" in statistic_file:
                validation_name = "ip_target_validation"
            elif "ip_all_validation" in statistic_file:
                validation_name = "ip_all_validation"
            elif "no_ip_validation" in statistic_file:
                validation_name = "no_ip_validation"
            elif "ip_last_hop_validation" in statistic_file:
                validation_name = "ip_last_hop_validation"
            else:
                validation_name = ""

            aggregation_df = pd.concat(
                [pd.DataFrame([[
                    validation_name,
                    country_positives,
                    country_negatives,
                    country_indeterminates,
                    campaign_date,
                    statistic_file
                ]], columns=aggregation_df.columns,
                ), aggregation_df],
                ignore_index=True
            )

        aggregation_df.sort_values(by=[
            "moment_of_campaign", "validation"],
            inplace=True)
        aggregation_df.to_csv(
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
            "aggregation_results.csv",
            sep=",",
            index=False
        )

    def check_jumps_between_countries(self):
        statistics_files = [filename for filename in
                            get_list_files_in_path(
                                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH)
                            if ("statistics" in filename) and
                            ("ip_all_validation" in filename)]
        jumps_df = pd.DataFrame(columns=[
            "total_checks", "number_jumps", "jumps_out_EEE",
            "moment_of_campaign", "filename"
        ])

        countries_EEE_set = countries_set_in_EEE()

        for statistic_file in statistics_files:
            statistic_df = pd.read_csv(
                HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + statistic_file)

            statistic_df["country_jump"] = statistic_df.apply(
                lambda row: not(row["origin_country"] != row["gt_country"]),
                axis=1
            )
            statistic_df["jump_out_EEE"] = statistic_df["gt_country"].apply(
                lambda destination_country:
                destination_country not in countries_EEE_set
            )

            campaign_moment_split_list = statistic_file.split("_")[-2:]
            campaign_hour = campaign_moment_split_list[1].split(".")[0]
            campaign_date = "{}_{}".format(
                campaign_moment_split_list[0],
                campaign_hour
            )

            number_jumps = statistic_df["country_jump"].value_counts()[
                bool(True)
            ]
            jumps_out_EEE = statistic_df["jump_out_EEE"].value_counts()[
                bool(True)
            ]

            jumps_df = pd.concat([
               pd.DataFrame([[
                   len(statistic_df.index),
                   number_jumps,
                   jumps_out_EEE,
                   campaign_date,
                   statistic_file
               ]], columns=jumps_df.columns
               ), jumps_df], ignore_index=True)

        jumps_df.sort_values(by=[
            "moment_of_campaign"],
            inplace=True)
        jumps_df.to_csv(
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
            "jumps_results.csv",
            sep=",",
            index=False
        )


hunter_campaigns_folders = get_list_folders_in_path(
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH)
hunter_campaigns = [folder for folder in hunter_campaigns_folders
                    if not ("statistics" in folder)]
validation_mods = ["ip_all_validation",
                   "ip_target_validation",
                   "ip_last_hop_validation",
                   "no_ip_validation"]
for hunter_campaign in hunter_campaigns:
    for validation in validation_mods:
        print("##################")
        print(validation)
        print(hunter_campaign)
        print("##################")
        hunter_campaign_statistics = HunterStatistics(
            validation_campaign_directory=hunter_campaign,
            validation=validation
        )
        hunter_campaign_statistics.\
            hunter_build_statistics_validation_campaign()

statistics = HunterStatistics()
statistics.aggregate_hunter_statistics_country()
statistics.check_jumps_between_countries()
