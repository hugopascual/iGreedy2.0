#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# main user program to process  (./igreedy for help)
#---------------------------------------------------------------------.

# TODO: make a constants file, and import the values
# TODO: take auxiliar functions out of main file
# TODO: revise and document code

asciiart = """
180 150W  120W  90W   60W   30W  000   30E   60E   90E   120E  150E 180
|    |     |     |     |     |    |     |     |     |     |     |     |
+90N-+-----+-----+-----+-----+----+-----+-----+-----+-----+-----+-----+
|          . _..::__:  ,-"-"._       |7       ,     _,.__             |
|  _.___ _ _<_>`!(._`.`-.    /        _._     `_ ,_/  '  '-._.---.-.__|
|.{     " " `-==,',._\{  \  / {)     / _ ">_,-' `                mt-2_|
+ \_.:--.       `._ )`^-. "'      , [_/( G        e      o     __,/-' +
|'"'     \         "    _L       0o_,--'                )     /. (|   |
|         | A  n     y,'          >_.\\._<> 6              _,' /  '   |
|         `. c   s   /          [~/_'` `"(   l     o      <'}  )      |
+30N       \\  a .-.t)          /   `-'"..' `:._        c  _)  '      +
|   `        \  (  `(          /         `:\  > \  ,-^.  /' '         |
|             `._,   ""        |           \`'   \|   ?_)  {\         |
|                `=.---.       `._._ i     ,'     "`  |' ,- '.        |
+000               |a    `-._       |     /          `:`<_|h--._      +
|                  (      l >       .     | ,          `=.__.`-'\     |
|                   `.     /        |     |{|              ,-.,\     .|
|                    |   ,'          \ z / `'            ," a   \     |
+30S                 |  /             |_'                |  __ t/     +
|                    |o|                                 '-'  `-'  i\.|
|                    |/                                        "  n / |
|                    \.          _                              _     |
+60S                            / \   _ __  _   _  ___ __ _ ___| |_   +
|                     ,/       / _ \ | '_ \| | | |/ __/ _` / __| __|  |
|    ,-----"-..?----_/ )      / ___ \| | | | |_| | (_| (_| \__ \ |_ _ |
|.._(                  `----'/_/   \_\_| |_|\__, |\___\__,_|___/\__| -|
+90S-+-----+-----+-----+-----+-----+-----+--___/ /--+-----+-----+-----+
     Based on 1998 Map by Matthew Thomas   |____/ Hacked on 2015 by 8^/  

"""

import sys, getopt, math,  time
import os.path, json

#./igreedy.py inputFile outputFile json <----json output
#inputFile: separated by \t:hostname\tlatitude\tlongitude\tping
#outputFile:

import sys
from anycast import Anycast,Object
from measurement import Measurement
from disc import *
import webbrowser
from threading import Thread

# TODO: This variables could be constants or be inside a config file
# TODO: Study use of each one
iatafile = './datasets/airports.csv'
infile = ''
outfile = 'output'
outformat = "csv"
gtfile = ''
alpha = 1  #advised settings
browser  = False 
noise = 0  #exponential additive noise, only for sensitivity analysis

IATA = []
IATAlat = {}
IATAlon = {}
IATAcity = {}

PAI = []
GT = {}
PAInum = 0
GTnum = 0

input_file = ''
probes_file = './probes_sets/ripe_probes.json'
output_path = './results/'
output_file = 'output'
outformat = "csv"
gt_file = ''
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

    global input_file, output_file, gt_file, IATA_file
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
        for radius, discList in resultEnumeration[1].getOrderedDisc().iteritems(): 
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
    
    global input_file, output_file, outformat, gt_file
    global alpha, base, load_time, run_time
        
    global numberOfInstance, discSolution, truePositive, falsePositive 
    global GT, PAI, IATAlat, IATAlon, IATAcity, GTnum, PAInum, weirdGtSolution
    weirdGtSolution=0

    # Results as a CSV    
    csv=open(output_file + ".csv","w")
    csv.write("#hostname\tcircleLatitude\tcircleLongitude\t" +\
                    "radius\tiataCode\tiataLatitude\tiataLongitude\n")
    for instance in discsSolution:      # circle to csv
        csv.write(instance[0].getHostname()+"\t"+\
                    str(instance[0].getLatitude())+"\t"+\
                    str(instance[0].getLongitude())+"\t"+\
                    str(instance[0].getRadius())+"\t"+\
                    str(instance[1][0])+"\t"+\
                    str(instance[1][1])+"\t"+\
                    str(instance[1][2])+"\n")
    csv.close()
    print("Number latency measurements: " + sum(1 for line in open(input_file)) -1)
    print("Elapsed time (load+igreedy): %.2f (%.2f + %.2f)" % (
        load_time+run_time, load_time, run_time))
    print("Instances: ", str(numberOfInstance))

    # Comparing to the Ground-truth    
    if gt_file != "":
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
                if(IATAcity[gt] is "Weird"):
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
                    if iata is not "NoCity":
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

    # Results as a JSON    
    data=Object()
    data.count= numberOfInstance
    data.instances=[]
    data.countGT=GTnum
    data.markerGT=[]
    for instance in discsSolution:
            #circle to Json
            tempCircle=instance[0]
            circle=Object()
            circle.id= tempCircle.getHostname()
            circle.latitude= tempCircle.getLatitude()
            circle.longitude= tempCircle.getLongitude()
            circle.radius= tempCircle.getRadius()
            #marker to Json
            tempMarker=instance[1]
            marker=Object()
            marker.id= tempMarker[0]
            marker.latitude= tempMarker[1]
            marker.longitude= tempMarker[2]
            marker.city=tempMarker[3]
            marker.code_country=tempMarker[4]
            markCircle=Object()
            markCircle.marker=marker
            markCircle.circle=circle
            data.instances.append(markCircle)
    if GTnum>0:
        for gt in GTtotal:
            markerGT=Object()
            markerGT.id= gt
            markerGT.latitude= IATAlat[gt] 
            markerGT.longitude= IATAlon[gt]
            data.markerGT.append(markerGT)


    json=open(output_file + ".json","w")
    json.write("var data=\n")
    json.write(data.to_JSON())
    json.close()

def threaded_browser():
    url = "./code/webDemo/demo.html"
    webbrowser.open(url,new=2)      # open in a new tab, if possible
    


def help():
    """Print the options avaliable on iGreedy"""  

    print (asciiart + """
Usage:  igreedy.py -i filename [ OPTIONS ]
        igreedy.py -m IP_direction [ -p filename ] [ OPTIONS ]

          -o output   [-n noise (0)]  [-t threshold (\infty)]  

Commands:
Either long or short options are allowed
    --input -i  filename        Input filename which contains the data of an 
                                specific measurement to be analyzed
    --measurement   -m  IP_direction
                                Real time measurements from Ripe Atlas using the
                                ripe probes in datasets/ripeProbes. IPV4/IPv6.

Parameters:
    --probes    -p  filename    
                                Filename of the JSON document which contains the
                                specification of the probes to use in the 
                                measurement (default 
                                "probes_sets/ripe_probes.json")

where:
    -i input file
    -o output prefix (.csv,.json)
    -g measured ground truth (GT) or publicly available information (PAI) files 
    (format: "hostname iata" lines for GT, "iata" lines for PAI)
    -a alpha (tune population vs distance score, see INFOCOM'15)
    -b browser (visualize the results in a browser with a map)
    -n noise (average of exponentially distributed additive latency noise; only for sensitivity)
    -t threshold (discard disks having latency larger than threshold to bound the error)
    -m IPV4 or IPV6 (real time measurements from Ripe Atlas using the ripe probes in datasets/ripeProbes) 
    """)

    sys.exit(0)

def main(argv):
    """Main function that execute on every run of igreedy.
    Checks input arguments and decide what code needs to be executed.
    """

    global input_file, probes_file
    global gt_file, output_path, output_file, threshold, alpha, browser, noise
    global load_time, run_time

    maker_time = time.time()
    ip=""

    # This sections gets the options used and their values    
    try:
        options, args = getopt.getopt(argv, 
                                      "h:i:m:p:a:n:t:o:g:b", 
                                      ["help",
                                       "input",
                                       "measurement", "probes", 
                                       "alpha", "noise", "threshold",
                                       "output", "groundtruth", "browser"])
    except getopt.GetoptError:
        help()

    # This section set as variables the values of the different options used
    for option, arg in options:
        if option in ("-h", "--help"):
            help()
        
        # Basic inputs checks
        if option in ("-i", "--input"):
            if not os.path.isfile(arg):
                print ("Input file <"+arg+"> does not exist")
                sys.exit(2)
            else: 
                input_file = arg
        
        if option in ("-m", "--measurement"):
            ip = arg

        if (ip != '') and (input_file != ''):
            print ("Sorry, you can't use input file and measurement options at the same time.")
            sys.exit(2)

        # Options if measurement command selected
        if (option in ("-m", "--measurement")) and (option in ("-p", "--probes")):
            if not os.path.isfile(arg):
                print ("Input file <"+arg+"> does not exist")
                sys.exit(2)
            else: 
                probes_file = arg

        # Inputs for the analysis part
        if option in ("-a", "--alpha"):
            alpha = float(arg)
            if alpha<0 or alpha>1:
                print ("alpha must be [0,1], wrong choice:", alpha)
                sys.exit(-1)
        
        if option in ("-n", "--noise"):
            noise = float(arg)
            print ("Additive noise, mean: ", noise)
        
        if option in ("-t", "--threshold"):
            threshold = float(arg)
            print ("Latency measurement threshold [ms]: ", threshold)

        # Optional quality of life options
        if option in ("-o", "--output"):
            output_file = arg
        output_file = output_path + output_file
        
        if option in ("-g", "--groundtruth"):
            if not os.path.isfile(arg):
                print ("Ground-truth file <"+arg+"> does not exist")
                sys.exit(2)
            else: 
                gt_file = arg
        
        if option in ("-b", "--browser"):
            browser = True

    # Print th values to inform the user about the parameters are going to be used
    print ('Airports:', IATA_file)
    readIATA()
    if input_file:
        print ('Measurement:', input_file)
    if gt_file:
        print ('Ground-truth:', gt_file)
        readGT()
    if output_file:
        print ('Output:', output_file + ".{csv,json}")

    # If the measurement option is used make a new measurement to get the latency records
    # TODO: check how this works
    if ip:
        measure=Measurement(ip)
        ripe_probes_geo = measure.doMeasure(probes_file)
        numLatencyMeasurement,input_file=measure.retrieveResult(ripe_probes_geo)
        if(numLatencyMeasurement<2):
            print >>sys.stderr, ("Error: for the anycast detection at least 2 latency measurement are needed")
            sys.exit(-1)

    # Analyze the data and get a mark of time spend getting the data and analyzing it 
    load_time = time.time() - maker_time
    maker_time = time.time()
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
