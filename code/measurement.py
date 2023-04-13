#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# helper functions to launch RIPE Atlas measurement  (./igreedy -m)
#---------------------------------------------------------------------.

# external modules imports
import json
import time
import os
import string
import sys
import time
import getopt
import socket
import collections
import webbrowser
import requests
# internal modules imports
from utils.constants import (
    MEASUREMENTS_PATH,
    MEASUREMENTS_CAMPAIGNS_PATH
)
from utils.common_functions import (
    dict_to_json_file
)
import RIPEAtlas

class Measurement(object):
    def __init__(self, ip, ripeProbes=None):

        if(self.checkIP(ip)):
            self._ip = ip
        else:
            print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
            sys.exit(1)
        self._ripeProbes = ripeProbes
        self._numberOfPacket = 2 #to improve
        self._numberOfProbes = 5 #to improve, introduce as parameter, in alternative to the list of probes
        self._measurement = None
        self.result = None
        self._ripe_probes_geo = {}

        self._percentageSuccessful = 0.8 

        self._probes_filepath = None
        self._probes_filename = None
        self._measurement_filename = None
        
    def getIP(self):
        return self._ip

    def getRipeProbes(self):
        return self._ripeProbes
    
    def get_measurement_id(self):
        return self._measurement.id

    def checkIP(self,str):
        try:
            addr = socket.inet_pton(socket.AF_INET6, str)
        except socket.error: # not a valid IPv6 address
            try:
                addr = socket.inet_pton(socket.AF_INET, str)
            except socket.error: # not a valid IPv4 address either
                return False
        return True

    def loadProbes(self,pathVPs=None):
        temp_list_probes=[]
        temp_information_probes={}
        if pathVPs is None:
            pathVPs = "./datasets/ripe-vps"

        tempInformationProbes={}
        tempListProbes=[]
        for line in open(pathVPs,'r').readlines():
            if line.startswith("#"): #skip header and comments
                continue 
            hostname,latitude,longitude = line.strip().split("\t")
            temp_list_probes.append(hostname)
            temp_information_probes[hostname]=[latitude,longitude]
        self._numberOfProbes=len(temp_list_probes)
        
        print("Information retrived of probes")
        print(temp_information_probes)
        
        return (",".join(temp_list_probes),temp_information_probes) #building the list

    def load_data_request(self, probes_file):
        data = {
            "definitions": [
                {
                    "target": self._ip, 
                    "description": "Ping %s" % self._ip, 
                    "type": "ping", 
                    "is_oneoff": True, 
                    "packets": self._numberOfPacket,
                    "af": 4
                }
            ]
        }

        if ":" in self._ip:
            af = 6
        else:
            af = 4
        data["definitions"][0]['af'] = af

        self._probes_filepath = probes_file
        self._probes_filename = probes_file.split("/")[-1][:-5]

        with open(probes_file) as file:
            probes_data_json = file.read()

        self._ripeProbes = json.loads(probes_data_json)
        data["probes"] = self._ripeProbes["probes"]
        return data

    def doMeasure(self, probes_file):
        data = self.load_data_request(probes_file)
        self._request_data = data

        # print ("Running measurement from Ripe Atlas with this data:")
        # print (json.dumps(data, indent=4))
        self._measurement = RIPEAtlas.Measurement(data)
        print ("ID measure: %s\tTARGET: %s\tNumber of Vantage Points: %i " % (
            self._measurement.id,  self._ip, self._measurement.num_probes))
        self.get_measurement_probes()

        return self._ripe_probes_geo

    def get_measurement_probes(self):
        measurements_url = "https://atlas.ripe.net/api/v2/measurements"
        probes_url = "https://atlas.ripe.net/api/v2/probes"

        measurement_id = self.get_measurement_id()

        url = measurements_url + "/%s" % measurement_id + "/?fields=probes"
        measurement_response = requests.get(url).json()

        for probe in measurement_response["probes"]:
            hostname = str(probe["id"])
            url = probes_url + "/%s" % hostname

            probe_response = requests.get(url).json()
            
            latitude = probe_response["geometry"]["coordinates"][1]
            longitude = probe_response["geometry"]["coordinates"][0]
            self._ripe_probes_geo[hostname]=[latitude, longitude]

    def save_measurement_results(self,
                                 ripe_measurement_results: dict,
                                 info_probes: dict,
                                 campaign_name: str) -> str:
        data_to_save = {
            "target": self._ip,
            "measurement_id": self._measurement.id,
            "request_data": self._request_data,
            "probes_filepath": self._probes_filepath,
            "measurement_results": []}

        for probe_result in ripe_measurement_results:
            probe_id = probe_result["prb_id"]
            for probe_measure in probe_result["result"]:
                if "rtt" in probe_measure.keys():
                    measure = dict()
                    try:
                        measure["hostname"] = str(probe_id)
                        measure["latitude"] = info_probes[str(probe_id)][0]
                        measure["longitude"] = info_probes[str(probe_id)][1]
                        measure["rtt_ms"] = probe_measure["rtt"]
                    except KeyError as exception:
                        print("Key Exception Error")
                        print(exception.__str__())
                    data_to_save["measurement_results"].append(measure)

        self._measurement_filename = "{}_{}_{}.json".format(
            self._ip,
            self._probes_filename,
            self.get_measurement_id()
        )

        if campaign_name is not None:
            measurement_filepath = MEASUREMENTS_CAMPAIGNS_PATH + \
                                   campaign_name + \
                                   "/{}".format(self._measurement_filename)
        else:
            measurement_filepath = MEASUREMENTS_PATH + "{}".format(
                self._measurement_filename)

        dict_to_json_file(data_to_save, measurement_filepath)
        return measurement_filepath
        
    def get_measurement_nums(self,ripe_measurement_results: dict) -> tuple[int, int, int, int, int]:
        num_probes_answer = 0
        num_probes_timeout = 0
        num_probes_fail=0
        num_latency_measurement = 0
        total_rtt = 0

        for result in ripe_measurement_results:
            for measure in result["result"]:
                num_probes_answer += 1
                if "rtt" in measure.keys():
                    try: 
                        total_rtt += int(measure["rtt"])
                        num_latency_measurement += 1
                    except KeyError as exception:
                        print (exception.__str__())
                elif "error" in measure.keys():
                    num_probes_fail += 1
                elif "x" in measure.keys():
                    num_probes_timeout += 1
                else:
                    print("Error in the measurement: result has no field rtt, \
                          or x or error")
        return (num_probes_answer, num_probes_timeout, num_probes_fail, 
                num_latency_measurement, total_rtt)

    def retrieveResult(self, info_probes, campaign_name: str):
        self.result = self._measurement.results(
            wait=True, percentage_required=self._percentageSuccessful)

        path_file = self.save_measurement_results(
            self.result,
            info_probes,
            campaign_name)

        (num_probes_answer,
         num_probes_timeout,
         num_probes_fail,
         num_latency_measurement,
         total_rtt) = self.get_measurement_nums(self.result)
        
        print("Number of answers: %s" % len(self.result))
        if num_probes_answer == 0:
            print("Watson, we have a problem, no successful test!")
            sys.exit(0)
        else:
            try:
                print("Resume: %i successful tests (%.1f %%), %i errors "
                      "(%.1f %%), %i timeouts (%.1f %%), average RTT: %i ms" %
                      (num_latency_measurement,
                       num_latency_measurement*100.0/num_probes_answer,
                       num_probes_fail,
                       num_probes_fail*100.0/num_probes_answer,
                       num_probes_timeout,
                       num_probes_timeout*100.0/num_probes_answer,
                       total_rtt/num_latency_measurement))
            except:
                  c = 0
        return num_latency_measurement, path_file

