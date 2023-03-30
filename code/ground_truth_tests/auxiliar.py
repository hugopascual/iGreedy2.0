#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
import math
import pandas as pd

def json_file_to_dict(file_path: str) -> dict:
    with open(file_path) as file:
        raw_json = file.read()
    
    return json.loads(raw_json)

def dict_to_json_file(dict: dict, file_path: str):
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4))
    file.close()

def list_to_json_file(dict: list, file_path: str):
    file = open(file_path, "w")
    file.write(json.dumps(dict, indent=4))
    file.close()

def get_alpha2_country_codes_from_file(filename: str) -> set:
    country_codes = set()
    countries_list = json_file_to_dict(filename)
    for country in countries_list:
        country_codes.add(country["alpha-2"])
    return country_codes

def list_of_dicts_to_csv(list: list, filepath: str):
    
    keys = list[0].keys()

    with open(filepath, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list)

def distance(a: dict, b: dict) -> float: 
    lat1 = a["latitude"]
    lat2 = b["latitude"]
    lon1 = a["longitude"]
    lon2 = b["longitude"]

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = lon1*degrees_to_radians
    theta2 = lon2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
            math.cos(phi1)*math.cos(phi2))
    if (abs(cos - 1.0) <0.000000000000001):
        arc=0.0   
    else:
        arc = math.acos( cos )
        
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    earth_radius_km = 6371
    return arc*earth_radius_km

def get_results_intances_locations():
    filepath = "results/campaigns/20230324/North-Central_1000_192.5.5.241_1.0.json" 
    anycast_instances = json_file_to_dict(filepath)["anycast_intances"]
    markers = []
    for instance in anycast_instances:
        markers.append(instance["marker"])
    
    df = pd.DataFrame(markers)
    df = df[["code_country", "city", "latitude", "longitude"]]
    df.rename(
        columns={
        "code_country": "country_code"},
        inplace=True)
    df["type"] = "result_instance"

    return df

def get_gt_intances_locations():
    filepath = "datasets/ground-truth/root_servers/root_servers_F.json" 
    
    df = pd.DataFrame(json_file_to_dict(filepath)["Sites"])
    df = df[["Country", "Town", "Latitude", "Longitude" ]]
    df.rename(
        columns={
        "Country": "country_code", 
        "Town": "city", 
        "Latitude": "latitude", 
        "Longitude": "longitude"},
        inplace=True)
    df.drop_duplicates(subset=['city'], inplace=True)
    df["type"] = "gt_instance"

    return df