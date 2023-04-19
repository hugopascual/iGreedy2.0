#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
import geocoder
import random
from shapely import (
    Polygon,
    box
)
# internal modules imports
from utils.constants import (
    RIPE_ATLAS_MEASUREMENTS_BASE_URL,
    RIPE_ATLAS_PROBES_BASE_URL
)
from utils.common_functions import (
    json_file_to_dict,
    get_section_borders_of_polygon
)
from visualize import (
    plot_polygon
)


class Hunter:
    def __init__(self, target: str, origin: (float, float) = ()):
        self._target = target
        if origin != ():
            self._origin = origin
        else:
            latlng = geocoder.ip("me").latlng
            self._origin = (latlng[1], latlng[0])
        self._separation = 1

    def hunt(self):
        return

    def find_probe_id_near_origin(self) -> str:
        section = get_section_borders_of_polygon(
            self.make_box_centered_on_origin()
        )
        filters = "longitude__gte={}&longitude__lte={}&latitude__gte={}&latitude__lte={}".format(
            section["longitude_min"], section["longitude_max"],
            section["latitude_min"], section["latitude_max"])
        fields = "fields=id,geometry"
        url = "{}?{}&{}".format(RIPE_ATLAS_PROBES_BASE_URL, filters, fields)
        probes_inside = requests.get(url=url).json()
        id_selected = random.choice(probes_inside["results"])["id"]
        return id_selected

    def make_traceroute_measurement(self):
        data = {
            "definitions": [
                {
                    "target": self._target,
                    "description": "Ping %s" % self._ip,
                    "type": "ping",
                    "is_oneoff": True,
                    "packets": self._numberOfPacket,
                    "af": 4
                }
            ]
        }

    def make_box_centered_on_origin(self) -> Polygon:
        return box(xmin=self._origin[0] - self._separation,
                   ymin=self._origin[1] - self._separation,
                   xmax=self._origin[0] + self._separation,
                   ymax=self._origin[1] + self._separation)
