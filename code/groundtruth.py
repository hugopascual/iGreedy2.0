#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
# internal modules imports
from utils.constants import (
    GROUND_TRUTH_VALIDATIONS_PATH,
    ALL_COUNTRIES_FILE_PATH,
    AREA_OF_INTEREST_FILEPATH,
    NEAR_CITY_TP_KM
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file,
    distance
)


def compare_cities_gt(results_filepath: str, gt_filepath: str) -> str:
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
        "statistics": calculate_performance_statistics_cities(
            instances_validated),
        "instances": instances_validated.to_dict('records')
    }

    results_filename = results_filepath.split("/")[-1][:-5]
    gt_filename = gt_filepath.split("/")[-1][:-5]
    gt_validation_filepath = GROUND_TRUTH_VALIDATIONS_PATH + \
                             "{}_{}.json".format(results_filename, gt_filename)
    dict_to_json_file(dict=comparison_result,
                      file_path=gt_validation_filepath)

    return gt_validation_filepath


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


def compare_countries_gt(results_filepath: str, gt_filepath: str) -> None:
    results_countries = set()
    gt_countries = set()
    area_of_interest = get_alpha2_country_codes(AREA_OF_INTEREST_FILEPATH)
    all_countries = get_alpha2_country_codes(ALL_COUNTRIES_FILE_PATH)

    true_positive_countries = results_countries.intersection(
        gt_countries, area_of_interest)
    false_positive_countries = results_countries.intersection(
        area_of_interest) - gt_countries
    true_negative_countries = (area_of_interest - gt_countries).intersection(
        area_of_interest - results_countries)
    false_negative_countries = area_of_interest.intersection(
        gt_countries) - results_countries

    tp = len(true_positive_countries)
    fp = len(false_positive_countries)
    tn = len(true_negative_countries)
    fn = len(false_negative_countries)

    # Outside area countries statistics
    instances_outside_true_detected = (all_countries - area_of_interest).\
        intersection(results_countries, gt_countries)
    instances_outside_false_detected = (all_countries - area_of_interest).\
        intersection(results_countries) - gt_countries

    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    statistics = {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "accuracy": (tp+tn)/(tp+fp+tn+fn),
        "precision": precision,
        "recall": recall,
        "f1": 2 * ((precision * recall) / (precision + recall))
    }

    results_dict = json_file_to_dict(results_filepath)
    comparison_result = {
        "target": results_dict["target"],
        "probes_filepath": results_dict["probes_filepath"],
        "alpha": results_dict["alpha"],
        "threshold": results_dict["threshold"],
        "noise": results_dict["noise"],
        "results_filepath": results_filepath,
        "gt_filepath": gt_filepath,
        "statistics": statistics,
        "countries_sets": {
            "results_countries": sorted(results_countries),
            "ground_truth_countries": sorted(gt_countries),
            "area_countries": sorted(area_of_interest),
            "true_positive_countries": sorted(true_positive_countries),
            "false_positive_countries": sorted(false_positive_countries),
            "true_negative_countries": sorted(true_negative_countries),
            "false_negative_countries": sorted(false_negative_countries),
            "instances_outside_true_detected": sorted(
                instances_outside_true_detected),
            "instances_outside_false_detected": sorted(
                instances_outside_false_detected)
        }
    }

    results_filename = results_filepath.split("/")[-1][:-5]
    gt_filename = gt_filepath.split("/")[-1][:-5]
    dict_to_json_file(dict=comparison_result,
                      file_path=GROUND_TRUTH_VALIDATIONS_PATH + "{}_{}.json"
                      .format(results_filename, gt_filename))


def calculate_performance_statistics_cities(validation: pd.DataFrame) -> dict:
    try:
        tp = int(validation["type"].value_counts()["TP"])
    except: tp = 0
    try:
        fp = int(validation["type"].value_counts()["FP"])
    except: fp = 0
    try:
        tn = int(validation["type"].value_counts()["TN"])
    except: tn = 0
    try:
        fn = int(validation["type"].value_counts()["FN"])
    except: fn = 0

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


def get_countries_set_from_root_servers(filepath: str) -> set:
    root_servers_raw_data = json_file_to_dict(filepath)

    root_servers_set = set()
    for instance in root_servers_raw_data["Sites"]:
        root_servers_set.add(instance["Country"])
    return root_servers_set


def get_countries_set_from_results(filepath: str) -> set:
    results_raw_data = json_file_to_dict(filepath)

    result_set = set()
    for instance in results_raw_data["anycast_intances"]:
        result_set.add(instance["marker"]["country_code"])
    return result_set


def print_city_gt_definitions():
    print("""########################################
# Definitions:
In this evaluation a positive is defined as a instance located near to the gt 
instance (less than 100km)

+ Statistics sets
- True Positive: 
- False Positive: 
- True Negative: 
- False Negative:

+ Statistics metrics
- Accuracy: (TP+TN)/(TP+FP+TN+FN)
- Precision: (TP)/(TP+FP)
- Recall: (TP)/(TP+FN)

########################################""")


def print_area_gt_definitions():
    print("""########################################
# Definitions:
In this evaluation a positive is defined as a country in the probes area with a 
anycast instance.

+ Sets
- RS: Set of countries where iGreedy has detected an anycast instance.
- GT: Set of countries with at least one known anycast instance.
- ALL: Set of all countries.
- AREA: Set of countries of probes area.

+ Statistics sets
- True Positive: Countries inside the probes area with a known and detected 
anycast instance.
Operation: Intersection(AREA, RS, GT)
- False Positive: Countries inside the probes area with a detected anycast 
instance that does not have any known anycast instance.
Operation: Intersection(AREA, RS) - GT
- True Negative: Countries inside the probes area without a known and detected 
anycast instance.
Operation: Intersection((AREA-RS), (AREA-GT))
- False Negative: Countries inside the probes area with a known anycast instance
that does not have any detected anycast instance.
Operation: Intersection(AREA, GT) - RS

+ Statistics metrics
- Accuracy: (TP+TN)/(TP+FP+TN+FN)
- Precision: (TP)/(TP+FP)
- Recall: (TP)/(TP+FN)

It could be possible that iGreedy detects a anycast instance outside the probes 
area. This cases could be interesting to known and present, for this reason the 
following sets are defined.
- INSTANCES_OUTSIDE_TRUE_DETECTED: Countries outside the probes area with a 
known and detected anycast instance.
Operation: Intersection((ALL - AREA), RS, GT)
- INSTANCES_OUTSIDE_FALSE_DETECTED: Countries outside the probes area with a 
detected anycast instance that does not have any known anycast instance.
Operation: Intersection((ALL - AREA), RS) - GT.
########################################""")
