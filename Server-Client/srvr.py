
# coding: utf-8

# In[ ]:


#!/usr/bin/python
import MySQLdb
import threading
import Queue
import time
import socket
import datetime
import requests
exitFlag = 0


class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name

        
def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            date2,nr,val = data.split(",")
            hr,mn,sc=date2.split(":")
            print(date2)
            print(nr)
            print(val)
            date1=int(mn)*60+int(sc)+10
            a=datetime.datetime.now()
            date2=int(a.minute)*60+int(a.second)
            if(date1>date2):
                queueLock.release()
                updating(nr,val)
        else:
            queueLock.release()
        time.sleep(5)
def updating(id,waga):
        link='https://intshelf.azurewebsites.net/api/'
        if(int(waga)==1):
            link=link+'up/'+str(id)
            print (link)
            r=requests.get(link)
        else:
            link=link+'down/'+str(id)
            print (link)
            r=requests.get(link)
     
            
    
nameList = [2.5, 3.0]
queueLock = threading.Lock()
workQueue = Queue.Queue(10)
threads = []

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
host=s.getsockname()[0]
s.close()
s = socket.socket()
#host = '192.168.43.173' #ip of raspberry pi
port = 12345
s.bind((host, port))


queueLock = threading.Lock()
workQueue = Queue.Queue(10)
# Open database connection

# prepare a cursor object using cursor() method
cursor = db.cursor()
thread = myThread(1, "numero uno", workQueue)
thread.start()
threads.append(thread)
# Prepare SQL query to INSERT a record into the database.

s.listen(5)
while True:
    c, addr = s.accept()
    print ('Got connection from',addr)
    data = c.recv(1024)
    queueLock.acquire()
    workQueue.put(str(data.decode('utf-8')))
    queueLock.release()
    #plik = open('/home/michal/workspace/python/msg.txt','ab')
    #plik.write("\n%s" % (data.decode('utf-8')))
    #plik.close()
    #print ('Dane: ', data.decode('utf-8'))
c.close()

while not workQueue.empty():
   pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
# disconnect from server
db.close()


