#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# main user program to process  (./igreedy for help)
#---------------------------------------------------------------------.

# TODO: make a constants file, and import the values
# TODO: take auxiliar functions out of main file
# TODO: revise and document code

# external modules imports
import sys, getopt, math,  time
import os.path, json
import sys
from anycast import Anycast,Object
from measurement import Measurement
from disc import *
import webbrowser
from threading import Thread
# internal modules imports
from utils.constants import (
    AIRPORTS_INFO_FILEPATH,
    DEFAULT_PROBES_PATH,
    RESULTS_PATH,
    ASCIIART
)
from utils.functions import (
    json_file_to_dict,
    dict_to_json_file
)

# TODO: This variables could be constants or be inside a config file
# TODO: Study use of each one
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
gt_file = None
alpha = 1       # advised settings
browser  = False 
noise = 0       # exponential additive noise, only for sensitivity analysis

numberOfInstance = 0
truePositive = 0
falsePositive = 0 
load_time = 0
run_time = 0
threshold = -1 # negative means infinity


def airportDistance(a,b):
        if (a not in IATAlat) or  (b not in IATAlat):  
            return "NaN"  
        lat1 = IATAlat[a] 
        lat2 = IATAlat[b]
        lon1 = IATAlon[a] 
        lon2 = IATAlon[b] 

        # Convert latitude and longitude to 
        # spherical coordinates in radians.
        degrees_to_radians = math.pi/180.0
            
        # phi = 90 - latitude
        phi1 = (90.0 - lat1)*degrees_to_radians
        phi2 = (90.0 - lat2)*degrees_to_radians
            
        # theta = longitude
        theta1 = lon1*degrees_to_radians
        theta2 = lon2*degrees_to_radians
            
        # Compute spherical distance from spherical coordinates.
            
        # For two locations in spherical coordinates 
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) = 
        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length
        
        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
               math.cos(phi1)*math.cos(phi2))
        if (abs(cos - 1.0) <0.000000000000001):
            arc=0.0   
        else:
            arc = math.acos( cos )
            
        # Remember to multiply arc by the radius of the earth 
        # in your favorite set of units to get length.
        return arc*6371


def readIATA():
    """
    Routine to read IATA
    """
    #IATA size name lat long countryCode city pop heuristic h1 h2 h3
    global IATA_file, IATA, IATAlat, IATAlon, IATAcity
    temp = []
    data = open(IATA_file)
    data.readline() #consume header
    for line in data.readlines():
        stuff = line.strip().split("\t")
        iata = stuff[0].upper()
        temp.append(iata)
        latlon = stuff[3]
        (lat,lon) = latlon.split(" ")
        IATAlat[iata] = float(lat)
        IATAlon[iata] = float(lon)
        IATAcity[iata] = stuff[5]
    IATA = set(temp)
    IATAcity["NoCity"] = "NoCity"



def readGT():
    """
    Routine to read groundtruth(GT)( / public available information (PAI)
    """
    global gt_file, GT, PAI, GTnum, PAInum,GTtotal
    global IATA, IATAlat, IATAlon, IATAcity

    GTlist = []
    PAIlist = []
    temp=[]

    if not os.path.isfile(gt_file):
        return

    data = open(gt_file)
    for line in data.readlines():
        if line.startswith("#"):
            continue
        iata = ""
        fields = line.strip().split("\t")
        if(len(fields)==2):  
            #ground truth measured from a specific vantage point
            hostname  = fields[0]
            iata = fields[1].upper()
            GT[hostname] = iata
            if (iata not in IATA and hostname != "#hostname"):
                print("Weird ground truth: <" + iata + "> for <" + hostname + ">")

                #raw_input("Weird ground truth: <" + iata + "> for <" + hostname + ">\n"
                #"This ground truth will be not considered in the validation\n
                #Press Enter to continue...")

                # Actually the measurement should not be counted as we have 
                # information we do not know how to handle
                # Yet the following trick avoid run_time errors (key not found)

                IATAlat[iata]=0
                IATAlon[iata]=0
                IATAcity[iata]="Weird"
            else:
                GTlist.append( iata )

        elif(len(fields)==1):
            #publicly avlable information, but not tied to a specific host
            iata=fields[0].upper() 
            temp.append( iata )
            if (iata not in IATA):
                print("Weird publicly available information: <" + iata + ">")
                #"This ground truth will be not considered in the validation\n
                #Press Enter to continue...")
                # Actually the measurement should not be counted as we have 
                # information we do not know how to handle
                # Yet the following trick avoid run_time errors (key not found)

                IATAlat[iata]=0
                IATAlon[iata]=0
                IATAcity[iata]="Weird"
            else:
                PAIlist.append( iata ) 

        else:
            print("Unexpected ground truth format: " + line)

    PAI = set(PAIlist)   
    PAInum = len(set(PAIlist))
    GTtotal=set(GTlist)
    GTnum = len(set(GTlist))
    

def analyze():
    """Routine to iteratively enumerate and geolocate anycast instances"""

    global input_file, gt_file, IATA_file
    global alpha, browser, noise, threshold
    global numberOfInstance, discsSolution

    anycast=Anycast(input_file,IATA_file,alpha,noise,threshold)

    radiusGeolocated=0.1
    treshold=0      #tolerance, airport out of the disc
    iteration=True
    discsSolution=[]

    numberOfInstance=0
    while(iteration):

        iteration=False
        resultEnumeration=anycast.enumeration()
  
        numberOfInstance+=resultEnumeration[0]
        if(numberOfInstance<=1):
            print("No anycast instance detected")
            sys.exit()
        for radius, discList in resultEnumeration[1].getOrderedDisc().items(): 
            for disc in discList:
                # if the disc was not geolocated before, geolocate it!
                if(not disc[1]):
                    # used for the csv output
                    #discs.append(disc[0])      # append the disc to the results
                    
                    # remove old disc from MIS of disc
                    # MIS = Maximum Independent Set
                    resultEnumeration[1].removeDisc(disc)
                    
                    # result geolocation with the stadistics of airports
                    city=anycast.geolocation(disc[0],treshold)

                    #if there is a city inside the disc
                    if(city is not False):
                        # geolocated one disc, re-run enumeration!
                        iteration=True 
                        # save for the results the city. Used for .csv output
                        #markers.append(newDisc)

                        discsSolution.append((disc[0],city))
                        #insert the new disc in the MIS
                        resultEnumeration[1].add(
                            Disc("Geolocated",
                                 float(city[1]), 
                                 float(city[2]), 
                                 radiusGeolocated), 
                            True)
                          
                        break       # exit for rerun MIS
                    else:
                        # insert the old disc in the MIS
                        resultEnumeration[1].add(disc[0],True)
                        # disc, marker
                        discsSolution.append((disc[0],["NoCity",
                                                       disc[0].getLatitude(),
                                                       disc[0].getLongitude(),
                                                       "N/A",
                                                       "N/A"])) 
                        
            if(iteration):
                break


def output():
    """Routine to output results to a JSON (for GoogleMaps) and a CSV (for 
    further processing)
    """
    
    global input_file, output_file, gt_file
    global base, load_time, run_time

    global ip, probes_file
    global alpha, noise, threshold
        
    global numberOfInstance, discSolution, truePositive, falsePositive 
    global GT, PAI, IATAlat, IATAlon, IATAcity, GTnum, PAInum, weirdGtSolution
    weirdGtSolution=0

    # Format of result file if no name is provided
    # $ip_$probes-filename_$alpha_$threshold_$noise.json
    # If noise or threshold are the deafult values they do not appear
    result_filename = ""
    probes_filename = probes_file.split("/")[-1][:-5]
    if output_file == (output_path+"output"):
        if not ip:
            # If the result is from an input file, it use the same as the input
            result_filename = input_file.split("/")[-1][:-5] + "_" + str(alpha)
        else: 
            result_filename = probes_filename + "_" + ip + "_" + str(alpha)
        if threshold != -1:
            result_filename += "_" + str(threshold)
        if noise != 0:
            result_filename += "_" + str(noise)
        result_filename += ".json"
        result_filename = "./results/"+result_filename
    else:
        result_filename = output_file

    print("Number latency measurements: {}".format(len(
        json_file_to_dict(input_file)["measurement_results"])))
    print("Elapsed time (load+igreedy): %.2f (%.2f + %.2f)" % (
        load_time+run_time, load_time, run_time))
    print("Instances: ", str(numberOfInstance))

    # Comparing to the Ground-truth    
    if gt_file != None:
        print("Validation with ground truth or public available information:")
        errors = []
        Mlist = [] #list with the iata code present in the solution
        meanErr = 0
        pseudoVar = 0
        meanOld = 0
        #fragile
    
        for instance in discsSolution:  #circle to csv
            #comparing vs. GT or PAI
            iata = instance[1][0]
            gt=""
            Mlist.append( iata )   #measured airport instance 
            if GTnum>0: #if there is at least one GT
                gt = GT[instance[0].getHostname()]
                if(IATAcity[gt] == "Weird"):
                    weirdGtSolution+=1
                    continue
            if (gt == iata ):
                print("True Positive [GT] "+ gt +"("+ IATAcity[gt] +")")
                truePositive += 1
            elif (iata in PAI):
                print("True Positive [PAI] " + iata) 
                truePositive += 1
            else:
                if GTnum>0 : #if there is a gt
                    distance = airportDistance(gt, iata)
                elif PAInum>0: #if we are here should always go in one branch
                    distance=20000 #antipodes distance
                    if iata != "NoCity":
                        for airportPAI in PAI:
                            newDistance=airportDistance(iata,airportPAI)
                            if(newDistance<distance):
                               distance=newDistance
                               gt=airportPAI
                    else:
                        # CHECK WITH DARIO
                        print("Circle without city inside:validation not possible")
                        continue

                if IATAcity[gt] == IATAcity[iata]:
                    print("True Positive [SameCity] " + gt +"("+ IATAcity[gt] +") "+ iata +"("+ IATAcity[iata] +") ")
                    truePositive += 1

                elif(distance < 99):
                    '''
                    Neighboring airports as e..g, EWR and JFK for NewYork, 
                    despite they are not in the same City, they however serve 
                    the same population. 
                    The distance EWR, JFK is 33Km
                    Same thing for ORY, CDG and BVA for Paris: while PAR 
                    aggregates ORY and CDG, it does not include Beauvais (BVA). 
                    The distance BVA, ORY is 83Km.
                    Hence we select a threshold of 99Km (98.615940132), 
                    that corresponds to the distance the light travels in 1ms 
                    considering a fiber medium.
                    '''

                    print("True Positive [CloseCity] "+ gt +"("+ IATAcity[gt] +") "+ iata +"("+ IATAcity[iata] +") ")
                    truePositive += 1

                else:    
                    print("False Positive [ERROR!!!] "+ gt +"("+ IATAcity[gt] +") "+ iata +"("+ IATAcity[iata] +") ") 
                    falsePositive += 1
                    try:
                        meanErr += float((distance-meanOld)/float(falsePositive))
                        pseudoVar += float((distance-meanOld)*(distance-meanErr))
                        meanOld = meanErr
                        errors.append( distance )
                    except:
                        print ("cannot do much; distance is not a number likely \
                        because the selected City is not the provided IATA list")
                        pass    
                        # cannot do much; distance is not a number likely because 
                        # the selected City is not the provided IATA list                        
                        
        if falsePositive>1:                
            stdErr = math.pow(pseudoVar / (falsePositive-1), 0.5)
        else:
            stdErr = 0

        if weirdGtSolution>0:
            print("VPs with weird GT present in the solution:  %s" % (weirdGtSolution))

    # Save results as JSON
    data = dict()

    data["target"] = ip
    data["probes_filename"] = probes_file
    data["alpha"] = alpha
    data["threshold"] = threshold
    data["noise"] = noise
    data["num_anycast_instances"] = numberOfInstance
    data["anycast_intances"] = []
    for instance in discsSolution:
        # circle
        tempCircle=instance[0]
        circle = dict()
        circle["id"]= tempCircle.getHostname()
        circle["latitude"]= tempCircle.getLatitude()
        circle["longitude"]= tempCircle.getLongitude()
        circle["radius"]= tempCircle.getRadius()
        # marker
        tempMarker=instance[1]
        marker = dict()
        marker["id"]= tempMarker[0]
        marker["latitude"]= tempMarker[1]
        marker["longitude"]= tempMarker[2]
        marker["city"]=tempMarker[3]
        marker["code_country"]=tempMarker[4]
        # union of circle and marker
        markCircle= dict()
        markCircle["marker"]=marker
        markCircle["circle"]=circle
        data["anycast_intances"].append(markCircle)
    
    dict_to_json_file(data, result_filename)

def threaded_browser():
    url = "./code/webDemo/demo.html"
    webbrowser.open(url,new=2)      # open in a new tab, if possible

def help():
    """Print the options avaliable on iGreedy"""  

    print (ASCIIART + """
Usage:  igreedy.py -i measurement_filepath [ OPTIONS ]
        igreedy.py -m IP_direction [ -p probes_filepath ] [ -c boolean ] [ OPTIONS ]

Commands:
Either long or short options are allowed
    --input         -i  measurement_filepath
                                Input filepath which contains the data of an 
                                specific measurement to be analyzed.
    --measurement   -m  IP_direction
                                Real time measurements from Ripe Atlas using the
                                ripe probes in datasets/ripeProbes. IPV4/IPv6.

Parameters:
    --probes        -p  probes_filepath    
                                Filepath of the JSON document which contains the
                                specification of the probes to use in the 
                                measurement (default "{}")
    --calculate     -c  boolean        
                                Use it when you want that iGreedy automaticaly 
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
                                latency noise, only for sensitivity. (default 0)
    --output        -o  filepath
                                Filepath to use in the output file with the 
                                measurements (.csv and .json).
    --groundtruth   -g  filepath
                                Filepath of the ground truth.
    --visualize     -v          Visualize the results. 
    """.format(DEFAULT_PROBES_PATH))

    sys.exit(0)

def main(argv):
    """Main function that execute on every run of igreedy.
    Checks input arguments and decide what code needs to be executed.
    """

    # First check for help option
    if ("-h" in argv) or ("--help" in argv):
        help()

    # Varibles needed to make the measurement and analisis
    global input_file, probes_file, ip
    global gt_file, output_path, output_file, threshold, alpha, browser, noise
    global load_time, run_time

    maker_time = time.time()

    analyze_measurement = False

    # This sections parse the options selected and their values
    try:
        options, args = getopt.getopt(argv, 
                                      "i:m:p:c:a:t:n:o:g:v", 
                                      ["input",
                                       "measurement", "probes", "calculate",
                                       "alpha", "threshold", "noise",
                                       "output", "groundtruth", "visualize"])
    except getopt.GetoptError as e:
        print(e)

    # This section set as variables the values of the different options used
    for option, arg in options:
        # Commands inputs checks
        if option in ("-i", "--input"):
            if not os.path.isfile(arg):
                print ("Input file <"+arg+"> does not exist")
                sys.exit(2)
            else: 
                input_file = arg
                
        elif option in ("-m", "--measurement"):
            ip = arg

        elif (ip != None) and (input_file != None):
            print ("Sorry, you can't use input file and measurement options at the same time.")
            sys.exit(2)

        # Options if measurement command selected
        elif option in ("-p", "--probes"):
            if not os.path.isfile(arg):
                print ("Input file <{}> does not exist".format(arg))
                sys.exit(2)
            else: 
                probes_file = arg

        elif option in ("-c", "--calculate"):
            if arg.lower() == "true":
                analyze_measurement = True
            elif arg.lower() == "false":
                analyze_measurement = False
            else:
                print("Argument for -c option not valid. Try with True or False")
                sys.exit(2)

        # Inputs for the analysis part
        elif option in ("-a", "--alpha"):
            alpha = float(arg)
            if alpha<0 or alpha>1:
                print ("alpha must be [0,1], wrong choice:", alpha)
                sys.exit(2)
            print("Alpha selected: ", alpha)

        elif option in ("-n", "--noise"):
            noise = float(arg)
            print ("Additive noise, mean: ", noise)
        
        if option in ("-t", "--threshold"):
            threshold = float(arg)
            print ("Latency measurement threshold [ms]: ", threshold)

        # Other options
        if option in ("-o", "--output"):
            output_file = arg
        
        if option in ("-g", "--groundtruth"):
            if not os.path.isfile(arg):
                print ("Ground-truth file <{}> does not exist".format(arg))
                sys.exit(2)
            else: 
                gt_file = arg
        
        if option in ("-v", "--visualize"):
            browser = True

    # Print important values to inform the user about the parameters are going to be used
    print ('Airports info from:', IATA_file)
    readIATA()
    if input_file:
        print ('Measurement filepath:', input_file)
    if gt_file:
        print ('Ground-truth filetpath:', gt_file)
        readGT()
    # Insert directory path in output_file
    if analyze_measurement or input_file:
        output_file = output_path + output_file
        print ('Output filepath:', output_file + ".{csv,json}")

    # If the measurement option is used make a new measurement to get the latency records
    if ip:
        print("Probes data from: ", probes_file)
        measure=Measurement(ip)
        ripe_probes_geo = measure.doMeasure(probes_file)
        numLatencyMeasurement, input_file=measure.retrieveResult(ripe_probes_geo)
        if(numLatencyMeasurement<2):
            print("Error: for the anycast detection at least 2 latency measurement are needed")
            sys.exit(-1)

    # Analyze the data and get a mark of time spend getting the data and analyzing it 
    load_time = time.time() - maker_time
    maker_time = time.time()
    if analyze_measurement or input_file:
        analyze()
    run_time = time.time() - maker_time
    output()

    # TODO: Check webDemo files because the code does not work
    if browser:
        os.rename(output_file+".json", "code/webDemo/data/anycastJson/output.json")
        # open a public URL, in this case, the webbrowser docs
        thread = Thread(target = threaded_browser)
        thread.start()

if __name__ == "__main__":
    main(sys.argv[1:])
