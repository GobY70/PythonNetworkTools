from netmiko import ConnectHandler
import getpass
from multiprocessing.dummy import Pool as ThreadPool
from time import time


#username = "cisco"
#password = "Cisco123"
#IP = "192.168.148.133"

def Get_cdp_entry(IP):
    try:
        neigborlist = []
        ssh_session = ConnectHandler(device_type="cisco_ios",ip=IP,username=username,password=password)
        hostname = str(ssh_session.find_prompt())[:-1]
        cdp_entry = ssh_session.send_command("show cdp entry *")
        filename = str(hostname+"cdp.txt")
        for line in str(cdp_entry).split("\n"):
            if "IP address: " in line:
                IP = line.split()[-1]
                print (IP)
                neigborlist.append(IP)
        neigbors = set(neigborlist)
        return (neigbors)
    except Exception as e:
        print (e)
        return(None)
    

# ==== Main Init === #
######################
devicelist = []
checklist = []
Seeddevice = input("Seeddevice : ")
username = input ("Username to connect to devices : ")
password = getpass.getpass("Password : ")

# First-Device:
devicelist.append(Seeddevice)
checklist.append(Seeddevice)

First_run = Get_cdp_entry(Seeddevice)
for Device in First_run:
    devicelist.append(Device)
 


# ==== Create Treats and do SSH_Worker ==== #

if len(hostlist) <= 25 :
    num_threads=len(hostlist)
else:
    num_threads=25

#num_threads=1  # only one thread
threads = ThreadPool( num_threads )
results = threads.map( get_wktools_output, hostlist )

threads.close()
threads.join()