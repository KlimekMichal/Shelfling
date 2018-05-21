import urllib2
contents = urllib2.urlopen("http://intshelf.azurewebsites.net/api/down/6").read()
print (contents)
values = contents.split('},')
for index,value in enumerate(values):
    value= value.translate(None, '}]')
    data = "Segment nr " +str(index+1) + " zawiera " + str(value.rpartition(':')[2]) + " puszek"
    #print (data)