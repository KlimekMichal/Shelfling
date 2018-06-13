import RPi.GPIO as GPIO
import time
import re
import sys
import urllib2
import requests
import json
from hx711 import HX711
from numpy import median

def cleanAndExit():
	print ("Cleaning...")
	GPIO.cleanup()
	print "Bye!"
	sys.exit()
	
class Line :
    
    def __init__(self,a_id,a_weight,a_quan,a_quan_max):
        self.id = a_id
        self.weight = a_weight
        self.quan = a_quan
        self.quan_max = a_quan_max

for x in range(0,60):  # try 4 times
    try:
        # msg.send()
        contents = urllib2.urlopen("http://intshelf.azurewebsites.net/api/info").read()
        str_error = None
    except Exception as str_error:
        pass
    if str_error:
        time.sleep(5)  # wait for 2 seconds before trying to fetch the data again
    else:
        break
    
lines=[]

jvar=json.loads(contents)

for i in range(6):
    lines.append(Line(i+1,jvar[i]['Weight'],jvar[i]['Quantity'],jvar[i]['MaxQuantity']))


def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()

def updating(id,waga,ile): ## waga=1 to w / waga!=1 to w 
        link='https://intshelf.azurewebsites.net/api/'
        rtr=ile
        if(int(waga)==1):
            link=link+'up/'+str(id)
            for _ in range(ile): 
                r=requests.get(link)
                ile=-1
            return rtr
        else:
            link=link+'down/'+str(id)  
            for _ in range(ile):
                r=requests.get(link)
                ile=-1
            return (0-rtr)

def somethingIsNotRight(id,isRight): #Jak 1 to na czerwono, co innego na normalnie
    link='https://intshelf.azurewebsites.net/api/'
    if(isRight==1):
        link=link + 'warning/'
    else:
        link=link + 'normal/'
    link = link + str(id)
    r=requests.get(link)

def isAllRight(id,weightShelf,weightOfOne,quantity,maxQuantity,numOfElements):
    if (numOfElements==0):
        if (weightShelf>=0+weightOfOne*0.07):
            somethingIsNotRight(id,1)
        else:
            somethingIsNotRight(id,0)
        return 0
    elif (weightShelf>=float(numOfElements*weightOfOne+numOfElements*weightOfOne*0.1) or weightShelf<=float(numOfElements*weightOfOne-(numOfElements*weightOfOne*0.1))):
        print (numOfElements*weightOfOne+numOfElements*weightOfOne*0.1)
        somethingIsNotRight(id,1)
        return 0
    elif (numOfElements>maxQuantity):
        somethingIsNotRight(id,1)
        return 0
    somethingIsNotRight(id,0)
    return 0

def process_data(id,weightShelf,weightOfOne,quantity,maxQuantity):
    numberOfElem=float(round(weightShelf/weightOfOne,0))   #liczba elementow
    #numberOfElem=int(round(numberOfElem))    #zaokrglona do najbliszej calkowitej
    ############### Waga wyszla dodatnia: ################
    #prt = "Liczba puszek: " + str(numberOfElem)
    #print (prt)
    
    ################## Korekcja wyswietlanego wyniku##############################
    ile = numberOfElem-quantity
    if(ile>0):
        updating(id,1,abs(int(ile)))
    elif(ile<0):
        updating(id,0,abs(int(ile)))
 
    #################################################################################
        
    ############### Sprawdzam czy na polce znajduja sie tylko farby ################# 
    isAllRight(id,weightShelf,weightOfOne,quantity,maxQuantity,numberOfElem)
    ##################################################################################


hx_tab=[None]*7
print("start")
hx_tab[1]=HX711(5, 6)
hx_tab[2]=HX711(20,21)
hx_tab[3]=HX711(4,17)
hx_tab[4]=HX711(22,27)
hx_tab[5]=HX711(18,24)
hx_tab[6]=HX711(13,19)

print("start1")
##############Tu bedzie potrzebna petla do ustawienia formatu czytania #############################
for i in range (6):
    hx_tab[i+1].set_reading_format("LSB", "MSB")
####################################################################################################

########################### PETLA DO JEDNOSTEK ODNIESIENIA #########################################
hx_tab[1].set_reference_unit(20.5)
hx_tab[2].set_reference_unit(20)
hx_tab[3].set_reference_unit(20)
hx_tab[4].set_reference_unit(19.5)
hx_tab[5].set_reference_unit(20)
hx_tab[6].set_reference_unit(20)
####################################################################################################
print("start2")
###############################PETLA DO RESTARTU####################################################
for i in range (6):
    hx_tab[i+1].reset()
    hx_tab[i+1].tare()
####################################################################################################
somethingIsNotRight(1,1)
time.sleep(2)
somethingIsNotRight(1,0)
j_initialize=json.loads(urllib2.urlopen("http://intshelf.azurewebsites.net/api/info").read())

initial_weights=[]*6

for i in range(len(initial_weights)):
    initial_weights[i]=j_initialize[i]['Quantity']

w_1=j_initialize[0]['Quantity']


while True:
    try:
        contents = urllib2.urlopen("http://intshelf.azurewebsites.net/api/info").read()

        lines=[]
        
        valz=[None]*6

        jvar=json.loads(contents)

        for i in range(6):
            lines.append(Line(i+1,jvar[i]['Weight'],jvar[i]['Quantity'],jvar[i]['MaxQuantity']))


   
        for i in range(6):
	    result=[None]*5
	    for j in range(5):
		result[j]=hx_tab[i+1].get_weight(5)
            valz[i]=median(result)
            #valz[i]=hx_tab[i+1].get_weight(5)
            if(valz[i]<=0):
                valz[i]=0;
            process_data(i+1,valz[i],lines[i].weight,lines[i].quan,lines[i].quan_max)
            prt = "Segment nr " + str(i+1) + ": " + str(valz[i])
            print (prt)

        
        ############ ZEBY POBRAC WYNIKI OD NOWA, ZA CHWILE ###########################
        for i in range(6):
            hx_tab[i+1].power_down()
            hx_tab[i+1].power_up()
       ################################################################# 
            


        
        
        
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()