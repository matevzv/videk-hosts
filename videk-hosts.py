import urllib2
import json
from itertools import groupby

nodes = urllib2.urlopen('http://localhost/api/nodes').read()

if "No nodes found" in nodes:
    print nodes
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


hosts = ""
for key, group in groupby(nodes_list, lambda x: x[0]):
    listOfThings = "\n".join([thing[1] for thing in group])
    hosts += "\n[" + key + "]" + "\n" + listOfThings + "\n"
    munin += "[" + key + ";]\n"
    munin += "    contacts admin\n\n"

hosts = hosts[1:]
hosts += "\n"

with open("/home/matevz/test/hosts", "w") as hosts_file:
    hosts_file.write(hosts)

with open("/home/matevz/test/munin.conf", "w") as munin_file:
    munin_file.write(munin)
