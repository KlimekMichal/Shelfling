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

contents = urllib2.urlopen("http://intshelf.azurewebsites.net/api/info").read()

lines=[]

jvar=json.loads(contents)

for i in range(6):
    lines.append(Line(i+1,jvar[i]['Weight'],jvar[i]['Quantity'],jvar[i]['MaxQuantity']))


def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()

def updating(id,waga,ile): ## waga=1 to w górę / waga!=1 to w dół
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

def somethingIsNotRight(id,isRight): #Jak 1 to na czerwono, coś innego na normalnie
    link='https://intshelf.azurewebsites.net/api/'
    if(isRight==1):
        link=link + 'warning/'
    else
        link=link + 'normal/'
    link = link + str(id)
    r=requests.get(link)

def process_data(id,weightShelf,weightOfOne,quantity,maxQuantity):
    numberOfElem=weightShelf/weightOfOne   #liczba elementów
    numberOfElem=int(round(numberOfElem,0))    #zaokrąglona do najbliższej całkowitej
    if(numberOfElem==-1): #Jeżeli waga mocno ujemna to coś nie tak
        numberOfElem=0
        somethingIsNotRight(id,1)
    else:
        somethingIsNotRight(id,0)
    ############### Waga wyszła dodatnia: ################
    prt = "Liczba puszek: " + str(numberOfElem)
    print (prt)

    ################## Korekcja ##############################
    ile = numberOfElem-quantity
    if(ile>0):
        updating(1,0,abs(int(ile)))
    elif(ile<0):
            updating(1,1,abs(int(ile)))
    elif(ile==0):
        time.sleep(0.1) 
    #################################################################################

    ############### Sprawdzam czy na półce znajdują się tylko farby ################# 
    if(weightShelf>=quantity*weightOfOne+quantity*weightOfOne*0.05 or weightShelf<=quantity*weightOfOne+quantity*weightOfOne*0.05)
        somethingIsNotRight(id,1)
    else:
        somethingIsNotRight(id,0)
    ##################################################################################

hx_tab=[None]*7

hx_tab[1]=HX711(5, 6)
hx_tab[2]=HX711(13,19)
hx_tab[3]=HX711(, )
hx_tab[4]=HX711(,)
hx_tab[5]=HX711(, )
hx_tab[6]=HX711(,)


hx = HX711(5, 6)
hx1 = HX711(13,19)
##############Tu będzie potrzebna pętla do ustawienia formatu czytania #############################
hx.set_reading_format("LSB", "MSB")
hx1.set_reading_format("LSB", "MSB")
####################################################################################################

########################### PĘTLA DO JEDNOSTEK ODNIESIENIA #########################################
hx.set_reference_unit(20)
hx1.set_reference_unit(20)
####################################################################################################

###############################PĘTLA DO RESTARTU####################################################
hx.reset()
hx.tare()
hx1.reset()
hx1.tare()
####################################################################################################

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


        ########################### SPRAWDZIĆ CZY NUMERUJE OD 1 CZY OD 0 #################################    
        for i in range(len(valz)):
            valz[i]=hx_tab[i].get_weight(5)
            valz[i]=abs(valz[i])
        

        ########################## DO WYWALENIA #######################
        val = hx.get_weight(5)
        val=abs(val)
        prt = "1. " + str(val)
        print (prt)
        
        print("Debugging: ")
        print(val/lines[0].weight)
        print(val)
        print(lines[0].weight)
        
        x1=round(val/lines[0].weight)
        
        x1=int(x1)
        
        print("Simple bedubging:")
        print(x1)
        
        for i in range(len(lines)):
         ################################################################### 
        

        ################################### DO ZASTĄPIENIA WYWOŁANIAMI FUNKCJI PROCESS_DATA ###############################
        if x1>lines[0].quan:
            print("Sending up signal on line 1.")
            requests.get("http://intshelf.azurewebsites.net/api/up/1")
            ++w_1
        
        elif x1<lines[0].quan:
            print("Sending down signal on line 1.")
            requests.get("http://intshelf.azurewebsites.net/api/down/1")
            --w_1
        
        #####################################################################################################################
        

        ################################ DO WYWALENIA #######################################
        val = hx1.get_weight(5)
        prt = "2. " + str(val)
        print (prt)
        
        #####################################################################################
        
        ############ CO TU SIĘ DZIEJE???? ###########################
        hx.power_down()
        hx1.power_down()
        hx.power_up()
        hx1.power_up()
        
        for i_hx in hx_tab:
            i_hx.power_down()
            i_hx.power_up()
       ################################################################# 
        time.sleep(0.8)
            


        
        
        
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()


    






