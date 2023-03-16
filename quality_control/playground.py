#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import constants
from auxiliar import (
    get_alpha2_country_codes
)

print(get_alpha2_country_codes(
    constants.ADECUATE_INTERNACIONAL_TRANSFERS_COUNTRIES_FILE_PATH))