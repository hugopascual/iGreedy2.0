#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ./igreedy.sh -w 192.5.5.241 -s "(52.01,4.56)"
# ./igreedy.sh -w 192.5.5.241
# ./igreedy.sh -w 104.16.123.96

import pandas as pd
# external modules imports
import requests
import geocoder
import random
import time
import subprocess
# internal modules imports
from utils.constants import (
    RIPE_ATLAS_MEASUREMENTS_BASE_URL,
    RIPE_ATLAS_PROBES_BASE_URL,
    KEY_FILEPATH,
    HUNTER_MEASUREMENTS_PATH
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file,
    check_discs_intersect,
    distance,
    get_distance_from_rtt,
    calculate_hunter_pings_intersection_area
)


class Hunter:
    def __init__(self, target: str, origin: (float, float) = (),
                 output_filename: str = "hunter_measurement.json",
                 check_cf_ray: bool = True,
                 additional_info: dict = None):
        self._target = target
        # origin format = (latitude, longitude)
        if origin != ():
            self._origin = origin
            self._traceroute_from_host = False
        else:
            try:
                (latitude, longitude) = geocoder.ip("me").latlng
            except:
                (latitude, longitude) = (0, 0)
            self._origin = (latitude, longitude)
            self._traceroute_from_host = True

        self._radius = 20
        self._url = RIPE_ATLAS_MEASUREMENTS_BASE_URL + "/?key={}".format(
            self.get_ripe_key()
        )
        self._measurement_id = 0
        self._measurement_result_filepath = output_filename
        self._ping_discs = []
        self._check_cf_ray = check_cf_ray
        self._results_measurements = {
            "origin": {
                "latitude": self._origin[0],
                "longitude": self._origin[1]
            },
            "target": self._target,
            "traceroute_from_host": self._traceroute_from_host,
            "gt_info": {},
            "hunt_results": {
                "cities": [],
                "countries": [],
                "airports_located": [],
                "intersection": {},
                "centroid": {}
            },
            "traceroute": [],
            "last_hop": {},
            "hops_directions_list": [],
            "discs_intersect": False,
            "ping_discs": [],
            "pings": []
        }
        if additional_info:
            self._results_measurements["additional_info"] = additional_info

    def hunt(self):
        if self._target is None or self._target == "":
            return

        if self._check_cf_ray:
            self.obtain_cf_ray()
        self.make_traceroute_measurement()
        self.build_measurement_filepath()

        # Geolocate last valid hop in traceroute measurement
        last_hop = self.geolocate_last_hop()
        print("Last Hop location: ", last_hop)
        self._results_measurements["last_hop"] = last_hop
        if last_hop["geolocation"] == {}:
            self.save_measurements()
            return

        # Pings from near last hop geo
        self.obtain_pings_near_last_hop(last_hop["geolocation"])

        # Intersection of discs from pings
        if self.check_ping_discs_intersection():
            print("All pings generated discs intersect")
            self._results_measurements["discs_intersect"] = True
            intersection_info = calculate_hunter_pings_intersection_area(
                self._results_measurements["ping_discs"]
            )
            self._results_measurements["hunt_results"]["intersection"] = \
                intersection_info["intersection"]
            self._results_measurements["hunt_results"]["centroid"] = \
                intersection_info["centroid"]
            # Location of airports inside intersection
            self.check_airports_inside_intersection()
        else:
            print("Some pings do not intersect. Bad scenario")

        self.save_measurements()

    def make_traceroute_measurement(self):
        print("###########")
        print("Traceroute phase initiated")
        print("###########")
        print("Target to hunt: ", self._target)
        if self._traceroute_from_host:
            self.host_traceroute_measurement()
        else:
            self.ripe_traceroute_measurement()

    def host_traceroute_measurement(self):
        result_traceroute = subprocess.run(["traceroute", self._target],
                                           stdout=subprocess.PIPE)
        hops_list = ((str(result_traceroute.stdout)).split("\\n")[1:])[:-1]
        self._results_measurements["traceroute"] = hops_list

    def ripe_traceroute_measurement(self):
        # Make traceroute from origin
        probe_id = self.find_probes_in_circle(
            latitude=self._origin[0],
            longitude=self._origin[1],
            radius=self._radius,
            num_probes=1
        )
        traceroute_data = {
            "definitions": [
                {
                    "target": self._target,
                    "description": "Hunter traceroute %s" % self._target,
                    "type": "traceroute",
                    "is_oneoff": True,
                    "af": 4,
                    "protocol": "ICMP",
                    "packets": 3
                }
            ],
            "probes": [
                {
                    "requested": 1,
                    "type": "probes",
                    "value": ",".join(map(str, probe_id))
                }
            ]
        }
        self.make_ripe_measurement(data=traceroute_data)
        if self._measurement_id == 0:
            print("Measure could not start")
            return
        else:
            print("Measure ID: ", self._measurement_id)
        # Obtain results
        self._results_measurements["traceroute"] = \
            self.get_measurement_results()

    def make_ripe_measurement(self, data: dict):
        # Start the measurement and get measurement id
        response = {}
        try:
            response = requests.post(self._url, json=data).json()
            self._measurement_id = response["measurements"][0]
        except Exception as e:
            print(e.__str__())
            print(response)

    def get_probes_scheduled(self) -> int:
        probes_scheduled_url = RIPE_ATLAS_MEASUREMENTS_BASE_URL + \
                               "{}/?fields=probes_scheduled".format(
                                   self._measurement_id)
        retrieved = False
        while not retrieved:
            time.sleep(1)
            try:
                response = requests.get(probes_scheduled_url).json()
                return int(response["probes_scheduled"])
            except:
                print("Measure not scheduled yet")

    def build_measurement_filepath(self):
        if self._measurement_result_filepath == "hunter_measurement.json":
            filename = "{}_{}_{}_{}.json".format(
                self._target,
                self._origin[0], self._origin[1],
                self._measurement_id)
            self._measurement_result_filepath = \
                HUNTER_MEASUREMENTS_PATH + filename
        else:
            return

    def get_measurement_results(self) -> list:
        results_measurement_url = \
            RIPE_ATLAS_MEASUREMENTS_BASE_URL + "{}/results".format(
                self._measurement_id
            )
        delay = 5
        enough_results = False
        attempts = 0
        response = []

        while not enough_results:
            print("Wait {} seconds for results. Number of attempts {}".
                  format(delay, attempts))
            time.sleep(delay)
            delay = 15
            attempts += 1
            probes_scheduled = self.get_probes_scheduled()
            print("Total probes scheduled for measurement: ", probes_scheduled)
            response = requests.get(results_measurement_url).json()
            print("Obtained response from {} probes".format(len(response)))
            if len(response) == probes_scheduled:
                print("Results retrieved")
                enough_results = True
            elif attempts >= 10:
                enough_results = True
            else:
                enough_results = False
        return response

    def geolocate_last_hop(self) -> dict:
        directions_list = self.build_hops_directions_list()
        print("Traceroute directions: ")
        [print(direction) for direction in directions_list]
        last_hop = self.select_last_hop_valid(directions_list)
        print("Last Hop IP direction valid: ", last_hop["ip"])
        return last_hop

    def select_last_hop_valid(self, directions_list: list) -> dict:
        validated = False
        last_hop_index = -2
        last_hop_direction = ""
        last_hop_geo = {}
        while not validated:
            if (len(directions_list) + last_hop_index) < 0:
                print("No last_hop valid direction")
                last_hop_direction = ""
                break

            last_hop_directions = directions_list[last_hop_index]
            # Check if there is results
            if not self.hop_from_directions_are_equal(last_hop_directions):
                last_hop_index += -1
                continue

            last_hop_direction = last_hop_directions[0]
            if "*" == last_hop_direction:
                last_hop_index += -1
                continue
            elif last_hop_direction == self._target:
                last_hop_index += -1
                continue

            try:
                # TODO geolocate last_hop_direction better
                last_hop_geo = self.geolocate_ip_commercial_database(
                    ip=last_hop_direction)
            except Exception as e:
                print("Exception")
                print(e)
                last_hop_index += -1
                continue

            validated = True

        last_hop = {
            "ip": last_hop_direction,
            "index": (len(directions_list) + last_hop_index),
            "geolocation": last_hop_geo
        }
        return last_hop

    def build_hops_directions_list(self) -> list:
        directions_list = []
        if self._traceroute_from_host:
            for result in self._results_measurements["traceroute"]:
                hop_directions = []
                for split in result.split(" "):
                    if split == "":
                        continue
                    elif split == "*":
                        hop_directions.append(split)
                    elif split[0] == "(" and split[-1] == ")":
                        hop_directions.append(split[1:-1])
                    else:
                        continue
                hop_directions = list(dict.fromkeys(hop_directions))
                directions_list.append(hop_directions)
        else:
            traceroute_results = \
                self._results_measurements["traceroute"][0]["result"]
            for hop in traceroute_results:
                hop_directions = []
                for hop_result in hop["result"]:
                    if "x" in hop_result.keys():
                        hop_directions.append("*")
                    else:
                        hop_directions.append(hop_result["from"])
                hop_directions = list(dict.fromkeys(hop_directions))
                directions_list.append(hop_directions)

        self._results_measurements["hops_directions_list"] = directions_list
        return directions_list

    def obtain_pings_near_last_hop(self, last_hop_geo: dict):
        print("###########")
        print("Pings phase initiated")
        print("###########")
        # Make pings from probes around last_hop_geo
        probes_id_list = self.find_probes_in_circle(
            latitude=last_hop_geo["latitude"],
            longitude=last_hop_geo["longitude"],
            radius=self._radius,
            num_probes=7
        )
        pings_data = {
            "definitions": [
                {
                    "target": self._target,
                    "description": "Hunter pings %s" % self._target,
                    "type": "ping",
                    "is_oneoff": True,
                    "af": 4,
                    "packets": 3
                }
            ],
            "probes": [
                {
                    "requested": len(probes_id_list),
                    "type": "probes",
                    "value": ",".join(map(str, probes_id_list))
                }
            ]
        }
        self.make_ripe_measurement(data=pings_data)
        if self._measurement_id == 0:
            print("Measure could not start")
            return
        else:
            print("Measure ID: ", self._measurement_id)
        # Obtain results
        self._results_measurements["pings"] = \
            self.get_measurement_results()

    def check_ping_discs_intersection(self) -> bool:
        # Build discs
        for ping_result in self._results_measurements["pings"]:
            min_rtt = ping_result["min"]
            ping_radius = get_distance_from_rtt(min_rtt)
            probe_location = self.get_probe_coordinates(ping_result["prb_id"])
            self._ping_discs.append({
                "probe_id": ping_result["prb_id"],
                "latitude": probe_location["latitude"],
                "longitude": probe_location["longitude"],
                "rtt_min": ping_result["min"],
                "radius": ping_radius
            })

        self._results_measurements["ping_discs"] = self._ping_discs

        if all(ping["radius"] == -1 for ping in self._ping_discs):
            return False

        # Check all disc intersection
        for disc1 in self._ping_discs:
            for disc2 in self._ping_discs:
                if disc1 == disc2:
                    continue
                elif disc1["radius"] == -1 or disc2["radius"] == -1:
                    continue
                elif check_discs_intersect(disc1, disc2):
                    continue
                else:
                    return False
        return True

    def check_airports_inside_intersection(self):
        airports_df = pd.read_csv("datasets/airports.csv", sep="\t")
        airports_df.drop(["pop",
                          "heuristic",
                          "1", "2", "3"], axis=1, inplace=True)

        def check_inside_intersection(airport_code) -> bool:
            airport_to_check = airports_df[
                (airports_df["#IATA"] == airport_code)
            ]
            lat_long_string = airport_to_check["lat long"].values[0]
            (airport_lat, airport_lon) = lat_long_string.split(" ")
            a = {"latitude": float(airport_lat),
                 "longitude": float(airport_lon)}
            for disc in self._ping_discs:
                b = {"latitude": disc["latitude"],
                     "longitude": disc["longitude"]}
                if distance(a=a, b=b) < disc["radius"]:
                    continue
                else:
                    return False
            return True

        airports_df["inside_intersection"] = airports_df["#IATA"].apply(
            lambda airport_code: check_inside_intersection(airport_code)
        )

        airports_inside_df = airports_df[(
                airports_df["inside_intersection"] == True
        )].copy()

        cities_results = list(airports_inside_df["city"].unique())
        countries_results = list(airports_inside_df["country_code"].unique())
        airports_inside_df.drop(["inside_intersection"], axis=1, inplace=True)
        airports_inside_df.rename(columns={"#IATA": "IATA_code"}, inplace=True)
        airports_located = airports_inside_df.to_dict("records")
        for airport_located in airports_located:
            (lat, lon) = airport_located["lat long"].split(" ")
            airport_located["latitude"] = float(lat)
            airport_located["longitude"] = float(lon)
            airport_located.pop("lat long", None)

        print("Cities locations detected: ")
        [print(city) for city in cities_results]
        print("Countries detected: ")
        [print(country) for country in countries_results]

        self._results_measurements["hunt_results"]["cities"] = \
            cities_results
        self._results_measurements["hunt_results"]["countries"] = \
            countries_results
        self._results_measurements["hunt_results"]["airports_located"] = \
            airports_located

    def save_measurements(self):
        dict_to_json_file(self._results_measurements,
                          self._measurement_result_filepath)

# Not class exclusive functions

    def find_probes_in_circle(self,
                              latitude: float, longitude: float,
                              radius: float, num_probes: int) -> list:
        radius_filter = "radius={},{}:{}".format(latitude, longitude, radius)
        connected_filter = "status_name=Connected"
        fields = "fields=id,geometry,address_v4"
        url = "{}?{}&{}&{}".format(RIPE_ATLAS_PROBES_BASE_URL,
                                   radius_filter,
                                   connected_filter,
                                   fields)
        probes_inside = requests.get(url=url).json()
        not_target_ip_probes = list(filter(
            lambda probe: probe["address_v4"] != self._target,
            probes_inside["results"]
        ))
        if len(not_target_ip_probes) == 0:
            print("No probes in a {} km circle.".format(radius))
            return self.find_probes_in_circle(
                latitude=latitude,
                longitude=longitude,
                radius=radius + 10,
                num_probes=num_probes
            )
        elif len(not_target_ip_probes) < num_probes:
            print("Less than {} probes suitable in area".format(num_probes))
            return self.find_probes_in_circle(
                latitude=latitude,
                longitude=longitude,
                radius=radius + 10,
                num_probes=num_probes
            )
        else:
            probes_selected = random.sample(not_target_ip_probes, num_probes)
            ids_selected = [probe["id"] for probe in probes_selected]
            return ids_selected

    def get_ripe_key(self) -> str:
        return json_file_to_dict(KEY_FILEPATH)["key"]

    def is_IP_anycast(self, ip: str) -> bool:
        # TODO validate if ip is anycast or not
        return False

    def hop_from_directions_are_equal(self, hop_directions_list: list) -> bool:
        if len(hop_directions_list) != 1:
            return False
        else:
            return True

    def geolocate_ip_commercial_database(self, ip: str) -> dict:
        (latitude, longitude) = geocoder.ip(ip).latlng
        return {
            "latitude": latitude,
            "longitude": longitude
        }

    def get_probe_coordinates(self, probe_id: int) -> dict:
        url = RIPE_ATLAS_PROBES_BASE_URL + "/%s" % probe_id
        probe_response = requests.get(url).json()

        latitude = probe_response["geometry"]["coordinates"][1]
        longitude = probe_response["geometry"]["coordinates"][0]
        return {
            "latitude": latitude,
            "longitude": longitude
        }

    # def make_box_centered_on_origin(self) -> Polygon:
    #     return box(xmin=self._origin[0] - self._separation,
    #                ymin=self._origin[1] - self._separation,
    #                xmax=self._origin[0] + self._separation,
    #                ymax=self._origin[1] + self._separation)

    def obtain_cf_ray(self):
        try:
            headers = requests.get("http://{}".format(self._target)).headers
            cf_ray_iata_code = headers["cf-ray"].split("-")[1]

            airports_df = pd.read_csv("datasets/airports.csv", sep="\t")
            airports_df.drop(["pop",
                              "heuristic",
                              "1", "2", "3"], axis=1, inplace=True)
            mask = airports_df["#IATA"].values == cf_ray_iata_code
            airport_cf_ray = airports_df[mask].to_dict("records")[0]

            self._results_measurements["gt_info"] = airport_cf_ray

        except Exception as e:
            print("NO CF-RAY IN HEADERS")


