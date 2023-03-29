#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

import constants as Constants
from auxiliar import (
    get_alpha2_country_codes_from_file,
    distance,
    get_gt_intances_locations,
    get_results_intances_locations
)

NEAR_KM=100.0

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

+ Stadistics sets
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

+Stadistics metrics
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

def area_intances_check(gt_countries: set, results_countries: set, area: set) -> dict:
    # In code RS == results_countries
    # In code GT == gt_countries
    # In code ALL == all_countries
    all_countries = get_alpha2_country_codes_from_file(Constants.ALL_COUNTRIES_FILE_PATH)

    true_positive_countries = results_countries.intersection(gt_countries, area)
    false_positive_countries = results_countries.intersection(area) - gt_countries
    true_negative_countries = (area-gt_countries).intersection(area-results_countries)
    false_negative_countries = area.intersection(gt_countries) - results_countries

    tp = len(true_positive_countries)
    fp = len(false_positive_countries)
    tn = len(true_negative_countries)
    fn = len(false_negative_countries)

    # Outside area countries stadistics
    instances_outside_true_detected = (all_countries - area).intersection(
        results_countries, gt_countries)
    instances_outside_false_detected = (all_countries - area).intersection(
        results_countries) - gt_countries
    
    stadistics = dict()

    stadistics["true_positives"] = tp
    stadistics["false_positives"] = fp
    stadistics["true_negatives"] = tn
    stadistics["false_negatives"] = fn
    stadistics["accuracy"] = ((tp+tn)/(tp+fp+tn+fn))*100
    stadistics["precision"] = ((tp)/(tp+fp))*100
    stadistics["recall"] = ((tp)/(tp+fn))*100

    stadistics["sets"] = {
        "results_countries": sorted(results_countries),
        "ground_truth_countries": sorted(gt_countries),
        "area_countries": sorted(area), 
        "true_positive_countries": sorted(true_positive_countries),
        "false_positive_countries": sorted(false_positive_countries),
        "true_negative_countries": sorted(true_negative_countries),
        "false_negative_countries": sorted(false_negative_countries),
        "instances_outside_true_detected": sorted(instances_outside_true_detected),
        "instances_outside_false_detected": sorted(instances_outside_false_detected)
    }

    return stadistics


def print_city_gt_definitions():
    print("""########################################
# Definitions:
In this evaluation a positive is defined as a instance located near to the gt 
instance (less than 100km)

+ Stadistics sets
- True Positive: 
- False Positive: 
- True Negative: 
- False Negative:

+Stadistics metrics
- Accuracy: (TP+TN)/(TP+FP+TN+FN)
- Precision: (TP)/(TP+FP)
- Recall: (TP)/(TP+FN)

########################################""")
          
def city_intances_check(area: set):
    results_df = get_results_intances_locations()
    results_df = results_df[results_df["country_code"].isin(area)]
    gt_df = get_gt_intances_locations()        
    gt_df = gt_df[gt_df["country_code"].isin(area)]

    results_df["type"] = results_df.apply(lambda x: check_tp_and_fp_city(
        gt_df=gt_df, city_name=x.city, lat=x.latitude, lon=x.longitude), axis=1)
    
    gt_df["type"] = "FN"

    metrics = pd.concat([results_df, gt_df])
    
    metrics.sort_values(by=["country_code", "city"], inplace=True)
    metrics.to_csv("metrics.csv")

def check_tp_and_fp_city(gt_df, city_name: str, lat: float, lon: float):
    if city_name in gt_df.city.values:
        gt_df.drop(gt_df[gt_df.city == city_name].index, inplace=True)
        return "TP"
    else:
        gt_df["distance"] = gt_df.apply(
            lambda x: distance(a={"latitude":lat,
                                  "longitude":lon}, 
                               b={"latitude":x.latitude,
                                  "longitude":x.longitude}), 
            axis=1)
        num_instances_near = len(gt_df[(gt_df["distance"]<NEAR_KM)])
        gt_df.drop(gt_df[gt_df["distance"]<NEAR_KM].index, inplace=True)
        gt_df.drop(columns="distance", inplace=True)
        if num_instances_near == 0:
            return "FP"
        elif num_instances_near == 1:
            return "TP"
        else:
            return "NN"
        


area_north_central = get_alpha2_country_codes_from_file(Constants.NORTH_CENTRAL_COUNTRIES_FILE_PATH)
city_intances_check(area_north_central)