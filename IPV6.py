##################################################################
#
# Author: gernot.eder@kapsch.net
# Date: Dez. 2018
# Used to enable IPv6 Router Adverdisement Guard on Catalyst Switches
#
###################################################################


from netmiko import Netmiko
from getpass import getpass
import re
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore

def create_list_from_file(filename):
    linelist = []
    try:
        with open(filename,"r") as file:
            filecontent=file.read()
            for line in filecontent.split("\n"):
                linelist.append(line)
        return (linelist)
    except Exception as e:
        print(Fore.RESET+e)
        return(None)


# IPv6 RA-Guard Configuration ""
GlobalCommand="ipv6 nd raguard policy RA-POLICY\ndevice-role host"
InterfaceCommand="ipv6 nd raguard attach-policy RA-POLICY"

# Ask for hosts-file, user and password 
hostsfile = input("Hosts Filename: ")
username = input("User to login to devices: ")
password = getpass("Password for User "+username+" :")

hostlist = create_list_from_file(hostsfile)

def get_access_interfaces(ssh_session):
    accessport="switchport mode access"
    interfacelist =[]
    interfaces=ssh_session.send_command("show interfaces status",use_textfsm=True)
    for p in interfaces:
        port = p["port"]
        # print (port)
        int_config = ssh_session.send_command("show run interface "+str(port))
        # print (int_config)
        if str(accessport) in str(int_config):
            interfacelist.append(port)
    # print (interfacelist)
    return interfacelist

def get_version(ssh_session):
    version=ssh_session.send_command("show version",use_textfsm=True)
    return (version)

def DeviceType_without_X(device_version):
    for ver in device_version:
        if len(ver["hardware"])==0:
            print (Fore.RESET+"No Hardwaretype found")
            return False
        hw = ver["hardware"][0]
        if "2960" in hw:
            if "X" in hw:
                #print ("2960 X or 2960 CX")
                return False
            if "S" in hw:
                #print ("2960 S")
                return True
            else :
                return True
        else:
            print ("not X")
            return True  

def check_sdm(ssh):
    hostname = ssh.find_prompt()[:-1]
    sdm = ssh.send_command("show sdm prefer")
    for sdm_line in sdm.split("\n"):
        if "The current template is" in sdm_line:
            current = re.findall(r'"(.*?)"', sdm_line)
            #print (Fore.RED+hostname +" : sdm pefer is set to : "+current[0]+Fore.RESET)
        if "On next reload" in sdm_line:
            next_reload = re.findall(r'"(.*?)"', sdm_line)
            if not next_reload:
                next_reload="Not Set"
            #print (Fore.RED+hostname + " : sdm pefer for next reload is set to : "+next_reload[0]+Fore.RESET)
        else:
            next_reload="Not Set"
    if "ipv6" in current[0]:
            return True
    if "ipv6" in next_reload[0]:
        #print (Fore.RED+"Reload Needet for Device "+hostname+Fore.RESET)
        return False
    if "Not set" in next_reload:
        #print (Fore.RED+"sdm must set and device reload needet on "+hostname+Fore.RESET)
        return False
    



def WORKER(IP):
    try: 
        error = False
        ssh = Netmiko(device_type="cisco_ios",ip=IP,username=username,password=password)
        hostname = ssh.find_prompt()[:-1]
        logfile = hostname+"_ipv6_cfg.txt"
        print (Fore.YELLOW+"Now connected to :",hostname+Fore.RESET)
        # Check Supported Software not supported in 15.0
        device_version=get_version(ssh)
       
        #for sw_ver in version:
        #    if sw_ver["version"][0:4] == "15.0":
        #        print ("Unsupported Software Version on "+hostname)
        #        break
        
        
        accessports = get_access_interfaces(ssh)               
        #print (hostname + "\n"+accessports)
        interfaceconfig=""
        for port in accessports:
            interface_cfg="interface "+str(port)+"\n"+InterfaceCommand
            interfaceconfig=interfaceconfig+interface_cfg+"\nexit\n"

       
        #
        # Check if sdm setup and/or reboot needet
        #
        if DeviceType_without_X(device_version):
            # print (hostname + " : Devicetype not X")
            if check_sdm(ssh):
                config=GlobalCommand+"\n"+interfaceconfig+"\n"
                print (Fore.GREEN+hostname+" : Send Config"+Fore.RESET)
            else:
                print (Fore.RED+hostname + " : Error on device: IPv6 not enabled in SDM"+Fore.RESET)
                config=""
        else:
            config=GlobalCommand+"\n"+interfaceconfig+"\n"
            print (Fore.GREEN+hostname+" : Send Config"+Fore.RESET)
            
        configuration=ssh.send_config_set(config)
        if "% Invalid input detected " in configuration:
            error = True
        f = open(logfile,"w")
        f.write(configuration)   
        write_mem=ssh.send_command("write mem")
        f.write(write_mem)
        f.close()
        if not error:
            print(Fore.RESET+hostname+" : Done")
        else:
            print(Fore.RED+hostname+" : Done with Error, see Logfile: "+logfile+Fore.RESET)
        ssh.disconnect()
    except Exception as e:
        print (e)
        return(None)

    
# ==== Create Treats and do Worker ==== #

if len(hostlist) <= 25 :
    num_threads=len(hostlist)
    #num_threads = 1  
else:
    num_threads=25

#num_threads=1  # only one thread
threads = ThreadPool( num_threads )
results = threads.map( WORKER, hostlist )

threads.close()
threads.join()
    












