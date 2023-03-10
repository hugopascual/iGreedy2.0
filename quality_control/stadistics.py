#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def global_instances_check(gt: dict, results: dict):
    results_countries = set(results.keys())
    gt_countries = set(gt.keys())

    true_positive_countries = results_countries.intersection(gt_countries)
    false_positive_countries = results_countries.difference(gt_countries)
    false_negative_countries = gt_countries.difference(results_countries)

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
    print()
    print("""
Definiciones:
True Positive: País en el que se ha detectado alguna instancia anycast y 
ese país está en el GT. Intersección entre Resultados y GT.

False Positive: País en el que se ha detectado alguna instancia anycast y no
hay ninguna según el GT. Resultados - GT

Fasle Negative: País que el GT marca con alguna instancia anycast y no se ha 
detectado. GT - Resultados
    """)