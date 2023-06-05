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
from anycast import Anycast
from measurement import Measurement
from disc import *
from hunter import Hunter
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
hunter_target = None
hunter_origin = None
check_cf_ray = True
validate_last_hop = True
validate_hunter_target = False
probes_file = DEFAULT_PROBES_PATH
output_path = RESULTS_PATH
output_file = "output"
results_filename = ""
gt_file = None
campaign_name = None
alpha = 1  # advised settings
visualize = False
noise = 0  # exponential additive noise, only for sensitivity analysis

numberOfInstance = 0
truePositive = 0
falsePositive = 0
load_time = 0
run_time = 0
threshold = -1  # negative means infinity


class iGreedy:
    # TODO make a class of iGreedy to make it maintainable
    def __init__(self, target: str,
                 alpha=1, threshold=-1, noise=0):
        # Data to make measurement
        self._target = ""

        # Data to analyze the results
        self._alpha = alpha
        self._threshold = threshold
        self._noise = noise

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
            return

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


def output() -> bool:
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
    data["ping_radius_function"] = "constant_1.52"
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
    if len(data["anycast_instances"]) == 0:
        return False
    else:
        return True


def print_help_text() -> None:
    """Print the options available on iGreedy"""

    print(ASCIIART + """
Usage:  igreedy.py -i measurement_filepath [OPTIONS]
        igreedy.py -m IP_direction [-p probes_filepath] [-c boolean] [OPTIONS]
        igreedy.py -w 

Commands:
Either long or short options are allowed
    --input         -i  measurement_filepath
                                Input filepath which contains the data of an 
                                specific measurement to be analyzed.
    --measurement   -m  IP_direction
                                Real time measurements from Ripe Atlas using 
                                the ripe probes in datasets/ripeProbes.
    --hunter        -w  IP_direction
                                Use HUNTER to geolocate the server where your 
                                petition goes.

Parameters:
    --probes        -p  probes_filepath    
                                Filepath of the JSON document which contains 
                                the specification of the probes to use in the 
                                measurement (default "{}")
    --results       -r  boolean
                                Use it when you want that iGreedy automatically 
                                calculate the results based on the measurement 
                                realized. If not present iGreedy do not analyze 
                                the measurement results. (default False)

iGreedy Options:
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
    
Hunter Options:
    --origin        -s  "(latitude,longitude)"
                                Latitude and longitude from where Hunter will
                                start the tracking.
    --check_cf_ray  -y  boolean
                                Use it when you want to check if cf-ray used in
                                cloudfare CDN exists (default True)
    --val_last_hop  -l  boolean 
                                Use it when you want to validate that all 
                                directions in last_hop are equal (default 
                                True)
    --val_target    -k  boolean 
                                Use it when you want to check if the target is 
                                anycast before start hunting. (default False)
    
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
    global ip, hunter_target, hunter_origin, check_cf_ray, validate_last_hop
    global validate_hunter_target
    global threshold, alpha, visualize, noise
    global load_time, run_time

    maker_time = time.time()

    analyze_measurement = False

    # These sections parse the options selected and their values
    try:
        options, args = getopt.getopt(argv,
                                      "i:m:p:r:w:s:y:l:k:a:t:n:o:c:g:v",
                                      ["input",
                                       "measurement", "probes", "results",
                                       "hunter", "origin", "check_cf_ray",
                                       "val_last_hop", "val_target",
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
                
        elif option in ("-r", "--results"):
            if arg.lower() == "true":
                analyze_measurement = True
            elif arg.lower() == "false":
                analyze_measurement = False
            else:
                print("Results option argument not valid. "
                      "Try with True or False")
                sys.exit(2)

        # Hunter option
        elif option in ("-w", "--hunter"):
            hunter_target = arg

        elif option in ("-s", "--origin"):
            hunter_origin = ast.literal_eval(arg)

        elif option in ("-y", "--check_cf_ray"):
            if arg.lower() == "true":
                check_cf_ray = True
            elif arg.lower() == "false":
                check_cf_ray = False
            else:
                print("Argument not valid. Try with True or False")
                sys.exit(2)

        elif option in ("-l", "--val_last_hop"):
            if arg.lower() == "true":
                validate_last_hop = True
            elif arg.lower() == "false":
                validate_last_hop = False
            else:
                print("Argument not valid. Try with True or False")
                sys.exit(2)

        elif option in ("-k", "--val_target"):
            if arg.lower() == "true":
                validate_hunter_target = True
            elif arg.lower() == "false":
                validate_hunter_target = False
            else:
                print("Argument not valid. Try with True or False")
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
        measure = Measurement(ip)
        ripe_probes_geo = measure.doMeasure(probes_file)
        numLatencyMeasurement, input_file = measure.retrieveResult(
            ripe_probes_geo, campaign_name)
        if numLatencyMeasurement < 2:
            print("Error: for the anycast detection at least 2 latency "
                  "measurement are needed")
            sys.exit(-1)

    # Hunter option
    if hunter_target:
        hunter = Hunter(target=hunter_target)

        if hunter_origin:
            hunter.set_origin(hunter_origin)
        if output_file == (output_path + "output"):
            hunter.set_output_filename(output_file)

        hunter.set_check_cf_ray(check_cf_ray)
        hunter.set_validate_last_hop(validate_last_hop)
        hunter.set_validate_target_anycast(validate_hunter_target)

        hunter.hunt()

    # Analyze the data and print the time of process
    load_time = time.time() - maker_time
    maker_time = time.time()
    if analyze_measurement:
        measurement_data = json_file_to_dict(input_file)
        probes_file = measurement_data["probes_filepath"]
        ip = measurement_data["target"]
        analyze()
        is_target_anycast = output()
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

    if analyze_measurement:
        if is_target_anycast:
            sys.exit(0)
        else:
            sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
