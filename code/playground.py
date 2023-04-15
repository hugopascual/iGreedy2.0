#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import shapely
from shapely.geometry import MultiPolygon, Polygon, box, MultiPoint, Point, shape
from shapely import wkt
from shapely import from_geojson, GeometryCollection
from utils.common_functions import (
    json_file_to_list,
    dict_to_json_file,
    json_file_to_dict
)


def generate_new_probes_set_using_countries():
    probes_set = {"probes": []}
    num_probes_per_country = [5, 10, 15]
    countries_array = json_file_to_list(
        "../datasets/countries_sets/North-Central_countries.json")
    alpha2_codes = []
    for country in countries_array:
        alpha2_codes.append(country["alpha-2"])

    for num_probes in num_probes_per_country:
        for code in alpha2_codes:
            probes_set["probes"].append({
                "requested": num_probes,
                "type": "country",
                "value": code
            })

        dict_to_json_file(
            dict=probes_set,
            file_path="../datasets/probes_sets/Europe_countries_{}.json".
            format(num_probes))
        probes_set = {"probes": []}

def map_grid():
    topLeft = {
        "latitude": 40.04722222,
        "longitude": 116.17944444
    }
    bottomRight = {
        "latitude": 39.7775,
        "longitude": 116.58888889
    }

    longitudes_cols = np.linspace(topLeft["longitude"], bottomRight["longitude"], num=10)
    latitudes_rows = np.linspace(topLeft["latitude"], bottomRight["latitude"], num=10)
    areas = pd.DataFrame(columns=["area",
                                  "top_left_latitude",
                                  "top_left_longitude",
                                  "bottom_right_latitude",
                                  "bottom_left_longitude"])
    areas = pd.concat(
        [pd.DataFrame([[
            "sub_area"
        ]], columns=areas.columns),
            areas],
        ignore_index=True)


def get_geometries(top_left, bottom_right, spacing=0.08):
    polygons = []
    points = []
    xmin = top_left[0]
    xmax = bottom_right[0]
    ymax = top_left[1]
    y = bottom_right[1]
    i = -1
    while True:
        if y > ymax:
            break
        x = xmin

        while True:
            if x > xmax:
                break

            # components for polygon grid
            polygon = box(x, y, x + spacing, y + spacing)
            polygons.append(polygon)

            # components for point grid
            point = Point(x, y)
            points.append(point)
            i = i + 1
            x = x + spacing

        y = y + spacing
    return polygons, points


def test_docu():
    polygons, points = get_geometries((14, 54), (24, 49), 0.5)

    ##country_geom is a shapely polygon with country boundaries
    country_geom = wkt.loads(
        'POLYGON((17.564247434051406 54.446991320181255,16.311806027801406 54.061910892199705,15.575722043426405 53.37933926382691,15.377968137176405 52.79871812523439,15.575722043426405 51.98076121960815,15.619667355926405 51.15448239676194,16.696327512176406 50.94037053252475,17.871864621551406 50.47422670556861,18.761757199676406 50.27102433369101,21.54709245171919 50.3018762188395,22.28317643609419 50.31590902034586,23.19504167046919 51.019189209157204,22.65671159234419 52.08481472438036,22.79953385796919 52.86108007657073,22.48237015280161 53.76537437170607,22.24067093405161 54.11458487224089,20.402314605750536 54.24318115411181,18.908173980750536 54.09526092933704,18.007295074500536 54.396969300395,17.564247434051406 54.446991320181255))')

    intersecting_polygons = []
    intersecting_points = []
    for polygon in polygons:
        if polygon.intersects(country_geom):
            intersecting_polygons.append(polygon)

    for point in points:
        if country_geom.contains(point):
            intersecting_points.append(point)

    polygon_grid = MultiPolygon(intersecting_polygons)
    point_grid = MultiPoint(intersecting_points)
    print(point_grid)

    longitudes = []
    latitudes = []
    areas = []
    for polygon in list(polygon_grid.geoms):
        bounds = polygon.bounds
        print(polygon)
        areas.append({
            "longitude_min": bounds[0],
            "latitude_min": bounds[1],
            "longitude_max": bounds[2],
            "latitude_max": bounds[3]
        })

        polygon_ext_coords_x, polygon_ext_coords_y = polygon.exterior.coords.xy
        longitudes = longitudes + polygon_ext_coords_x.tolist()
        latitudes = latitudes + polygon_ext_coords_y.tolist()
    print(areas)
    fig = go.Figure(data=go.Scattergeo(
        lon=longitudes,
        lat=latitudes,
        mode='markers'
    ))
    fig.update_layout(
        title='Test Mesh'
    )
    fig.show()


def get_borders_good():
    selected_countries = get_selected_countries_borders(
        "../datasets/countries_sets/North-Central_countries.json")
    features = selected_countries["features"]
    # NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
    countries_geometry_collection = GeometryCollection(
        [shape(feature["geometry"]).buffer(0) for feature in features])

    north_central = {
        "top_left_latitude": 90,
        "top_left_longitude": -30,
        "bottom_right_latitude": 30,
        "bottom_right_longitude": 45
    }
    ww = {
        "top_left_latitude": 90,
        "top_left_longitude": -180,
        "bottom_right_latitude": -90,
        "bottom_right_longitude": 180
    }
    area_polygons, area_points = get_geometries(
        (ww["top_left_longitude"], ww["top_left_latitude"]),
        (ww["bottom_right_longitude"], ww["bottom_right_latitude"]),
        1)

    intersecting_polygons = []
    for polygon in area_polygons:
        if polygon.intersects(countries_geometry_collection):
            intersecting_polygons.append(polygon)

    polygon_grid = MultiPolygon(intersecting_polygons)
    plot_multipolygon(polygon_grid)


def get_area_of_polygon(polygon: shapely.Polygon) -> dict:
    bounds = polygon.bounds
    return {
        "longitude_min": bounds[0],
        "latitude_min": bounds[1],
        "longitude_max": bounds[2],
        "latitude_max": bounds[3]
    }


def plot_multipolygon(multipolygon: shapely.MultiPolygon):
    longitudes = []
    latitudes = []
    for polygon in list(multipolygon.geoms):
        polygon_ext_coords_x, polygon_ext_coords_y = polygon.exterior.coords.xy
        longitudes = longitudes + polygon_ext_coords_x.tolist()
        latitudes = latitudes + polygon_ext_coords_y.tolist()

    fig = go.Figure(data=go.Scattergeo(
        lon=longitudes,
        lat=latitudes,
        mode='markers'
    ))
    #fig.update_geos(
    #    projection_type="natural earth"
    #)
    fig.update_layout(
        title='Test Mesh'
    )
    fig.show()


def plot_polygon(polygon: shapely.Polygon):
    longitudes = []
    latitudes = []

    polygon_ext_coords_x, polygon_ext_coords_y = polygon.exterior.coords.xy
    longitudes = longitudes + polygon_ext_coords_x.tolist()
    latitudes = latitudes + polygon_ext_coords_y.tolist()

    fig = go.Figure(data=go.Scattergeo(
        lon=longitudes,
        lat=latitudes,
        mode='markers'
    ))
    #fig.update_geos(
    #    projection_type="natural earth"
    #)
    fig.update_layout(
        title='Test Mesh'
    )
    fig.show()


def get_selected_countries_borders(country_set_filepath: str) -> dict:
    countries_names_set = set()
    countries_list = json_file_to_list(country_set_filepath)
    for country in countries_list:
        countries_names_set.add(country["name"])
    # Because some name issues find in Europe
    countries_names_set.update(["Russia", "United Kingdom"])

    countries_borders_file_path = "../datasets/UIA_Latitude_Longitude_Graticules_and_World_Countries_Boundaries.geojson"
    countries_borders_dict = json_file_to_dict(countries_borders_file_path)
    selected_features = []
    for country_border in countries_borders_dict["features"]:
        if country_border["properties"]["CNTRY_NAME"] in countries_names_set:
            selected_features.append(country_border)
    countries_borders_dict["features"] = selected_features

    return countries_borders_dict


get_borders_good()
