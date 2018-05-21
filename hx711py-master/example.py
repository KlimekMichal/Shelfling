import RPi.GPIO as GPIO
import time
import sys
import urllib2
import requests
from hx711 import HX711
from numpy import median

def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()

def process_data(value):
    data=value/1400
    data=int(round(data,0))
    if(data==-1):
        data=0;
    prt = "Liczba puszek: " + str(data)
    print (prt)
    contents = urllib2.urlopen("http://intshelf.azurewebsites.net/api/up/6").read()
    values = contents.split('},')
    for index,value in enumerate(values):
        value= value.translate(None, '}]')
        value= value.rpartition(':')[2]
    values[0]=values[0].rpartition(':')[2]
    ile=int(values[0])-data
    if(ile>0):
        updating(1,0,int(ile))
    elif(ile<0):
            updating(1,1,abs(int(ile)))
    elif(ile==0):
        time.sleep(0.1)
        
        #data = "Segment nr " +str(index+1) + " zawiera " + str(value.rpartition(':')[2]) + " puszek"
        #print (int(value.rpartition(':')[2]))
        
    
def updating(id,waga,ile):
        link='https://intshelf.azurewebsites.net/api/'
        print(ile)
        if(int(waga)==1):
            link=link+'up/'+str(id)
            print (link)
            for _ in range(ile): 
                r=requests.get(link)
                ile=-1
        else:
            link=link+'down/'+str(id)
            print (link)   
            for _ in range(ile):
                r=requests.get(link)
                ile=-1
time.sleep(15)            
hx = HX711(5, 6)

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("LSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(20)

hx.reset()
hx.tare()
val = [0,0,0,0,0]
while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment the three lines to see what it prints.
        #n#p_arr8_string = hx.get_np_arr8_string()
        #binary_string = hx.get_binary_string()
        #print binary_string + " " + np_arr8_string
        #
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        licznik=0;
        while licznik<4:
            val[licznik] = hx.get_weight(5)
            #print (hx.get_weight(5))
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)
            licznik+=1
        process_data(median(val))
        #print(sum(val)/len(val))
        time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
