#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import subprocess
# internal modules imports
from hunter import Hunter
from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH
)


class AnycastValidationCloudfare:

    def __init__(self, today: str,
                 campaign_name: str, additional_to_name: str = "",
                 check_cf_ray: bool = True,
                 validate_last_hop: bool = True):
        # A total of 74 files (37*2)
        self._targets_list = ["192.5.5.241", "104.16.123.96"]
        self._vpn_servers_names = [
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "GE",
            "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LT", "LU", "MT", "MD",
            "NL", "NO", "PL", "PT", "RO", "RU", "RS", "SK", "SI", "ES", "SE",
            "CH", "TR", "UA", "UK"
        ]
        self._campaign = "{}_{}_{}".format(
            campaign_name, today, additional_to_name)
        self._today = today

        self.check_cf_ray = check_cf_ray
        self.validate_last_hop = validate_last_hop

    def validate_anycast_from_vpn(self):
        for vpn_server in self._vpn_servers_names:
            additional_info = self.connect_to_vpn_server(vpn_server)
            for target in self._targets_list:
                output_filename = "{}{}/{}_{}.json".format(
                    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH,
                    self._campaign, target, vpn_server)
                hunter = Hunter(
                    target=target,
                    check_cf_ray=self.check_cf_ray,
                    validate_last_hop=self.validate_last_hop,
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


#i = 0
#validator_last_hop = AnycastValidationCloudfare(
#    check_cf_ray=True,
#    validate_last_hop=True,
#    today="20230606",
#    campaign_name="validation_anycast_udp_cloudfare_{}".format(i),
#    additional_to_name="ip_last_hop_validation")
#validator_last_hop.validate_anycast_from_vpn()

i = 1
validator_no_last_hop = AnycastValidationCloudfare(
    check_cf_ray=True,
    validate_last_hop=False,
    today="20230607",
    campaign_name="validation_anycast_udp_cloudfare_{}".format(i))
validator_no_last_hop.validate_anycast_from_vpn()
