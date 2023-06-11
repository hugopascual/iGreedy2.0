#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports

# internal modules imports
from validate_hunter_anycast_cloudfare import AnycastValidationCloudfare

# Make two hunter campaigns validating last_hop and not
campaign_name = "validation_anycast_host_udp_cloudfare"
host_validator = AnycastValidationCloudfare(
    check_cf_ray=True,
    validate_last_hop=False,
    campaign_name=campaign_name)
host_validator_no_last_hop = AnycastValidationCloudfare(
    check_cf_ray=True,
    validate_last_hop=False,
    campaign_name=campaign_name)
host_validator.validate_anycast_from_vpn()
host_validator_no_last_hop.validate_anycast_from_vpn()
