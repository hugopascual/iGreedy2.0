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


class iGreedyStatistics:

    def __init__(self,
                 validation_campaign_directory: str = None,
                 output_filename: str = None):
        self._validation_campaign_directory = validation_campaign_directory
        self._output_filename = output_filename

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
            "probe_selection", "probe_set_number",
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

            probe_set_name_division = result_dict["probes_filepath"].split(
                "/")[-1].split["_"]

            region = probe_set_name_division[0]

            if "section" in region:
                probe_selection = "mesh"
            else:
                probe_selection = "area"
            probe_set_number = float(".".join(
                map(str, probe_set_name_division[1].split("")[:-1])))

            validation_results_df = pd.concat(
                [pd.DataFrame([[
                    result_dict["target"],
                    result_dict["probes_filepath"].split("/")[-1],
                    probe_selection,
                    probe_set_number,
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

def get_statistics_igreedy():
    campaign_name = "{}_{}".format(
        "North-Central_validation_20230410", DISTANCE_FUNCTION_USED)
    igreedy_statistics = iGreedyStatistics(
        validation_campaign_directory=campaign_name,
        output_filename=campaign_name
    )
    igreedy_statistics.igreedy_build_statistics_validation_campaign()

get_statistics_igreedy()
