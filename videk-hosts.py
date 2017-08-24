import re
import json
import urllib2
from urllib2 import URLError
from itertools import groupby

try:
    nodes = urllib2.urlopen('http://localhost:3000/api/nodes').read()
except URLError, e:
    print e.code
    exit()

munin = ""
with open("/etc/munin/munin.conf", "r") as munin_file:
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
    munin += "    address " + \
        node['name'].replace("sna-lgtc-", "").replace("-", ".") + "\n\n"

hosts = "[local]\nlocalhost ansible_connection=local\n"
for key, group in groupby(nodes_list, lambda x: x[0]):
    listOfThings = "\n".join([re.findall( r'[0-9]+(?:\.[0-9]+){3}', \
        thing[1].replace("-", "."))[0] for thing in group])
    hosts += "\n[" + key + "]" + "\n" + listOfThings + "\n"
    munin += "[" + key + ";]\n"
    munin += "    contacts admin\n\n"

hosts += "\n"

with open("/etc/ansible/hosts", "w") as hosts_file:
    hosts_file.write(hosts)

with open("/etc/munin/munin.conf", "w") as munin_file:
    munin_file.write(munin)
