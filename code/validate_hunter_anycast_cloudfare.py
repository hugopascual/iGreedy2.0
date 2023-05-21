#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# python3 code/validate_hunter_anycast_cloudfare.py | tee -a "validation_anycast_cloudfare_logs.txt"
# external modules imports
import pandas as pd
import requests
import random
# internal modules imports
from hunter import Hunter
from utils.constants import (
    RIPE_ATLAS_PROBES_BASE_URL
)


class AnycastValidationCloudfare:

    def __init__(self):
        self._targets_list = ["192.5.5.241", "104.16.123.96"]
        self._vpn_servers_names = ["Host"]

    def validate_anycast_from_vpn(self):
        for vpn_server in self._vpn_servers_names:
            for target in self._targets_list:
                output_filename = \
                    "datasets/hunter_measurements/campaigns/" \
                    "validation_anycast_cloudfare_{}/{}_{}.json".format(
                        "202230521",
                        target,
                        vpn_server)
                hunter = Hunter(
                    target=target,
                    check_cf_ray=True,
                    output_filename=output_filename
                )
                hunter.hunt()

    def connect_to_vpn_server(self, vpn_server: str):
        if vpn_server == "Host":
            return
        else:
            return


validator = AnycastValidationCloudfare()
validator.validate_anycast_from_vpn()
