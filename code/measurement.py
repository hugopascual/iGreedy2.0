#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# helper functions to launch RIPE Atlas measurement  (./igreedy -m)
#---------------------------------------------------------------------.

# external modules imports
import json
import random
import sys
import socket
import requests
from shapely.geometry import(
    MultiPolygon,
    Polygon,
    box,
    shape,
    GeometryCollection
)
import ast
# internal modules imports
from utils.constants import (
    MEASUREMENTS_PATH,
    MEASUREMENTS_CAMPAIGNS_PATH,
    COUNTRY_BORDERS_GEOJSON_FILEPATH
)
from utils.common_functions import (
    dict_to_json_file,
    json_file_to_dict,
    get_section_borders_of_polygon,
    is_probe_inside_section
)
from visualize import (
    plot_multipolygon
)
import RIPEAtlas

class Measurement(object):
    def __init__(self, ip, ripe_probes=None, mesh_area=None):

        if(self.checkIP(ip)):
            self._ip = ip
        else:
            print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
            sys.exit(1)
        self._ripeProbes = ripe_probes
        self._mesh_area = mesh_area
        self._numberOfPacket = 2 #to improve
        self._numberOfProbes = 5 #to improve, introduce as parameter, in alternative to the list of probes
        self._measurement = None
        self.result = None
        self._ripe_probes_geo = {}

        self._percentageSuccessful = 0.8

        self._probes_filepath = None
        self._probes_filename = None
        self._measurement_filename = None

    def getIP(self):
        return self._ip

    def getRipeProbes(self):
        return self._ripeProbes

    def get_measurement_id(self):
        return self._measurement.id

    def checkIP(self,str):
        try:
            addr = socket.inet_pton(socket.AF_INET6, str)
        except socket.error: # not a valid IPv6 address
            try:
                addr = socket.inet_pton(socket.AF_INET, str)
            except socket.error: # not a valid IPv4 address either
                return False
        return True

    def loadProbes(self,pathVPs=None):
        temp_list_probes=[]
        temp_information_probes={}
        if pathVPs is None:
            pathVPs = "./datasets/ripe-vps"

        tempInformationProbes={}
        tempListProbes=[]
        for line in open(pathVPs,'r').readlines():
            if line.startswith("#"): #skip header and comments
                continue
            hostname,latitude,longitude = line.strip().split("\t")
            temp_list_probes.append(hostname)
            temp_information_probes[hostname]=[latitude,longitude]
        self._numberOfProbes=len(temp_list_probes)

        print("Information retrived of probes")
        print(temp_information_probes)

        return (",".join(temp_list_probes),temp_information_probes) #building the list

    def load_data_request(self, probes_file):
        data = {
            "definitions": [
                {
                    "target": self._ip,
                    "description": "Ping %s" % self._ip,
                    "type": "ping",
                    "is_oneoff": True,
                    "packets": self._numberOfPacket,
                    "af": 4
                }
            ]
        }

        if ":" in self._ip:
            af = 6
        else:
            af = 4
        data["definitions"][0]['af'] = af
        self.build_probes_object(probes_file)
        data["probes"] = self._ripeProbes["probes"]
        return data

    def build_probes_object(self, probes_file):
        probes_info = json_file_to_dict(probes_file)
        self._probes_filepath = probes_file
        self._probes_filename = probes_file.split("/")[-1][:-5]
        if "probes_per_section" in probes_info.keys():
            # Build probes object from an area
            self._mesh_area = ast.literal_eval(probes_info["area"])
            probes_data_json = self.mesh_area_probes_object()
            self._ripeProbes = probes_data_json
        else:
            # Build probes object from a file
            self._ripeProbes = probes_info

    def get_probes_in_section(self, section: dict) -> dict:
        base_url = "https://atlas.ripe.net/api/v2/probes/"
        filters = "longitude__gte={}&longitude__lte={}&latitude__gte={}&latitude__lte={}".format(
            section["longitude_min"], section["longitude_max"],
            section["latitude_min"], section["latitude_max"])
        fields = "fields=id,geometry"
        url = "{}?{}&{}".format(base_url, filters, fields)
        return requests.get(url=url).json()

    def mesh_area_probes_object(self) -> dict:
        polygon_grid = self.build_intersection_grid_with_countries()
        plot_multipolygon(polygon_grid)
        sections_borders = []
        for polygon in list(polygon_grid.geoms):
            sections_borders.append(get_section_borders_of_polygon(polygon))

        probes_id_list = []
        print("Number of sections to select probes: {}".format(len(sections_borders)))
        for section in sections_borders:
            probes_in_mesh_area = self.get_probes_in_section(section)
            probes_filtered = filter(
                lambda probe: is_probe_inside_section(
                    probe=probe, section=section),
                probes_in_mesh_area["results"])
            probes_filtered = list(probes_filtered)
            try:
                id_selected = random.choice(probes_filtered)["id"]
                probes_id_list.append(id_selected)
            except IndexError:
                # Inside the selected section there is no probe
                continue

        if len(probes_id_list) > 1000:
            print("More than 1000 probes in grid, selecting a set of 1000")
            probes_id_list = random.sample(probes_id_list, 1000)

        return {
            "probes": [
                {
                    "requested": len(probes_id_list),
                    "type": "probes",
                    "value": ",".join(map(str, probes_id_list))
                }
            ]

        }

    def build_intersection_grid_with_countries(self):
        countries_borders_dict = json_file_to_dict(
            COUNTRY_BORDERS_GEOJSON_FILEPATH)
        features = countries_borders_dict["features"]
        # NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates
        countries_geometry_collection = GeometryCollection(
            [shape(feature["geometry"]).buffer(0) for feature in features])
        area_polygons = self.get_polygons_in_mesh_area()
        intersecting_polygons = []
        for polygon in area_polygons:
            if polygon.intersects(countries_geometry_collection):
                intersecting_polygons.append(polygon)

        return MultiPolygon(intersecting_polygons)

    def get_polygons_in_mesh_area(self) -> list:
        spacing = 0.3
        polygons = []
        x_min = self._mesh_area[0]
        x_max = self._mesh_area[2]
        y_max = self._mesh_area[1]
        y = self._mesh_area[3]
        i = -1
        while True:
            if y > y_max:
                break
            x = x_min

            while True:
                if x > x_max:
                    break

                # components for polygon grid
                polygon = box(x, y, x + spacing, y + spacing)
                polygons.append(polygon)

                i = i + 1
                x = x + spacing

            y = y + spacing
        return polygons

    def doMeasure(self, probes_file):
        data = self.load_data_request(probes_file)
        self._request_data = data

        # print ("Running measurement from Ripe Atlas with this data:")
        # print (json.dumps(data, indent=4))
        self._measurement = RIPEAtlas.Measurement(data)
        print("ID measure: %s\tTARGET: %s\tNumber of Vantage Points: %i " % (
            self._measurement.id,  self._ip, self._measurement.num_probes))
        self.get_measurement_probes()

        return self._ripe_probes_geo

    def get_measurement_probes(self):
        measurements_url = "https://atlas.ripe.net/api/v2/measurements"
        probes_url = "https://atlas.ripe.net/api/v2/probes"

        measurement_id = self.get_measurement_id()

        url = measurements_url + "/%s" % measurement_id + "/?fields=probes"
        measurement_response = requests.get(url).json()

        for probe in measurement_response["probes"]:
            hostname = str(probe["id"])
            url = probes_url + "/%s" % hostname

            probe_response = requests.get(url).json()

            latitude = probe_response["geometry"]["coordinates"][1]
            longitude = probe_response["geometry"]["coordinates"][0]
            self._ripe_probes_geo[hostname] = [latitude, longitude]

    def save_measurement_results(self,
                                 ripe_measurement_results: dict,
                                 info_probes: dict,
                                 campaign_name: str) -> str:
        data_to_save = {
            "target": self._ip,
            "measurement_id": self._measurement.id,
            "request_data": self._request_data,
            "probes_filepath": self._probes_filepath,
            "measurement_results": []}

        for probe_result in ripe_measurement_results:
            probe_id = probe_result["prb_id"]
            for probe_measure in probe_result["result"]:
                if "rtt" in probe_measure.keys():
                    measure = dict()
                    try:
                        measure["hostname"] = str(probe_id)
                        measure["latitude"] = info_probes[str(probe_id)][0]
                        measure["longitude"] = info_probes[str(probe_id)][1]
                        measure["rtt_ms"] = probe_measure["rtt"]
                    except KeyError as exception:
                        print("Key Exception Error")
                        print(exception.__str__())
                    data_to_save["measurement_results"].append(measure)

        self._measurement_filename = "{}_{}_{}.json".format(
            self._ip,
            self._probes_filename,
            self.get_measurement_id()
        )

        if campaign_name is not None:
            measurement_filepath = MEASUREMENTS_CAMPAIGNS_PATH + \
                                   campaign_name + \
                                   "/{}".format(self._measurement_filename)
        else:
            measurement_filepath = MEASUREMENTS_PATH + "{}".format(
                self._measurement_filename)

        dict_to_json_file(data_to_save, measurement_filepath)
        return measurement_filepath

    def get_measurement_nums(self, ripe_measurement_results: dict) -> \
            tuple[int, int, int, int, int]:
        num_probes_answer = 0
        num_probes_timeout = 0
        num_probes_fail=0
        num_latency_measurement = 0
        total_rtt = 0

        for result in ripe_measurement_results:
            for measure in result["result"]:
                num_probes_answer += 1
                if "rtt" in measure.keys():
                    try:
                        total_rtt += int(measure["rtt"])
                        num_latency_measurement += 1
                    except KeyError as exception:
                        print (exception.__str__())
                elif "error" in measure.keys():
                    num_probes_fail += 1
                elif "x" in measure.keys():
                    num_probes_timeout += 1
                else:
                    print("Error in the measurement: result has no field rtt, \
                          or x or error")
        return (num_probes_answer, num_probes_timeout, num_probes_fail,
                num_latency_measurement, total_rtt)

    def retrieveResult(self, info_probes, campaign_name: str):
        self.result = self._measurement.results(
            wait=True, percentage_required=self._percentageSuccessful)

        path_file = self.save_measurement_results(
            self.result,
            info_probes,
            campaign_name)

        (num_probes_answer,
         num_probes_timeout,
         num_probes_fail,
         num_latency_measurement,
         total_rtt) = self.get_measurement_nums(self.result)

        print("Number of answers: %s" % len(self.result))
        if num_probes_answer == 0:
            print("Watson, we have a problem, no successful test!")
            sys.exit(0)
        else:
            try:
                print("Resume: %i successful tests (%.1f %%), %i errors "
                      "(%.1f %%), %i timeouts (%.1f %%), average RTT: %i ms" %
                      (num_latency_measurement,
                       num_latency_measurement*100.0/num_probes_answer,
                       num_probes_fail,
                       num_probes_fail*100.0/num_probes_answer,
                       num_probes_timeout,
                       num_probes_timeout*100.0/num_probes_answer,
                       total_rtt/num_latency_measurement))
            except:
                  c = 0
        return num_latency_measurement, path_file

