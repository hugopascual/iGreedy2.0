#!/usr/bin/env python3
#----------------------------------------------------------------------
# detection, enumeration and geolocation helper routines called by the
# main program (igreedy.py)
#---------------------------------------------------------------------.
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


from disc import *
import collections
import json,sys
import random

#class for print in Json
class Object:
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class Anycast(object):
    #def __init__(self,infile,airportFile=0,alpha):
    def __init__(self,infile,airportFile,alpha,noise=0,threshold=-1):
        self.alpha=float(alpha)
        self._setDisc={} #disc from the input 
        self._discsMis = Discs() #disc belong maximum indipendent set
        self._airports={}
        data = open(infile)
        data.readline()
        
        #------------------load data in a structure has as key the ping---------------
        #Example structure:  {ping1:[Disc1,Disc2,Disc3],ping2:[Disc3,Disc4,Disc5]}    
        for line in data.readlines():
            try:
                #Thou shall not mix measurement and groundtruth.
                #hostname,latitude,longitude,gt,ping= line.strip().split("\t")
                hostname,latitude,longitude,minRTT= line.strip().split("\t")
                if hostname.startswith("#"):
                    continue
            except:
                print("problem with input line:" + line)
                sys.exit(0)

            # additive controlled noise (negative exponential distribution) to make problem harder ;)
            if noise>0:
               minRTT = float(minRTT)
               minRTT += float(random.expovariate(1/noise))

            if not ( float(minRTT) > threshold and threshold > 0):
                if(self._setDisc.get(float(minRTT)) is None):
                    self._setDisc[float(minRTT)]=[Disc(hostname,float(latitude),float(longitude),float(minRTT))]
                else:                
                    self._setDisc[float(minRTT)].append(Disc(hostname,float(latitude),float(longitude),float(minRTT)))
        data.close()
        self._orderDisc=collections.OrderedDict(sorted(self._setDisc.items())) #order the discs by ping
        #------------------load airport---------------
        if(airportFile!=0):        
            airportLines = open(airportFile)
            airportLines.readline()    
            for line in airportLines.readlines():
                iata,size,name,latLon,country_code,city,popHeuristicGooglemapslonlat=line.strip().split("\t")
                latitude,longitude=latLon.strip().split()
                pop,Heuristic,lon,lat=popHeuristicGooglemapslonlat.strip().split()
                self._airports[iata]=[float(latitude),float(longitude),int(pop),city,country_code]           
            airportLines.close()
 
    def detection(self):
        self._discsMis = Discs()
        for ping, setDiscs in self._orderDisc.iteritems(): 
            for disc in setDiscs:
                if not self._discsMis.overlap(disc):
                    self._discsMis.add(disc,False)
                    if(len(self._discsMis)>1):
                        return True
        return False
    
    def enumeration(self):
        numberOfDisc=0
        for ping, setDiscs in self._orderDisc.iteritems(): 
            for disc in setDiscs:
                if not self._discsMis.overlap(disc):
                    numberOfDisc+=1
                    self._discsMis.add(disc,False)
        return [numberOfDisc,self._discsMis]    

    def geolocateCircle(self,disc,airportsSet):
        #alpha parameter for the new igreedy with population
        totalPopulation=0
        totalDistanceFromCenter=0
        chosenCity=""
        oldscore=0
        score=0

        for iata, airportInfo in airportsSet.iteritems(): #_airports[iata]=[float(latitude),float(longitude),int(pop),city,country_code]
            totalPopulation+= airportInfo[2]
            totalDistanceFromCenter+=disc.distanceFromTheCenter(airportInfo[0],airportInfo[1])

        for iata, airportInfo in airportsSet.iteritems(): #_airports[iata]=[float(latitude),float(longitude),int(pop),city,country_code]
            popscore = float(airportInfo[2])/float(totalPopulation)
            distscore = float(disc.distanceFromTheCenter(airportInfo[0],airportInfo[1]))/float(totalDistanceFromCenter)

            #alpha=tunable knob
            score=  self.alpha*popscore + (1-self.alpha)*distscore

            if(score>oldscore):
                chosenCity=[iata,airportInfo[0],airportInfo[1],airportInfo[3],airportInfo[4]]
                oldscore=score
        if(score==0):
            return False
        else:
            return chosenCity
    
    def geolocation(self,disc,treshold): 
        geolocatedInstance=[] 
        maxPopulation=0
        geolocatedInstanceOut=[]
        maxPopulationOut=0
        airportsInsideDisk={}
        """
        listIataInside=[]
        listPopulation=[] 
        listDistanceFromCenter=[]
        listCityInside=[]
        """

        for iata, airportInfo in self._airports.iteritems(): #_airports[iata]=[float(latitude),float(longitude),int(pop),city,country_code]
            distanceFromBorder=disc.getRadius()-disc.distanceFromTheCenter(airportInfo[0],airportInfo[1])
#create a subset of airport inside the disk and after decide witch one is the one we guess
            if(distanceFromBorder>0): #if the airport is inside the disc
                airportsInsideDisk[iata]=airportInfo

        return self.geolocateCircle(disc,airportsInsideDisk)
        """
                 listIataInside.append(iata)
                 if(airportInfo[3]  not in listCityInside):
                     listPopulation.append(airportInfo[2])
                     listCityInside.append(airportInfo[3])
                     listDistanceFromCenter.append(disc.distanceFromTheCenter(airportInfo[0],airportInfo[1]))
        """

        """
                 if(airportInfo[2]>maxPopulation): #check if the city is more populated
                    geolocatedInstance=[iata,airportInfo[0],airportInfo[1],airportInfo[3],airportInfo[4]]#save the city with the highest population
                    maxPopulation=airportInfo[2] #update the maxPopulation
            elif(maxPopulation==0 and distanceFromBorder>-treshold ): #if there is no city inside yet and the distance is smaller than the threshold 
                if(airportInfo[2]>maxPopulationOut):#check if the city is more populated
                    geolocatedInstanceOut=[iata,airportInfo[0],airportInfo[1]]#save the city with the highest population
                    maxPopulationOut=airportInfo[2] #update the maxPopulation
        """
#-----geolocation fig jsac
#        print disc.getHostname()+"\t"+str(disc.getRadius())+"\t"+str(len(listCityInside))+"\t"+",".join(listIataInside)+"\t"+','.join(str(x) for x in listCityInside)+"\t"+','.join(str(x) for x in listPopulation)+"\t"+','.join(str(x) for x in listDistanceFromCenter)
#-----geolocation fig jsac
        """
        if(maxPopulation!=0):
            return geolocatedInstance
        elif(maxPopulationOut!=0):
            return geolocatedInstanceOut
        return False #no airports inside
        """

