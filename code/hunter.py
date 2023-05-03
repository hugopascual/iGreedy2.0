#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
import geocoder
import random
import time
# internal modules imports
from utils.constants import (
    RIPE_ATLAS_MEASUREMENTS_BASE_URL,
    RIPE_ATLAS_PROBES_BASE_URL,
    KEY_FILEPATH,
    HUNTER_MEASUREMENTS_PATH
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file
)


class Hunter:
    def __init__(self, target: str, origin: (float, float) = ()):
        self._target = target
        if origin != ():
            self._origin = origin
        else:
            latlng = geocoder.ip("me").latlng
            self._origin = (latlng[1], latlng[0])
        self._radius = 30
        self._url = RIPE_ATLAS_MEASUREMENTS_BASE_URL + "/?key={}".format(
            self.get_ripe_key()
        )
        self._measurement_id = 0
        self._probes_scheduled = 0
        self._measurement_result_filepath = "hunter_measurement.json"

    def hunt(self):
        # Make traceroute from origin
        # self.make_traceroute_measurement()
        self._measurement_id = 53115611
        print("Measure ID: ", self._measurement_id)
        self.get_probes_scheduled()
        self.build_measurement_filepath()
        self.get_measurement_results()
        # Geolocate last valid hop in traceroute
        self.geolocate_last_hop()

    def make_traceroute_measurement(self):
        probe_id = self.find_probes_in_circle(
            latitude=self._origin[1],
            longitude=self._origin[0],
            radius=self._radius,
            num_probes=1
        )
        data = {
            "definitions": [
                {
                    "target": self._target,
                    "description": "Hunter %s" % self._target,
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
                    "value": probe_id
                }
            ]
        }

        # Start the measurement and get measurement id
        response = requests.post(self._url, json=data).json()
        self._measurement_id = response["measurements"][0]

    def get_probes_scheduled(self):
        probes_scheduled_url = RIPE_ATLAS_MEASUREMENTS_BASE_URL + \
                               "{}/?fields=probes_scheduled".format(
                                   self._measurement_id)
        retrieved = False
        while not retrieved:
            time.sleep(1)
            try:
                response = requests.get(probes_scheduled_url).json()
                self._probes_scheduled = int(response["probes_scheduled"])
            except:
                print("Measure not scheduled yet")
            if self._probes_scheduled != 0:
                retrieved = True

    def build_measurement_filepath(self):
        filename = "{}_{}_{}_{}.json".format(
            self._target,
            self._origin[1], self._origin[0],
            self._measurement_id)
        self._measurement_result_filepath = HUNTER_MEASUREMENTS_PATH + filename

    def get_measurement_results(self):
        results_measurement_url = \
            RIPE_ATLAS_MEASUREMENTS_BASE_URL + "{}/results".format(
                self._measurement_id
            )
        delay = 5
        enough_results = False
        attempts = 0
        response = {}
        while not enough_results:
            print("Wait {} seconds for results. Number of attempts {}".
                  format(delay, attempts))
            time.sleep(delay)
            delay = 15
            attempts += 1

            response = requests.get(results_measurement_url).json()
            if len(response) == self._probes_scheduled:
                print("Results retrieved")
                enough_results = True

        dict_to_json_file(response, self._measurement_result_filepath)

    def geolocate_last_hop(self) -> dict:
        last_hop = self.select_last_hop_valid()
        last_hop_direction = last_hop["result"][0]["from"]
        min_rtt = min(result["rtt"] for result in last_hop["result"])
        # TODO
        return {"latitude": 40, "longitude": -3}

    def select_last_hop_valid(self) -> dict:
        measurement_data = json_file_to_dict(
            self._measurement_result_filepath)[0]
        validated = False
        last_hop_index = -2
        last_hop = {}
        while not validated:
            last_hop = measurement_data["result"][last_hop_index]
            # Check if there is results
            if "x" in last_hop["result"].keys():
                last_hop_index += -1
                continue
            if self.is_IP_anycast(last_hop["result"][0]["from"]):
                last_hop_index += -1
                continue
            if not self.hop_from_directions_are_equal(last_hop):
                last_hop_index += -1
                continue
            validated = True
        return last_hop

    def get_ripe_key(self) -> str:
        return json_file_to_dict(KEY_FILEPATH)["key"]

    def find_probes_in_circle(self,
                              latitude: float, longitude: float,
                              radius: float, num_probes: int) -> list:
        filters = "radius={},{}:{}".format(latitude, longitude, radius)
        fields = "fields=id,geometry,status"
        url = "{}?{}&{}".format(RIPE_ATLAS_PROBES_BASE_URL, filters, fields)
        probes_inside = requests.get(url=url).json()
        probes_connected = list(filter(
            lambda probe: probe["status"]["name"] == "Connected",
            probes_inside["results"]))
        if len(probes_connected) == 0:
            "No probes in area"
        elif len(probes_connected) < num_probes:
            num_probes = len(probes_connected)
        probes_selected = random.sample(probes_connected, num_probes)
        ids_selected = [probe["id"] for probe in probes_selected]
        return ids_selected

    def is_IP_anycast(self, ip: str) -> bool:
        return False

    def hop_from_directions_are_equal(self, hop: dict) -> bool:
        initial_direction = hop["result"][0]["from"]
        for result in hop["result"]:
            if initial_direction != result["from"]:
                return False
        return True

    # def make_box_centered_on_origin(self) -> Polygon:
    #     return box(xmin=self._origin[0] - self._separation,
    #                ymin=self._origin[1] - self._separation,
    #                xmax=self._origin[0] + self._separation,
    #                ymax=self._origin[1] + self._separation)
