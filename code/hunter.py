#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import requests
# internal modules imports
from utils.constants import (
    RIPE_ATLAS_MEASUREMENTS_BASE_URL,
    RIPE_ATLAS_PROBES_BASE_URL
)
from utils.common_functions import (
    json_file_to_dict
)


class Hunter:
    def __init__(self, target: str, origin: tuple):
        self._target = target
        self._origin = origin

    def find_probe_id_near_origin(self):
        self._origin = (0, 0)

    def make_traceroute_measurement(self):
        return