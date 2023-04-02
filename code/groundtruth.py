#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd

# internal modules imports
from utils.constants import (
    GROUND_TRUTH_VALIDATIONS_PATH,
    AREA_OF_INTEREST_FILEPATH,
    NEAR_CITY_TP_KM
)
from utils.functions import (
    json_file_to_dict,
    dict_to_json_file,
    distance
)


def get_alpha2_country_codes(filename: str) -> set:
    country_codes = set()
    countries_list = json_file_to_dict(filename)
    for country in countries_list:
        country_codes.add(country["alpha-2"])
    return country_codes


def get_results_instances_locations(filepath: str) -> pd.DataFrame:
    anycast_instances = json_file_to_dict(filepath)["anycast_instances"]
    markers = []
    for instance in anycast_instances:
        markers.append(instance["marker"])

    df = pd.DataFrame(markers)
    df = df[["country_code", "city", "latitude", "longitude"]]
    df["type"] = "result_instance"

    return df


def get_gt_instances_locations(filepath: str) -> pd.DataFrame:
    df = pd.DataFrame(json_file_to_dict(filepath)["Sites"])
    df = df[["Country", "Town", "Latitude", "Longitude"]]
    df.drop_duplicates(subset=['Town'], inplace=True)
    df.rename(
        columns={
            "Country": "country_code",
            "Town": "city",
            "Latitude": "latitude",
            "Longitude": "longitude"},
        inplace=True)
    df["type"] = "gt_instance"

    return df


def check_city_positive(gt_df, city_name: str, lat: float, lon: float):
    if city_name in gt_df.city.values:
        # Delete city from gt if a TP detected
        gt_df.drop(gt_df[gt_df.city == city_name].index, inplace=True)
        return "TP"
    else:
        # Calculate distance of result city to every other gt city
        # If distance is less than NEAR_CITY_TP_KM is a TP, if not is an FP
        gt_df["distance"] = gt_df.apply(
            lambda x: distance(a={"latitude": lat,
                                  "longitude": lon},
                               b={"latitude": x.latitude,
                                  "longitude": x.longitude}),
            axis=1)
        num_instances_near = len(gt_df[(gt_df["distance"] < NEAR_CITY_TP_KM)])
        if num_instances_near == 0:
            gt_df.drop(columns="distance", inplace=True)
            return "FP"
        else:
            # Delete city from gt if a TP detected
            gt_df.drop(gt_df[gt_df["distance"] < NEAR_CITY_TP_KM].index,
                       inplace=True)
            gt_df.drop(columns="distance", inplace=True)
            return "TP"


def calculate_performance_statistics(validation: pd.DataFrame) -> dict:
    tp = int(validation["type"].value_counts()["TP"])
    fp = int(validation["type"].value_counts()["FP"])
    tn = 0
    fn = int(validation["type"].value_counts()["FN"])

    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    statistics = {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "accuracy": (tp+tn)/(tp+fp+fn),
        "precision": precision,
        "recall": recall,
        "f1": 2*((precision*recall)/(precision+recall))
    }

    return statistics


def compare_to_gt(results_filepath: str, gt_filepath: str) -> None:
    area_of_interest = get_alpha2_country_codes(AREA_OF_INTEREST_FILEPATH)
    results_df = get_results_instances_locations(results_filepath)
    results_df = results_df[results_df["country_code"].isin(area_of_interest)]
    gt_df = get_gt_instances_locations(gt_filepath)
    gt_df = gt_df[gt_df["country_code"].isin(area_of_interest)]

    # Check for every city TP or FP
    results_df["type"] = results_df.apply(
        lambda x: check_city_positive(
            gt_df=gt_df,
            city_name=x.city,
            lat=x.latitude,
            lon=x.longitude),
        axis=1)

    # Remaining cities in GT are FN
    gt_df["type"] = "FN"

    instances_validated = pd.concat([results_df, gt_df])
    instances_validated.sort_values(by=["country_code", "city"], inplace=True)

    results_dict = json_file_to_dict(results_filepath)
    comparison_result = {
        "target": results_dict["target"],
        "probes_filepath": results_dict["probes_filepath"],
        "alpha": results_dict["alpha"],
        "threshold": results_dict["threshold"],
        "noise": results_dict["noise"],
        "results_filepath": results_filepath,
        "gt_filepath": gt_filepath,
        "statistics": calculate_performance_statistics(instances_validated),
        "instances": instances_validated.to_dict('records')
    }

    results_filename = results_filepath.split("/")[-1][:-5]
    gt_filename = gt_filepath.split("/")[-1][:-5]
    dict_to_json_file(dict=comparison_result,
                      file_path=GROUND_TRUTH_VALIDATIONS_PATH + "{}_{}.json"
                      .format(results_filename, gt_filename))
