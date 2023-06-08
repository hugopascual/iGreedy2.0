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
    dict_to_json_file
)


class Statistics:

    def __init__(self,
                 validation_campaign_directory: str = None,
                 output_filename: str = None,
                 validate_target: bool = True):
        self._validation_campaign_directory = validation_campaign_directory
        self._output_filename = output_filename
        self._validate_target = validate_target

    def igreedy_build_statistics_validation_campaign(self):
        if not self._validation_campaign_directory or \
                not self._output_filename:
            print("No campaign name or output filename provided")
            return

        results_filenames = get_list_files_in_path(
            GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH +
            self._validation_campaign_directory)

        validation_results_df = pd.DataFrame(columns=[
            "target", "probes_file",
            "threshold", "alpha",
            "Accuracy", "Precision", "Recall", "F1",
            "distance_function", "filename"
        ])

        for result_filename in results_filenames:
            print(result_filename)
            result_dict = json_file_to_dict("{}/{}".format(
                GROUND_TRUTH_VALIDATIONS_CAMPAIGNS_PATH +
                self._validation_campaign_directory, result_filename)
            )

            validation_results_df = pd.concat(
                [pd.DataFrame([[
                    result_dict["target"],
                    result_dict["probes_filepath"].split("/")[-1],
                    result_dict["threshold"],
                    result_dict["alpha"],
                    result_dict["statistics"]["accuracy"],
                    result_dict["statistics"]["precision"],
                    result_dict["statistics"]["recall"],
                    result_dict["statistics"]["f1"],
                    result_dict["ping_radius_function"],
                    result_filename,
                ]], columns=validation_results_df.columns,
                ), validation_results_df],
                ignore_index=True
            )

        validation_results_df.sort_values(
            by=["target", "probes_file", "threshold", "alpha"],
            inplace=True
        )

        csv_name = "{}{}{}{}".format(
            GT_VALIDATIONS_STATISTICS,
            "statistics_",
            self._output_filename,
            ".csv"
        )

        validation_results_df.to_csv(csv_name, sep=",", index=False)

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
            print(result_filename)
            result_dict = json_file_to_dict("{}/{}".format(
                HUNTER_MEASUREMENTS_CAMPAIGNS_PATH +
                self._validation_campaign_directory, result_filename)
            )

            if not result_dict["gt_info"]:
                results_not_valid.append(result_filename)
                continue

            outcome_country = self.calculate_hunter_result_outcome(
                result_dict, "country")
            outcome_city = self.calculate_hunter_result_outcome(
                result_dict, "city")

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
            sep=",",
            index=False
        )

        dict_to_json_file(
            results_not_valid,
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
            "results_not_valid/results_not_valid_" +
            self._output_filename + ".json")

    def calculate_hunter_result_outcome(self, results: dict, param: str) -> \
            (str, str):
        if param == "city":
            result_param = "cities"
            gt_param = "city"
        elif param == "country":
            result_param = "countries"
            gt_param = "country_code"
        else:
            print("Outcome param not valid")
            return "Indeterminate", "Not calculated"

        print("Param: {} Result_param: {} GT_param: {}".format(
            param, result_param, gt_param
        ))

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
            if results["gt_info"][gt_param] == \
                    results["hunt_results"][result_param][0]:
                return "Positive", "Same result airport"
            else:
                return "Negative", "Different result airport"
        elif num_result_countries == 0:
            centroid = from_geojson(results["hunt_results"]["centroid"])
            if not results["last_hop"]["ip"]:
                return "Indeterminate", "Last hop not valid"
            elif not results["discs_intersect"]:
                return "Indeterminate", "Ping discs no intersection"
            elif not centroid:
                return "Indeterminate", "Centroid not found"
            else:
                nearest_airport = get_nearest_airport_to_point(centroid)
                if results["gt_info"][gt_param] == \
                        nearest_airport[gt_param]:
                    return "Positive", "Same result in nearest airport"
                else:
                    return "Negative", "Different result in nearest airport"
        else:
            return "Indeterminate", "Too many results"

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

        aggregation_df.to_csv(
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
            "aggregation_results.csv",
            sep=",",
            index=False
        )


def get_statistics_hunter():
    hunter_campaigns = [
        "validation_anycast_udp_cloudfare_0_20230606_ip_last_hop_validation",
        "validation_anycast_udp_cloudfare_1_20230607"
    ]

    for hunter_campaign in hunter_campaigns:
        for validate_target in [True, False]:
            campaign_name = "_".join(
                map(str, hunter_campaign.split("_")[:6]))
            additional_to_name = "_".join(
                map(str, hunter_campaign.split("_")[6:]))
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

            output_filename = campaign_name + "_" + validation_name
            hunter_campaign_statistics = Statistics(
                validation_campaign_directory=hunter_campaign,
                output_filename=output_filename,
                validate_target=validate_target
            )
            hunter_campaign_statistics.\
                hunter_build_statistics_validation_campaign()

    statistics = Statistics()
    statistics.aggregate_hunter_statistics_country()


def get_statistics_igreedy():
    campaign_name = "{}_{}".format(
        "North-Central_validation_20230410", DISTANCE_FUNCTION_USED)
    igreedy_statistics = Statistics(
        validation_campaign_directory=campaign_name,
        output_filename=campaign_name
    )
    igreedy_statistics.igreedy_build_statistics_validation_campaign()


#get_statistics_hunter()
get_statistics_igreedy()
