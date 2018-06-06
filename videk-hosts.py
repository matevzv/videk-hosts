import re
import json
import urllib2
from urllib2 import URLError

try:
    nodes = urllib2.urlopen('http://localhost:3000/api/nodes')
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
clusters = {}
nodes = json.load(nodes)
valid_nodes = []
for node in nodes:
    try:
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', \
            node['name'].replace("-", "."))[0]

        if node['cluster'] in clusters:
            clusters[node['cluster']].append(node['name'])
        else:
            clusters[node['cluster']] = [node['name']]

        munin += "[" + node['cluster'] + ";" + node['name'] + "]\n"
        munin += "    address " + ip + "\n\n"

        valid_nodes.append(node)
    except:
        pass

nodes = valid_nodes

hosts = "[local]\nlocalhost ansible_connection=local\n"
for cluster, nodes in clusters.items():
    hosts += "\n[" + cluster + "]" + "\n"
    munin += "[" + cluster + ";]\n"
    munin += "    contacts admin\n\n"

    for node in nodes:
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', node.replace("-", "."))[0]
        hosts += ip + "\n"

with open("/etc/ansible/hosts", "w") as hosts_file:
    hosts_file.write(hosts)

with open("/etc/munin/munin.conf", "w") as munin_file:
    munin_file.write(munin[:-1])
