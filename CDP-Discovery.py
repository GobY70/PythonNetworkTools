from netmiko import ConnectHandler
import getpass
from multiprocessing.dummy import Pool as ThreadPool

# Text FSM have to be installed and environment NET_TEXTFSM have to set correctly 
# see: "https://pynet.twb-tech.com/blog/automation/netmiko-textfsm.html"

def Get_cdp_entry(IP):
    try:
        neigborlist = []
        checklist.append(IP)
        ssh_session = ConnectHandler(device_type="cisco_ios",ip=IP,username=username,password=password)
        hostname = str(ssh_session.find_prompt())[:-1]
        print ("Now connected to: ",hostname)
        devicesuccess.append(IP)
        cdp_entry = ssh_session.send_command("show cdp entry *")   # get IP-adresses from Neighbors
        cdp_neighbors = ssh_session.send_command("show cdp neighbor ", use_textfsm=True) # get structured Data with TextFSM
        # Debug only: print (cdp_neighbors)
        filename = str(hostname+"_cdp.txt")
        for line in str(cdp_entry).split("\n"):
            if "IP address: " in line:
                IP = line.split()[-1]
                # Debuging only: print (IP)
                neigborlist.append(IP)
        neigbors = set(neigborlist)
        with open (filename,"w") as f:
            for neigbor in cdp_neighbors:
                neighbor_no_fwdn = str(neigbor["neighbor"].split(".")[0])
                f.write(hostname+" -- "+neigbor["local_interface"]+" -- "+neigbor["neighbor_interface"]+" -- "+neighbor_no_fwdn)
                # debug only: print (hostname+" -- "+neigbor["local_interface"]+" -- "+neigbor["neighbor_interface"]+" -- "+neigbor["neighbor"])
                f.write("\n")
        for neigbor in neigbors:
            devicelist.append(neigbor)
        return (neigbors)
    except Exception as e:
        print (e)
        return(None)
    
######################
# ==== Main Init === #
######################
devicelist = []       # Devices which was discovered by CDP
checklist = []        # Devices which tryed to check
devicesuccess = []    # Devices connected Successfully
Seeddevice = input("Seeddevice (IP-Adress) : ")
username = input ("Username to connect to devices : ")
password = getpass.getpass("Password : ")

# First-Device:
devicelist.append(Seeddevice)

First_run = Get_cdp_entry(Seeddevice)

mustcheck = set(set(devicelist) - set(checklist))

# ==== Create Treats and do SSH_Worker ==== #

while len(mustcheck) >=1:
    if len(mustcheck) <= 25 :
        num_threads=len(mustcheck)
    else:
        num_threads=25
    
    threads = ThreadPool( num_threads )
    results = threads.map( Get_cdp_entry, mustcheck)
    
    mustcheck = (set(devicelist) - set(checklist))
    print ("Devices that have to be checked: ",str(mustcheck))
    threads.close()
    threads.join()

# Write hosts.txt file with the connected Devices
with open ("hosts.txt","w") as f:
    print (devicesuccess)
    for host in set(devicesuccess):
        f.write(host+"\n")

