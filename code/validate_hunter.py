#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# external modules imports
# internal modules imports

class UnicastValidation:

    def __init__(self, target: str):
        self._target = target
        self._unicast_list = []

    def build_unicast_directions_list(self):
        self._unicast_list = []
