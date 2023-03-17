#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import constants as Constants
from auxiliar import (
    get_alpha2_country_codes
)

def print_global_gt_definitions():
    print("""########################################
# Definiciones:
+ Conjuntos
- RS: Conjunto de paises donde iGreedy ha detectado una instancia anycast.
- GT: Conjunto de paises donde hay al menos una instancia anycast conocida.
- ALL: Conjunto de todos los paises del mundo.

+ Estadisticas
- True Positive: País en el que se ha detectado alguna instancia anycast y 
ese país está en el GT. Intersección entre RS y GT.
- False Positive: País en el que se ha detectado alguna instancia anycast y no
hay ninguna según el GT. RS - GT
- True Negative: No se tiene en cuenta, porque serían todos aquellos paises en los
que no hay instancia anycast y no se detecta. Es un conjunto que no aporta nigún
valor a la medida. En todo caso se podría medir como: Intersección entre 
(ALL-GT) y (ALL-RS).
- False Negative: País que el GT marca con alguna instancia anycast y no se ha 
detectado. GT - RS
########################################""")

def global_instances_check(gt: dict, results: dict):
    # In code RS == results_countries
    results_countries = set(results.keys())
    # In code GT == gt_countries
    gt_countries = set(gt.keys())

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
# Definiciones:
+ Conjuntos
-RS: Conjunto de paises donde iGreedy ha detectado una instancia anycast.
-GT: Conjunto de paises donde hay al menos una instancia anycast conocida.
-ALL: Conjunto de todos los paises del mundo.
-AREA: Conjunto de paises dentro del area de selección de las probes.

+ Estadisticas
- True Positive: País dentro de AREA en el que se ha detectado alguna instancia 
anycast y ese país está en el GT. Intersección entre RS, GT y AREA.
- False Positive: País dentro del AREA en el que se ha detectado alguna instancia 
anycast y no hay ninguna según el GT. (Interseccion entre RS y AREA) - GT
- True Negative: Aquellos paises dentro del AREA en los que no hay instancia 
anycast y no se detecta. Intersección entre (AREA-GT) y (AREA-RS).
- False Negative: País dentro del AREA y que el GT marca con alguna instancia 
anycast y no se ha detectado. (Intersección entre GT y AREA) - RS

En el exterior del AREA puede que se detecten instancias por lo que se definen 
los siguientes conjuntos:
- INSTANCES_OUTSIDE_TRUE_DETECTED: Paises donde se detecta una instancia, no 
pertenecen al AREA y si estan en el GT. 
Intersección de (ALL - AREA), RS y GT.
- INSTANCES_OUTSIDE_FALSE_DETECTED: Paises donde se detecta una instancia, no 
pertenecen al AREA y no estan en el GT. 
(Intersección de (ALL - AREA) y RS) - GT.
- INSTANCES_OUTSIDE_NON_DETECTED: Paises fuera del AREA donde el GT indica que 
hay instancias anycast y no se han detectado. 
(Intersección de (ALL - AREA) y GT) - RS.
########################################""")

def area_intances_check(gt: dict, results: dict, area: set):
    # In code RS == results_countries
    results_countries = set(results.keys())
    # In code GT == gt_countries
    gt_countries = set(gt.keys())
    # In code ALL == all_countries
    all_countries = get_alpha2_country_codes(Constants.ALL_COUNTRIES_FILE_PATH)

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
