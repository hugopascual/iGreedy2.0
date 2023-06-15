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
    print("Sleeping")
    sleep(39600)
