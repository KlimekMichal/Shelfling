import socket
import datetime
import time
               
now = datetime.datetime.now()
s = socket.socket()        
host = '192.168.1.28'# ip of raspberry pi 
port = 12345               
s.connect((host, port))
message = "%i dzien %i : %i : %i" % (now.day, now.hour, now.minute, now.second)
msg = "111111111111"
s.sendto(message.encode('utf-8'),(host,port))
s.close()