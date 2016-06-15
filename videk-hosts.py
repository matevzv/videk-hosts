import json
import urllib2
from urllib2 import URLError
from itertools import groupby

try:
    nodes = urllib2.urlopen('http://localhost/api/nodes').read()
except URLError, e:
    print e.code
    exit()

munin = ""
with open("/home/matevz/test/munin.conf", "r") as munin_file:
    for line in munin_file:
        munin += line
        if "# automagicaly generated from here on" in line:
            break

munin += "\n"
nodes = json.loads(nodes)
nodes_list = []
for node in nodes:
    nodes_list.append((node['cluster'], node['name']))
    munin += "[" + node['cluster'] + ";" + node['name'] + "]\n"
    munin += "    address " + node['name'] + "\n\n"

hosts = "[local]\nlocalhost ansible_connection=local\n"
for key, group in groupby(nodes_list, lambda x: x[0]):
    listOfThings = "\n".join([thing[1] for thing in group])
    hosts += "\n[" + key + "]" + "\n" + listOfThings + "\n"
    munin += "[" + key + ";]\n"
    munin += "    contacts admin\n\n"

hosts += "\n"

with open("/home/matevz/test/hosts", "w") as hosts_file:
    hosts_file.write(hosts)

with open("/home/matevz/test/munin.conf", "w") as munin_file:
    munin_file.write(munin)
