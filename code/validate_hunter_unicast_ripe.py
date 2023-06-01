#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
import pandas as pd
import requests
import random
import json
# internal modules imports
from hunter import Hunter
from utils.constants import (
    RIPE_ATLAS_PROBES_BASE_URL,
    HUNTER_MEASUREMENTS_CAMPAIGNS_PATH
)


class UnicastValidation:

    def __init__(self):
        self._radius = 20
        self._probe_target_ip = ""

    def validate_with_ripe_probes(self):
        airports_filtered = self.get_airports_filtered()
        today = "20230531"
        for index, airport in airports_filtered.iterrows():
            target_location = self.airport_location(airport)
            output_filename = \
                HUNTER_MEASUREMENTS_CAMPAIGNS_PATH + \
                "validation_unicast_udp_ripe_{}_1/{}_{}_{}.json".format(
                    today,
                    airport["#IATA"],
                    airport["city"],
                    airport["country_code"]
                )

            probe_target = self.find_probes_in_circle(
                latitude=target_location["latitude"],
                longitude=target_location["longitude"],
                radius=self._radius,
                num_probes=1
            )[0]
            self._probe_target_ip = probe_target["address_v4"]

            hunter = Hunter(target=self._probe_target_ip,
                            check_cf_ray=False,
                            gt_info= airport.to_dict(),
                            output_filename=output_filename)
            hunter.hunt()

    def get_airports_filtered(self) -> pd.DataFrame:
        airports_df = pd.read_csv("datasets/airports.csv", sep="\t")
        airports_df.drop(["pop",
                          "heuristic",
                          "1", "2", "3"], axis=1, inplace=True)
        large_airports = airports_df[
            (airports_df["size"] == "large_airport")
        ].copy()

        large_airports.drop_duplicates(
            subset=['city'],
            keep='first',
            inplace=True)

        #large_airports = large_airports.sample(n=2)

        return large_airports

    def airport_location(self, airport) -> dict:
        (airport_lat, airport_lon) = airport["lat long"].split(" ")
        return {"latitude": float(airport_lat),
                "longitude": float(airport_lon)}

    def find_probes_in_circle(self,
                              latitude: float, longitude: float,
                              radius: float, num_probes: int) -> list:
        radius_filter = "radius={},{}:{}".format(latitude, longitude, radius)
        is_public_filter = "is_public=True"
        connected_filter = "status_name=Connected"
        fields = "fields=id,geometry,address_v4"
        url = "{}?{}&{}&{}&{}".format(RIPE_ATLAS_PROBES_BASE_URL,
                                      radius_filter,
                                      is_public_filter,
                                      connected_filter,
                                      fields)
        probes_inside = requests.get(url=url).json()
        if probes_inside["count"] == 0:
            print("No probes in a {} km circle.".format(radius))
            return self.find_probes_in_circle(
                latitude=latitude,
                longitude=longitude,
                radius=radius + 10,
                num_probes=num_probes
            )
        elif probes_inside["count"] < num_probes:
            print("Less than {} probes suitable in area".format(num_probes))
            return self.find_probes_in_circle(
                latitude=latitude,
                longitude=longitude,
                radius=radius + 10,
                num_probes=num_probes
            )
        else:
            probes_selected = random.sample(probes_inside["results"],
                                            num_probes)
            probes_target = [{"id": probe["id"],
                             "address_v4": probe["address_v4"]}
                             for probe in probes_selected]
            return probes_target


validator = UnicastValidation()
validator.validate_with_ripe_probes()
