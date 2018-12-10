from netmiko import ConnectHandler
import getpass
import re
from multiprocessing.dummy import Pool as ThreadPool
from time import time

#username = "cisco"
#password = "Cisco123"
#IP = "192.168.148.133"

Configure_Commands=["interface eth 0/0\nno cdp enable\n" ]


def check_newdevice (known,new):
    reallynew=[]
    for item in new:
        if not item in known:
            reallynew.append(item)
    return(reallynew)


def create_list_from_file(filename):
    linelist = []
    try:
        with open(filename,"r") as file:
            filecontent=file.read()
            for line in filecontent.split("\n"):
                linelist.append(line)
        return (linelist)
    except Exception as e:
        print(e)
        return(None)


def get_wktools_output(IP):
    try:
        ssh_session = ConnectHandler(device_type="cisco_ios",ip=IP,username=username,password=password)
        hostname = str(ssh_session.find_prompt())[:-1]+"_config.txt"
        with open (hostname,"w") as outputfile:
            for command in Configure_Commands:
                outputfile.write(command)
                outputfile.write("\n")
                commandoutput = ssh_session.send_config_set(command)
                outputfile.write(commandoutput)
        ssh_session.send_command("wr mem")
        return(True)
    except Exception as e:
        print (e)
        return(None)

# === Main Program ===#

# ==== Main Init === #
######################
devicelist = []
hostlist = []
filename = input("IP-Host-File : ")
username = input ("Username to connect to devices : ")
password = getpass.getpass("Password : ")

hostlist = create_list_from_file(filename)


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