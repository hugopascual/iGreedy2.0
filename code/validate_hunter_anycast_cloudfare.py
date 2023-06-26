#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import subprocess
import datetime
# internal modules imports
from hunter import Hunter
from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
)


class AnycastValidationCloudfare:

    def __init__(self,
                 campaign_name: str,
                 check_cf_ray: bool = True,
                 validate_last_hop: bool = True,
                 origin: (float, float) = ()):
        self._today = datetime.datetime.utcnow().strftime('%Y%m%d_%H:%M:%S')
        # A total of 56 files (29*2)
        self._targets_list = ["192.5.5.241", "104.16.123.96"]
        self._vpn_servers_names = [
            "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
            "FR", "GR", "HR", "HU", "IE", "IS", "IT", "LT", "LU", "LV",
            "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK"
        ]

        self._origin = origin
        self._check_cf_ray = check_cf_ray
        self._validate_last_hop = validate_last_hop

        if not self._validate_last_hop:
            self._campaign = "{}_{}".format(campaign_name, self._today)
        else:
            self._campaign = "{}_{}_{}".format(
                campaign_name, "ip_last_hop_validation", self._today)

    def validate_anycast_from_vpn(self):
        for vpn_server in self._vpn_servers_names:
            additional_info = self.connect_to_vpn_server(vpn_server)

            print("Server searched {}, VPN connected {}".format(
                vpn_server, additional_info["server_name"]
            ))

            for target in self._targets_list:
                output_filename = "{}{}/{}_{}.json".format(
                    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
                    self._campaign, target, vpn_server)
                hunter = Hunter(
                    target=target,
                    origin=self._origin,
                    check_cf_ray=self._check_cf_ray,
                    validate_last_hop=self._validate_last_hop,
                    output_filename=output_filename,
                    additional_info=additional_info
                )
                hunter.hunt()

    def connect_to_vpn_server(self, vpn_server: str) -> dict:
        connection_result = subprocess.run([
            "protonvpn-cli", "connect", "--cc",
            vpn_server,
            "--protocol", "tcp"], stdout=subprocess.PIPE)
        connection_status = subprocess.run([
            "protonvpn-cli", "status"], stdout=subprocess.PIPE)
        status_params_raw = (str(connection_status.stdout)
                             .split("\\n")[3:])[:-6]
        status_params = []
        for param_raw in status_params_raw:
            status_params.append((param_raw.split("\\t")[-1])[1:])
        try:
            return {
                "ip": status_params[0],
                "server_name": status_params[1],
                "country": status_params[2],
                "protocol": status_params[3],
            }
        except Exception as e:
            print(e)
            return {
                "params": status_params
            }
