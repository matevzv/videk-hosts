import re
import time
import json
import requests
from datetime import datetime

videk = 'http://localhost:3000/'

try:
    nodes = requests.get(videk + 'api/nodes')
except:
    exit()

munin = ""
with open("/etc/munin/munin.conf", "r") as munin_file:
    for line in munin_file:
        munin += line
        if "# automagicaly generated from here on" in line:
            break

munin += "\n"
clusters = {}
nodes = nodes.json()
valid_nodes = []
for node in nodes:
    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', \
        node['name'].replace("-", "."))

    if ip:
        ip = ip[0]
        
        if node['cluster'] in clusters:
            clusters[node['cluster']].append(node['name'])
        else:
            clusters[node['cluster']] = [node['name']]

        munin += "[" + node['cluster'] + ";" + node['name'] + "]\n"
        munin += "    address " + ip[0] + "\n\n"

        valid_nodes.append(node)

    elif "ebottle" in node['cluster']:
        ts = int(time.time()) - 30*60
        ts = datetime.fromtimestamp(ts).isoformat()
        url = videk + "api/measurements?node_id=" + node["_id"] + "&from=" + ts
        measurements = requests.get(url).json()

        if "No measurements" in measurements:
            requests.put(videk + "api/nodes/" + str(node["_id"]), data={"status":"inactive"})
        else:
            requests.put(videk + "api/nodes/" + str(node["_id"]), data={"status":"active"})

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
