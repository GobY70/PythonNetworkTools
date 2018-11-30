
# Virtualenvireonment aus :/mnt/d/Python/virtenv/ve_netmiko 
# cd /mnt/d/Python/virtenv/ve_netmiko 
# source bin/activate

from tcpping import tcpping 
from netmiko import ConnectHandler
import ipaddress
from time import time
import getpass
from multiprocessing.dummy import Pool as ThreadPool


def check_ip_network(ip_net):
    try:
        ipaddress.IPv4Network(ip_net)

        return (True)
    except:
        return (False)

def worker_ssh_test(IP):
    if tcpping(str(IP),23,2):
        reachable.append(str(IP))


def worker_get_devicesinfo(IP):
    hostip=IP
    try :
        ssh_session = ConnectHandler(device_type="cisco_ios_telnet",ip=hostip,username=user,password=pwd)
        sh_ver = ssh_session.send_command("show version")
        hostname = ssh_session.find_prompt()
        if "LINUXL2" in sh_ver:
            hosttype = "Switch"
        elif "linux-l3" in sh_ver:
            hosttype = "Router"
        else:
            hosttype = "Other"
        my_inventory.append({"hostname":hostname,"ip":IP,"hosttype":hosttype})
        ssh_session.disconnect()
        return (None)
    except Exception as e:
        print ( IP, " Failed: ", e)    
        return (None)




#==============================================================================
# ---- Main: Create Inventory
#==============================================================================

# Initialize Gobal Vars
reachable=[]
ip_net="300.300.300.300/22"
num_threads = 75
my_inventory=[]

while not check_ip_network(ip_net):
    ip_net = input("Enter Discovery Network, like 192.168.1.0/24: ")

user = input("Enter Username : ")
pwd = getpass.getpass("Enter Password : " )

print ("-"*40)
hosts = list(ipaddress.IPv4Network(ip_net).hosts())

#----
#---- Try TCP-SYN on Ip Network
#---- 

starttime=time()
starttime1=time()

print ('\n--- Creating threadpool with ',num_threads,' threads: Try TCP-SYN on Port 23 ---\n')
threads = ThreadPool( num_threads )
results = threads.map( worker_ssh_test, hosts )

threads.close()
threads.join()

print ("--- Finished TCP-SYN on ",len(hosts)," Hosts in ",time()-starttime,"\n")
print ("--- Detected ",len(reachable)," Hosts with open TCP-Port 23\n")
print ("-"*40)
# debug only print ("Reachable Hosts: ",reachable)

#----
#---- Get Host INfos 
#----

num_threads = 25
if num_threads >= len(reachable):
    num_threads = len(reachable)

starttime=time()

print ('\n--- Creating threadpool with ',num_threads,' threads: Try get Hostinfos  on  ',len(reachable),' Hosts ---\n\n')
threads = ThreadPool( num_threads )
results = threads.map( worker_get_devicesinfo, reachable )

threads.close()
threads.join()

print ("\n---Finished get Hostinfos  in ",time()-starttime)," ---\n"
print ("-"*40)
# print (my_inventory)

#----
#----  Writing Inventory File for Nornir
#----

print ("\n--- writing Inventory File ---")
with open("hosts.txt",mode="w") as myfile:
    # myfile.write("---\n")
    for device in my_inventory:
        # hostname = device.get("hostname")[:-1]
        # myfile.write(hostname)
        # myfile.write(":\n    nornir_host: ")
        dev_ip = device.get("ip")
        myfile.write(dev_ip)
        myfile.write("\n")
        # myfile.write(" \n    nornir_username: ")
        # myfile.write(user)
        # myfile.write("\n    nornir_password: ")
        # myfile.write(pwd)
        # myfile.write("\n")
        #myfile.write("    nornir_ssh_port: 22\n")
        #myfile.write("    nornir_nos: cisco_ios\n")
        #if device.get("hosttype") == "Switch":
        #    myfile.write("    groups:\n")
        #    myfile.write("        - Switch\n")
        #elif device.get("hosttype") == "Router":
        #    myfile.write("    groups:\n")
        #    myfile.write("        - Router\n")
        # myfile.write("\n")


print ("\n---- Finished creating hosts.txt for use with ITG-Python-Scripts in ", starttime1-time() ,"----\n")
print ("-"*40)

