import requests

nodes = requests.get('http://localhost/api/nodes')

if "No nodes found" in nodes.text:
    print nodes.text
    exit()

munin = ""
with open("/etc/munin/munin.conf", "r") as munin_file:
    for line in munin_file:
        munin += line
        if "# automagicaly generated from here on" in line:
            break

munin += "\n"
hosts = ""
for node in nodes.json():
    hosts += "[" + node['cluster'] + "]\n"
    munin += "[" + node['cluster'] + "]\n"
    hosts += node['name'] + "\n\n"
    munin += "    address " + node['name'] + "\n"
    munin += "    contacts admin\n\n"

with open("/etc/ansible/hosts", "w") as hosts_file:
    hosts_file.write(hosts)

with open("/etc/munin/munin.conf", "w") as munin_file:
    munin_file.write(munin)
