import socket
import datetime
import time

now = datetime.datetime.now()
s = socket.socket()
host = '192.168.1.28' #ip of raspberry pi
port = 12345
s.bind((host, port))


s.listen(5)
while True:
  c, addr = s.accept()
  print ('Got connection from',addr)
  data = c.recv(1024)
  plik = open('/home/michal/workspace/python/msg.txt','ab')
  plik.write("\n%s" % (data.decode('utf-8')))
  plik.close()
  #print ('Dane: ', data.decode('utf-8'))
  c.close()
