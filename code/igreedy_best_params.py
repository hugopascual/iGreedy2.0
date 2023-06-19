#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from statistics import mean

from utils.constants import (
    GT_VALIDATIONS_STATISTICS,
    CLOUDFARE_IPS,
    ROOT_SERVERS
)


def first_try():
    igreedy_statistics_df = pd.read_csv(
        GT_VALIDATIONS_STATISTICS +
        "statistics_North-Central_validation_20230410.csv")

    # dataframe con los optimos de cada escenario
    optimal_params_df = pd.DataFrame()
    target_list = CLOUDFARE_IPS + list(ROOT_SERVERS.keys())

    for target in target_list:
        target_df = igreedy_statistics_df[
            igreedy_statistics_df["target"] == target]
        target_df = target_df[target_df["Precision"] == target_df["Precision"].max()]
        target_df = target_df[target_df["Recall"] == target_df["Recall"].max()]
        target_df = target_df[target_df["F1"] == target_df["F1"].max()]
        target_df = target_df[target_df["Accuracy"] == target_df["Accuracy"].max()]
        target_optimal = target_df
        target_optimal.sort_values(by=["threshold", "alpha"], inplace=True)

        optimal_params_df = pd.concat(
            [target_optimal, optimal_params_df], ignore_index=True)

    optimal_params_df.sort_values(by=["target", "threshold", "alpha"])
    optimal_params_df.to_csv(
        GT_VALIDATIONS_STATISTICS + "optimal_params_by_target.csv",
        sep=","
    )


def try_with_params_combinations(result_to_max: str):

    igreedy_statistics_df = pd.read_csv(
        GT_VALIDATIONS_STATISTICS +
        "statistics_North-Central_validation_20230410.csv")

    probe_selection_list = ["mesh", "area"]
    probe_set_number_list = [1, 1.5, 2, 100, 300, 500, 1000]
    threshold_list = [-1, 0.5, 1, 5, 10, 20, 30]
    alpha_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    distance_function_list = ["constant_1.52", "verloc_aprox"]

    target_list = CLOUDFARE_IPS + list(ROOT_SERVERS.keys())
    target_list.sort()
    #target_list = ["104.16.123.96"]

    df_colums = ["sum_error", "avg_error"] + ["probe_selection",
                                              "probe_set_number",
                                              "distance_function",
                                              "threshold",
                                              "alpha"] + target_list

    combinations_error_df = pd.DataFrame(
        columns=df_colums
    )

    target_max_list = []
    for target in target_list:
        max_precision_for_target = igreedy_statistics_df[
            igreedy_statistics_df["target"] == target
            ][result_to_max].max()
        target_max_list.append(max_precision_for_target)

    probes_combinations = [
        ("mesh", 1), ("mesh", 1.5), ("mesh", 2),
        ("area", 100), ("area", 300), ("area", 500), ("area", 1000)
    ]

    for distance_function in distance_function_list:
        for threshold in threshold_list:
            for alpha in alpha_list:
                for probes_combination in probes_combinations:
                    params = [
                        probes_combination[0],
                        probes_combination[1],
                        distance_function,
                        threshold,
                        alpha
                    ]
                    print(params)

                    result_for_params = get_list_of_result_for_params(
                        params=params,
                        df=igreedy_statistics_df,
                        result_to_max=result_to_max
                    )

                    error_list = [maximum - result for maximum, result in
                                  zip(target_max_list, result_for_params)]

                    avg_error = mean(error_list)
                    sum_error = sum(error_list)

                    list_to_concat = [sum_error, avg_error
                                      ] + params + error_list

                    combinations_error_df = pd.concat([
                        pd.DataFrame([list_to_concat],
                                     columns=combinations_error_df.columns),
                        combinations_error_df
                    ], ignore_index=True)

    combinations_error_df.sort_values(
        by=["sum_error", "avg_error"], inplace=True, ignore_index=True)
    combinations_error_df.to_csv(
        GT_VALIDATIONS_STATISTICS + "matrix_{}.csv".format(result_to_max),
        sep=",", index=False
    )


def get_list_of_result_for_params(
        params: list, df: pd.DataFrame, result_to_max: str) -> list:

    target_combination_df = df.loc[
        (df["probe_selection"] == params[0]) &
        (df["probe_set_number"] == params[1]) &
        (df["distance_function"] == params[2]) &
        (df["threshold"] == params[3]) &
        (df["alpha"] == params[4])
    ]

    result_for_combination = target_combination_df[result_to_max].values
    return result_for_combination


try_with_params_combinations(result_to_max="Precision")


