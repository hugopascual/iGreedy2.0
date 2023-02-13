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




Introduction
-------------
Thanks for downloading iGreedy, a tool able to detect, enumerate and 
geolocate anycast replicas with a fistful of pings [1]. This brief readme
file describes the basic steps to get started with the tool. The tool
allows to  (i) analyze existing measurement or (ii) generate and analyze
new measurement (iii) visualize the measurement on a GoogleMap [2]. 
The package also contains (iv) datasets corredated  with ground-truth to 
assess the accuracy of the tool. A technical report detailing the iGreedy 
technique and dataset is available at:

        http://www.telecom-paristech.fr/~drossi/anycast



Installation
-------------
iGreedy should run out of the box. There is no python depenedency which 
we are aware of. All the code you need is in the code/ folder



Configuration
-------------
While running iGreedy on the provided datasets does not require any special
configuration, however to launch new measurement from RIPE Atlas you need to
(i) have a RIPE Atlas account (ii) have enough credits (iii) configure your
authentication. Measurement are launched by code/RIPEAtlas.py which is going
to read your RIPE Atlas key from the following file:

    datasets/auth


Usage
-------------
usage:     
     igreedy.py (-i input|-m target) [-o output] [-b browser (false)] 
                [-g groundtruth] [-a alpha (1)]  [-t threshold (\infty)] 

mandatory:
     -i input file
     -m IPV4 or IPV6 (real time measurements from Ripe Atlas using the ripe probes in datasets/ripeProbes) 
optional:
     -o output prefix (.csv,.json)
     -b browser (visualize a GoogleMap of the results in a browser)
     -g measured ground truth (GT) or publicly available information (PAI) files 
        (format: "hostname iata" lines for GT, "iata" lines for PAI)
     -a alpha (tune population vs distance score; was 0.5 in INFOCOM'15, now defaults to 1)
     -t threshold (discard disks having latency larger than threshold to bound the error; discouraged)


Run iGreedy on existing measurement
-------------------------------------


iGreedy can run on existing datasets, e.g., over F root server:

    ./igreedy -i datasets/measurement/f-ripe

Run iGreedy over the F root server dataset, showing results on a map (opening your browser):

    ./igreedy -i datasets/measurement/f-ripe -b

Run iGreedy over the F root server dataset, showing results and ground truth on a map (opening your browser):

    ./igreedy -i datasets/measurement/f-ripe -g ./igreedy -i datasets/ground-truth/f-ripe -b

Run iGreedy over the EdgeCast dataset, using publicly available information

    ./igreedy -i datasets/measurement/edgecast-ripe -g datasets/public-available-information/edgecast 

Run iGreedy over the EdgeCast dataset, using publicly available information

    ./igreedy -i datasets/measurement/cloudflare-planetlab -g datasets/ground-truth/cloudflare-planetlab 
  

Run iGreedy on new measurement from RIPE Atlas
----------------------------------------------

Note1: RIPE Atlas is instructed to vantage points contained in
            datasets/ripe-vps

Note2: You are free to use your favorite sets of vantage points by simply changing 
       the content of datasets/ripe-vps. We provide two example (ripe-vps.rand10 
       and ripe-vps.suggested200) that are conservative in the number of probes
       but useful for anecdotal use of:
        - detection (ripe-vps.rand10)
        - enumeration and geolocation (ripe-vps.suggested200)

Note3: The set of RIPE Atlas vantage points used by default (datasets/ripe-vps) is 
       conservative (10 random probes of ripe-vps.rand10) and useful at most for 
       detection (and to avoid burning all your credits with a for loop :)
       The set of ripe-vps.suggested200 is again very conservative and useful for 
       familiarizing with the tool before launching a measurement campaign. 

Note4: The set of measurements is saved in datasets/measurement for further post-processing

To run iGreedy on the F root server 192.5.5.241, configure your key (see above) then run:

       ./igreedy -m 192.5.5.241 -b


Have fun!
Danilo and Dario



References
----------

The technique is explained here:  
[1] D. Cicalese, D. Joumblatt, D. Rossi, M. Buob, J. Auge, T. Friedman,
    A Fistful of Pings: Accurate and Lightweight Anycast Enumeration and 
    Geolocation. In IEEE INFOCOM, Hong Kong, China, Apr 2015. 

The GoogleMap visualization was started here:
[2] D. Cicalese, D. Joumblatt, D. Rossi, M. Buob, J. Auge, T. Friedman,
    A Lightweight Anycast Enumeration and Geolocation. In IEEE INFOCOM, 
    Demo Session, Hong Kong, China, Apr 2015.

You can fine more resources and technical reports at:
[3] http://www.telecom-paristech.fr/~drossi/anycast
