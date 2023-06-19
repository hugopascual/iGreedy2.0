#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from time import sleep

while True:
    command = subprocess.run(
        [
            "/usr/bin/python3.8",
            "code/make_validation.py"
        ], stdout=subprocess.PIPE
    )

    connection_result = subprocess.run(
        ["protonvpn-cli", "disconnect"],
        stdout=subprocess.PIPE
    )

    for i in range(1, 12):
        print("Started the {} hour of sleep".format(i))
        sleep(3600)
