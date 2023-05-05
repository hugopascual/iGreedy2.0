#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import shapely
import ast
import random
import requests
import geocoder
from shapely.geometry import MultiPolygon, Polygon, box, MultiPoint, Point, shape
from shapely import wkt
from shapely import from_geojson, GeometryCollection
from utils.constants import (
    RIPE_ATLAS_PROBES_BASE_URL
)
from utils.common_functions import (
    json_file_to_list,
    dict_to_json_file,
    json_file_to_dict,
    is_probe_inside_section,
    get_polygon_from_section
)
from visualize import (
    plot_polygon,
    plot_multipolygon
)

lista = ["hola", "adios", "que tal", "mal", "bien"]
index = -2
print(lista[index])
