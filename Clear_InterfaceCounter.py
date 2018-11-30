from netmiko import ConnectHandler
from tcpping import tcpping
import getpass
import re
from multiprocessing.dummy import Pool as ThreadPool
from time import time





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
        hostname = str(ssh_session.find_prompt())[:-1]
        filename = hostname + "_run.txt"
        output1 = ssh_session.send_command("clear counters",expect_string="\[confirm\]")
        output2 = ssh_session.send_command("\n",expect_string="#")
        print (output1)
        print (output2)
        #with open (filename,"w") as outputfile:
        #+    for command in wktools_commands:
        #        outputfile.write(command)
        #        outputfile.write("\n")
        #        commandoutput = ssh_session.send_command(command)
        #       outputfile.write(commandoutput) 
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
