#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import constants as Constants
from auxiliar import (
    get_alpha2_country_codes_from_file
)

def print_global_gt_definitions():
    print("""########################################
# Definitions:
In this evaluation a positive is defined as a country with a anycast instance.

+ Sets
- RS: Set of countries where iGreedy has detected an anycast instance.
- GT: Set of countries with at least one known anycast instance.
- ALL: Set of all countries.

+ Stadistics sets
- True Positive: Countries with a known and detected anycast instance.
Operation: Intersection(RS, GT)
- False Positive: Countries with a detected anycast instance that does not have 
any known anycast instance.
Operation: RS - GT
- True Negative: Countries without a known and detected anycast instance.
Operation: Intersection((ALL-RS), (ALL-GT))
- False Negative: Countries with a known anycast instance that does not have 
any detected anycast instance.
Operation: GT - RS
########################################""")

def global_instances_check(gt: dict, results: dict):
    # In code RS == results_countries
    results_countries = set(results.keys())
    # In code GT == gt_countries
    gt_countries = set(gt.keys())
    # In code ALL == all_countries
    all_countries = get_alpha2_country_codes_from_file(Constants.ALL_COUNTRIES_FILE_PATH)

    true_positive_countries = results_countries.intersection(gt_countries)
    false_positive_countries = results_countries.difference(gt_countries)
    false_negative_countries = gt_countries.difference(results_countries)

    # Print results
    print("Ground Truth countries number: %1.0f" %len(gt_countries))
    print(gt_countries)
    print("Results countries number: %1.0f" %len(results_countries))
    print(results_countries)
    print("True Positives: {0:d}. That is a {1:1.2f}%.".format(
        len(true_positive_countries), 
        (len(true_positive_countries)/len(gt_countries))*100)
    )
    print(true_positive_countries)
    print("False Positives: {0:d}. That is a {1:1.2f}%.".format(
        len(false_positive_countries), 
        (len(false_positive_countries)/len(gt_countries))*100)
    )
    print(false_positive_countries)
    print("Fasle Negatives: {0:d}. That is a {1:1.2f}%.".format(
        len(false_negative_countries), 
        (len(false_negative_countries)/len(gt_countries))*100)
    )
    print(false_negative_countries)
    print("########################################")

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

def area_intances_check(gt: dict, results: dict, area: set):
    # In code RS == results_countries
    results_countries = set(results.keys())
    # In code GT == gt_countries
    gt_countries = set(gt.keys())
    # In code ALL == all_countries
    all_countries = get_alpha2_country_codes_from_file(Constants.ALL_COUNTRIES_FILE_PATH)

    true_positive_countries = results_countries.intersection(gt_countries, area)
    false_positive_countries = results_countries.intersection(area) - gt_countries
    true_negative_countries = (area-gt_countries).intersection(area-results_countries)
    false_negative_countries = area.intersection(gt) - results_countries

    # Print results
    print("Ground Truth countries number: %1.0f" %len(gt_countries))
    print(gt_countries)
    print("Results countries number: %1.0f" %len(results_countries))
    print(results_countries)

    print("True Positives: {0:d}. That is a {1:1.2f}%.".format(
        len(true_positive_countries), 
        (len(true_positive_countries)/len(gt_countries))*100)
    )
    print(true_positive_countries)

    print("False Positives: {0:d}. That is a {1:1.2f}%.".format(
        len(false_positive_countries), 
        (len(false_positive_countries)/len(gt_countries))*100)
    )
    print(false_positive_countries)

    print("True Negatives: {0:d}. That is a {1:1.2f}%.".format(
        len(true_negative_countries), 
        (len(true_negative_countries)/len(gt_countries))*100)
    )
    print(true_negative_countries)

    print("Fasle Negatives: {0:d}. That is a {1:1.2f}%.".format(
        len(false_negative_countries), 
        (len(false_negative_countries)/len(gt_countries))*100)
    )
    print(false_negative_countries)
    print("########################################")

    # Ouside area countries stadistics
    instances_outside_true_detected = (all_countries - area).intersection(
        results_countries, gt_countries)
    instances_outside_false_detected = (all_countries - area).intersection(
        results_countries) - gt_countries
    instances_outside_non_detected = (all_countries - area).intersection(
        gt_countries) - results_countries
    
    print("Countries outside area with instance detected: ")
    print(instances_outside_true_detected)
    print("Countries outside area with a false detected instance: ")
    print(instances_outside_false_detected)
    print("Countries outside area with instances not detected")
    print(instances_outside_non_detected)
