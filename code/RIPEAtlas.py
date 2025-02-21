#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#---------------------------------------------------------------
# for convenience included in this igreedy package, available at GitHub: 
# https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib
#---------------------------------------------------------------

""" A module to perform measurements on the RIPE Atlas
<http://atlas.ripe.net/> probes using the UDM (User Defined
Measurements) creation API.

Authorization key is expected in $HOME/.atlas/auth or have to be
provided in the constructor's arguments.

Stéphane Bortzmeyer <bortzmeyer+ripe@nic.fr>
"""

import os, sys
import json
import time
import requests

from utils.custom_exceptions import (
    AuthFileNotFound,
    FieldsQueryError,
    InternalError,
    MeasurementAccessError,
    MeasurementNotFound,
    RequestSubmissionError,
    ResultError
)
import utils.common_functions as cm

authfile = "datasets/auth"
base_url = "https://atlas.ripe.net/api/v2/measurements"

# The following parameters are currently not settable. Anyway, be
# careful when changing these, you may get inconsistent results if you
# do not wait long enough. Other warning: the time to wait depend on
# the number of the probes.
# All in seconds:
fields_delay_base = 6
fields_delay_factor = 0.2
results_delay_base = 3
results_delay_factor = 0.15
maximum_time_for_results_base = 30
maximum_time_for_results_factor = 5
# The basic problem is that there is no easy way in Atlas to know when
# it is over, either for retrieving the list of the probes, or for
# retrieving the results themselves. The only solution is to wait
# "long enough". The time to wait is not documented so the values
# above have been found mostly with trial-and-error.

class Measurement():
    """ An Atlas measurement, identified by its ID (such as #1010569) in the field "id" """

    def __init__(self, data, wait=True, sleep_notification=None, key=None, id=None):
        """
        Creates a measurement."data" must be a dictionary (*not* a JSON string) having the members
        requested by the Atlas documentation. "wait" should be set to False for periodic (not
        oneoff) measurements. "sleep_notification" is a lambda taking one parameter, the
        sleep delay: when the module has to sleep, it calls this lambda, allowing you to be informed of
        the delay. "key" is the API key. If None, it will be read in the configuration file.

        If "data" is None and id is not, a dummy measurement will be created, mapped to
         the existing measurement having this ID.
        """

        if data is None and id is None:
            raise RequestSubmissionError("No data and no measurement ID")
        
        # TODO: when creating a dummy measurement, a key may not be necessary if the measurement is public
        if not key:
            if not os.path.exists(authfile):
                raise AuthFileNotFound("Authentication file %s not found" % authfile)
            auth = open(authfile)
            key = auth.readline()[:-1]
            auth.close()

        self.url = base_url + "/?key=%s" % key
        self.url_probes = base_url + "/%s/?fields=probes,status"
        self.url_status = base_url + "/%s/?fields=status" 
        self.url_results = base_url + "/%s/results/" 
        self.url_latest = base_url + "/%s/latest/?versions=%s"

        if data is not None:
            try:
                self.notification = sleep_notification
                # Start the measurement and get measurement id
                results = requests.post(self.url, json=data).json()
                # TODO remove only for test
                #print(json.dumps(results, indent=4))
                #data["petition_result"] = results
                #print(key)
                #cm.dict_to_json_file(dict=data,
                #                     file_path="last_measurement_data.json")
                self.id = results["measurements"][0]

            except requests.HTTPError as e:
                raise RequestSubmissionError("Status %s, reason \"%s\"" % \
                                             (e.code, e.read()))

            if not wait:
                return
            # Find out how many probes were actually allocated to this measurement
            enough = False
            requested = 0
            for probes_types in data["probes"]:
                requested =+ probes_types["requested"]
            fields_delay = fields_delay_base + (requested * fields_delay_factor)
            while not enough:
                # Let's be patient
                if self.notification is not None:
                    self.notification(fields_delay)
                time.sleep(fields_delay)
                fields_delay *= 2
                try:
                    meta = requests.get(self.url_probes % self.id).json()
                    if meta["status"]["name"] == "Specified" or \
                           meta["status"]["name"] == "Scheduled" or \
                            meta["status"]["name"] == "synchronizing":
                        # Not done, loop
                        pass
                    elif meta["status"]["name"] == "Ongoing":
                        enough = True
                        self.num_probes = len(meta["probes"])
                    else:
                        raise InternalError("Internal error in #%s, unexpected status when querying the measurement fields: \"%s\"" % (self.id, meta["status"]))
                except requests.HTTPError as e:
                    raise FieldsQueryError("%s" % e.read())
        else:
            self.id = id
            try:
                result_status = requests.get(self.url_status % self.id).json()
            except requests.HTTPError as e:
                if e.code == 404:
                    raise MeasurementNotFound
                else:
                    raise MeasurementAccessError("%s" % e.read())
            status = result_status["status"]["name"]
            # TODO: test status
            self.num_probes = None # TODO: get it from the status?
            
    def results(self, wait=True, percentage_required=0.9, latest=None):
        """Retrieves the result. "wait" indicates if you are willing to wait until
        the measurement is over (otherwise, you'll get partial
        results). "percentage_required" is meaningful only when you wait
        and it indicates the percentage of the allocated probes that
        have to report before the function returns (warning: the
        measurement may stop even if not enough probes reported so you
        always have to check the actual number of reporting probes in
        the result). "latest" indicates that you want to retrieve only
        the last N results (by default, you get all the results).
        """
        if latest is not None:
            wait = False
        if latest is None:
            url_lastest = self.url_results % self.id
        else:
            url_lastest = self.url_latest% (self.id, latest)
        if wait:
            enough = False
            attempts = 0
            results_delay = 15
            maximum_time_for_results = 360
            start = time.time()
            elapsed = 0
            result_data = None
            while not enough and elapsed < maximum_time_for_results:
                if self.notification is not None:
                    self.notification(results_delay)
                print("Wait 15 seconds for results. Number of attempts {}".
                      format(attempts))
                time.sleep(results_delay)
                attempts += 1
                elapsed = time.time() - start
                try:
                    result_data = requests.get(url_lastest).json()
                    num_results = len(result_data)
                    if num_results >= self.num_probes*percentage_required:
                        # Requesting a strict equality may be too
                        # strict: if an allocated probe does not
                        # respond, we will have to wait for the stop
                        # of the measurement (many minutes). Anyway,
                        # there is also the problem that a probe may
                        # have sent only a part of its measurements.
                        enough = True
                    else:
                        result_status = requests.get(self.url_status % self.id).json()
                        status = result_status["status"]["name"]
                        if status == "Ongoing":
                            # Wait a bit more
                            pass
                        elif status == "Stopped":
                            # Even if not enough probes
                            enough = True
                        else:
                            raise InternalError("Unexpected status when retrieving the measurement: \"%s\"" % \
                                   result_data["status"])
                except requests.HTTPError as e:
                    if e.code != 404: 
                        # Yes, we may have no result file at all for some time
                        raise ResultError(str(e.code) + " " + e.reason)
            if result_data is None:
                raise ResultError("No results retrieved")
        else:
            try:
                result_data = requests.get(url_lastest).json()
            except requests.HTTPError as e:
                raise ResultError(e.read())
        return result_data

