#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main user program to process  (./igreedy for help)
# ---------------------------------------------------------------------.

# external modules imports
import getopt
import time
import os.path
import sys
from anycast import Anycast
from measurement import Measurement
from disc import *
import ast
# internal modules imports
from utils.constants import (
    AIRPORTS_INFO_FILEPATH,
    DEFAULT_PROBES_PATH,
    RESULTS_PATH,
    RESULTS_CAMPAIGNS_PATH,
    ASCIIART
)
from utils.common_functions import (
    json_file_to_dict,
    dict_to_json_file
)
from groundtruth import compare_cities_gt
from visualize import (
    plot_file
)

IATA_file = AIRPORTS_INFO_FILEPATH

IATA = []
IATAlat = {}
IATAlon = {}
IATAcity = {}

PAI = []
GT = {}
PAInum = 0
GTnum = 0

input_file = None
ip = None
probes_file = DEFAULT_PROBES_PATH
output_path = RESULTS_PATH
output_file = "output"
results_filename = ""
gt_file = None
campaign_name = None
alpha = 1  # advised settings
visualize = False
noise = 0  # exponential additive noise, only for sensitivity analysis
mesh_area = None

numberOfInstance = 0
truePositive = 0
falsePositive = 0
load_time = 0
run_time = 0
threshold = -1  # negative means infinity


def airportDistance(a, b):
    if (a not in IATAlat) or (b not in IATAlat):
        return "NaN"
    lat1 = IATAlat[a]
    lat2 = IATAlat[b]
    lon1 = IATAlon[a]
    lon2 = IATAlon[b]

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi / 180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians

    # theta = longitude
    theta1 = lon1 * degrees_to_radians
    theta2 = lon2 * degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    if abs(cos - 1.0) < 0.000000000000001:
        arc = 0.0
    else:
        arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc * 6371


def readIATA():
    """
    Routine to read IATA
    """
    # IATA size name lat long countryCode city pop heuristic h1 h2 h3
    global IATA_file, IATA, IATAlat, IATAlon, IATAcity
    temp = []
    data = open(IATA_file)
    data.readline()  # consume header
    for line in data.readlines():
        stuff = line.strip().split("\t")
        iata = stuff[0].upper()
        temp.append(iata)
        latlon = stuff[3]
        (lat, lon) = latlon.split(" ")
        IATAlat[iata] = float(lat)
        IATAlon[iata] = float(lon)
        IATAcity[iata] = stuff[5]
    IATA = set(temp)
    IATAcity["NoCity"] = "NoCity"


def analyze():
    """Routine to iteratively enumerate and geolocate anycast instances"""

    global input_file, gt_file, IATA_file
    global alpha, visualize, noise, threshold
    global numberOfInstance, discsSolution

    anycast = Anycast(input_file, IATA_file, alpha, noise, threshold)

    radiusGeolocated = 0.1
    treshold = 0  # tolerance, airport out of the disc
    iteration = True
    discsSolution = []

    numberOfInstance = 0
    while iteration:

        iteration = False
        resultEnumeration = anycast.enumeration()

        numberOfInstance += resultEnumeration[0]
        if numberOfInstance <= 1:
            print("No anycast instance detected")
            sys.exit()
        for radius, discList in resultEnumeration[1].getOrderedDisc().items():
            for disc in discList:
                # if the disc was not geolocated before, geolocate it!
                if not disc[1]:
                    # used for the csv output
                    # append the disc to the results
                    # discs.append(disc[0])

                    # remove old disc from MIS of disc
                    # MIS = Maximum Independent Set
                    resultEnumeration[1].removeDisc(disc)

                    # result geolocation with the statistics of airports
                    city = anycast.geolocation(disc[0], treshold)

                    # if there is a city inside the disc
                    if city is not False:
                        # geolocated one disc, re-run enumeration!
                        iteration = True
                        # save for the results the city. Used for .csv output
                        # markers.append(newDisc)

                        discsSolution.append((disc[0], city))
                        # insert the new disc in the MIS
                        resultEnumeration[1].add(
                            Disc("Geolocated",
                                 float(city[1]),
                                 float(city[2]),
                                 radiusGeolocated),
                            True)

                        break  # exit for rerun MIS
                    else:
                        # insert the old disc in the MIS
                        resultEnumeration[1].add(disc[0], True)
                        # disc, marker
                        discsSolution.append((disc[0], [
                            "NoCity",
                            disc[0].getLatitude(),
                            disc[0].getLongitude(),
                            "N/A",
                            "N/A"]))

            if iteration:
                break


def output():
    """Routine to output results to a JSON (for GoogleMaps) and a CSV (for 
    further processing)
    """

    global input_file, output_file, gt_file, results_filename
    global base, load_time, run_time

    global ip, probes_file
    global alpha, noise, threshold

    global numberOfInstance
    global GT, PAI, IATAlat, IATAlon, IATAcity, GTnum, PAInum

    # Format of result file if no name is provided
    # $ip_$probes-filename_$alpha_$threshold_$noise.json
    # If noise or threshold are the default values they do not appear
    if output_file == (output_path + "output"):
        measurement_filename = input_file.split("/")[-1][:-5]
        results_filename = output_path + "{}_{}_{}_{}.json".format(
            measurement_filename,
            alpha,
            threshold,
            noise)
    else:
        results_filename = output_file

    print("Number latency measurements: {}".format(len(
        json_file_to_dict(input_file)["measurement_results"])))
    print("Elapsed time (load+igreedy): %.2f (%.2f + %.2f)" % (
        load_time + run_time, load_time, run_time))
    print("Instances: ", str(numberOfInstance))

    # Save results as JSON
    data = dict()

    data["target"] = ip
    data["measurement_filepath"] = input_file
    data["probes_filepath"] = probes_file
    data["alpha"] = alpha
    data["threshold"] = threshold
    data["noise"] = noise
    data["num_anycast_instances"] = numberOfInstance
    data["anycast_instances"] = []
    for instance in discsSolution:
        # circle
        tempCircle = instance[0]
        circle = dict()
        circle["id"] = tempCircle.getHostname()
        circle["latitude"] = tempCircle.getLatitude()
        circle["longitude"] = tempCircle.getLongitude()
        circle["radius"] = tempCircle.getRadius()
        # marker
        tempMarker = instance[1]
        marker = dict()
        marker["id"] = tempMarker[0]
        marker["latitude"] = tempMarker[1]
        marker["longitude"] = tempMarker[2]
        marker["city"] = tempMarker[3]
        marker["country_code"] = tempMarker[4]
        # union of circle and marker
        markCircle = dict()
        markCircle["marker"] = marker
        markCircle["circle"] = circle
        data["anycast_instances"].append(markCircle)

    dict_to_json_file(data, results_filename)


def print_help_text() -> None:
    """Print the options available on iGreedy"""

    print(ASCIIART + """
Usage:  igreedy.py -i measurement_filepath [OPTIONS]
        igreedy.py -m IP_direction [-p probes_filepath] [-c boolean] [OPTIONS]

Commands:
Either long or short options are allowed
    --input         -i  measurement_filepath
                                Input filepath which contains the data of an 
                                specific measurement to be analyzed.
    --measurement   -m  IP_direction
                                Real time measurements from Ripe Atlas using 
                                the ripe probes in datasets/ripeProbes.

Parameters:
    --probes        -p  probes_filepath    
                                Filepath of the JSON document which contains 
                                the specification of the probes to use in the 
                                measurement (default "{}")
    --mesh_probes   -w  python tuple
                                Python tuple with the coordinates of the area 
                                to get the probes of. Use the following format:
                                (top_left_longitude, top_left_latitude, 
                                bottom_right_longitude, bottom_right_latitude)
    --results       -r  boolean
                                Use it when you want that iGreedy automatically 
                                calculate the results based on the measurement 
                                realized. If not present iGreedy do not analyze 
                                the measurement results. (default False)

Options:
    --alpha         -a  alpha   
                                Alpha (tune population vs distance score, 
                                see INFOCOM'15). (default 1)
    --threshold     -t  threshold   
                                Discard disks having latency larger than 
                                threshold to bound the error. If negative is 
                                counted as infinity. (default -1)
    --noise         -n  noise   
                                Average of exponentially distributed additive 
                                latency noise, only for sensitivity.
                                (default 0)
    --output        -o  filepath
                                Filepath to use in the output file with the 
                                measurements (.csv and .json).
    --groundtruth   -g  filepath
                                Filepath of the ground truth.
    --campaign      -c  campaign_name
                                specify a campaign for measurements, results 
                                and groundtruth validations. Just put the name 
                                of the campaign not the path. The campaign 
                                directory must be created.
    --visualize     -v          Visualize the results. 
    """.format(DEFAULT_PROBES_PATH))
    sys.exit(0)


def main(argv):
    """Main function that execute on every run of iGreedy.
    Checks input arguments and decide what code needs to be executed.
    """

    # First check for help option
    if ("-h" in argv) or ("--help" in argv):
        print_help_text()

    # Variables needed to make the measurement and analysis
    global input_file, probes_file, gt_file, output_path, output_file
    global campaign_name
    global ip
    global threshold, alpha, visualize, noise, mesh_area
    global load_time, run_time

    maker_time = time.time()

    analyze_measurement = False

    # These sections parse the options selected and their values
    try:
        options, args = getopt.getopt(argv,
                                      "i:m:p:w:r:a:t:n:o:c:g:v",
                                      ["input",
                                       "measurement", "probes", "mesh-probes",
                                       "results",
                                       "alpha", "threshold", "noise",
                                       "output", "campaign", "groundtruth",
                                       "visualize"])
    except getopt.GetoptError as e:
        print(e)
        sys.exit(2)

    # This section set as variables the values of the different options used
    for option, arg in options:
        # Commands inputs checks
        if option in ("-i", "--input"):
            if not os.path.isfile(arg):
                print("Input file <" + arg + "> does not exist")
                sys.exit(2)
            else:
                input_file = arg

        elif option in ("-m", "--measurement"):
            ip = arg

        elif (ip is not None) and (input_file is not None):
            print("Sorry, you can't use input file and measurement options at "
                  "the same time.")
            sys.exit(2)

        # Options if measurement command selected
        elif option in ("-p", "--probes"):
            if not os.path.isfile(arg):
                print("Input file <{}> does not exist".format(arg))
                sys.exit(2)
            else:
                probes_file = arg

        elif option in ("-w", "--mesh_probes"):
            try:
                mesh_area = ast.literal_eval(json_file_to_dict(arg)["area"])
            except Exception as e:
                print("Probes mesh not recognized, try again")
                print(e)
        elif option in ("-r", "--results"):
            if arg.lower() == "true":
                analyze_measurement = True
            elif arg.lower() == "false":
                analyze_measurement = False
            else:
                print("Results option argument not valid. "
                      "Try with True or False")
                sys.exit(2)

        # Inputs for the analysis part
        elif option in ("-a", "--alpha"):
            alpha = float(arg)
            if alpha < 0 or alpha > 1:
                print("alpha must be [0,1], wrong choice:", alpha)
                sys.exit(2)
            print("Alpha selected: ", alpha)

        elif option in ("-n", "--noise"):
            noise = float(arg)
            print("Additive noise, mean: ", noise)

        if option in ("-t", "--threshold"):
            threshold = float(arg)
            print("Latency measurement threshold [ms]: ", threshold)

        # Other options
        if option in ("-o", "--output"):
            output_file = arg

        if option in ("-c", "--campaign"):
            campaign_name = arg
            output_path = RESULTS_CAMPAIGNS_PATH + campaign_name + "/"

        if option in ("-g", "--groundtruth"):
            if not os.path.isfile(arg):
                print("Ground-truth file <{}> does not exist".format(arg))
                sys.exit(2)
            else:
                gt_file = arg

        if option in ("-v", "--visualize"):
            visualize = True
            try:
                visualization_filepath = args[0]
            except:
                visualization_filepath = None

    # Print important values
    print('Airports info from:', IATA_file)
    readIATA()
    if input_file:
        analyze_measurement = True
        print('Measurement filepath:', input_file)
    if gt_file:
        print('Ground-truth filepath:', gt_file)
    # Insert directory path in output_file
    if analyze_measurement:
        output_file = output_path + output_file
        print('Output filepath:', output_file + ".{csv,json}")

    # If the measurement option selected make a new measurement
    if ip:
        print("Probes data from: ", probes_file)
        measure = Measurement(ip, mesh_area=mesh_area)
        ripe_probes_geo = measure.doMeasure(probes_file)
        numLatencyMeasurement, input_file = measure.retrieveResult(
            ripe_probes_geo, campaign_name)
        if numLatencyMeasurement < 2:
            print("Error: for the anycast detection at least 2 latency "
                  "measurement are needed")
            sys.exit(-1)

    # Analyze the data and print the time of process
    load_time = time.time() - maker_time
    maker_time = time.time()
    if analyze_measurement:
        measurement_data = json_file_to_dict(input_file)
        probes_file = measurement_data["probes_filepath"]
        ip = measurement_data["target"]
        analyze()
        output()
        if gt_file:
            gt_validation_filepath = compare_cities_gt(
                results_filepath=results_filename,
                gt_filepath=gt_file,
                campaign_name=campaign_name)
    run_time = time.time() - maker_time

    if visualize:
        if visualization_filepath == "" or visualization_filepath is None:
            if gt_file:
                visualization_filepath = gt_validation_filepath
            elif analyze_measurement:
                visualization_filepath = results_filename
            else:
                visualization_filepath = input_file
        plot_file(visualization_filepath)


if __name__ == "__main__":
    main(sys.argv[1:])
