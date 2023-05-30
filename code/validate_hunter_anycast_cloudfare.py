#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import subprocess
# internal modules imports
from hunter import Hunter


class AnycastValidationCloudfare:

    def __init__(self):
        # A total of 74 files (37*2)
        self._targets_list = ["192.5.5.241", "104.16.123.96"]
        self._vpn_servers_names = [
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "GE",
            "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LT", "LU", "MT", "MD",
            "NL", "NO", "PL", "PT", "RO", "RU", "RS", "SK", "SI", "ES", "SE",
            "CH", "TR", "UA", "UK"
        ]

    def validate_anycast_from_vpn(self):
        today = "20230530"
        for vpn_server in self._vpn_servers_names:
            additional_info = self.connect_to_vpn_server(vpn_server)
            for target in self._targets_list:
                output_filename = \
                    "datasets/hunter_measurements/campaigns/" \
                    "validation_anycast_udp_cloudfare_{}_3_no_check_multi_ip_last_hop/{}_{}.json".format(
                        today,
                        target,
                        vpn_server)
                hunter = Hunter(
                    target=target,
                    check_cf_ray=True,
                    output_filename=output_filename,
                    additional_info=additional_info
                )
                hunter.hunt()

    def connect_to_vpn_server(self, vpn_server: str) -> dict:
        if vpn_server == "Host":
            return None
        else:
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


validator = AnycastValidationCloudfare()
validator.validate_anycast_from_vpn()
