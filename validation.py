#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from time import sleep
import datetime

# Command to restore protonvpn-cli error
# nmcli connection show --active

while True:
    hour = datetime.datetime.utcnow().hour
    execution_hours = [4, 10, 16, 22]
    if hour in execution_hours:
        print("Execution")
        #command = subprocess.run(
        #    [
        #        "/usr/bin/python3.8",
        #        "code/make_validation.py"
        #    ], stdout=subprocess.PIPE
        #)

        #connection_result = subprocess.run(
        #    ["protonvpn-cli", "disconnect"],
        #    stdout=subprocess.PIPE
        #)
    else:
        print("Waiting for the next programmed hour, now is {}".format(hour))
        print("Programmed hours of execution are {}".format(execution_hours))
        sleep(3600)
