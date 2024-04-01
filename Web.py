import streamlit as st
from netmiko import ConnectHandler
from dotenv import load_dotenv
import os
import pandas as pd
import re
from time import sleep

st.set_page_config(layout='wide')


if "isConnected" not in st.session_state:
    st.session_state.isConnected = False

if "statusData" not in st.session_state:
    st.session_state.statusData = pd.DataFrame()

if "outputMsg" not in st.session_state:
    st.session_state.outputMsg = ''

if "giports" not in st.session_state:
    load_dotenv()
    st.session_state.giports = os.getenv("giports")

if "teports" not in st.session_state:
    load_dotenv()
    st.session_state.teports = int(st.session_state.giports) + int(os.getenv("teports"))


#################################
# NetMiko / Switch interaction

def ConnectToSwitch():
    load_dotenv()
    cisco_3850 = {
    'device_type': 'cisco_ios',
    'host':   os.getenv("host"),
    'username': os.getenv("username"),
    'password': os.getenv("password"),
    'port' : 22
    } 
    if st.session_state.isConnected == False:
        print("Connecting")
        with st.spinner(text="Connecting.."):
            sleep(1)
            st.session_state.net_connect = ConnectHandler(**cisco_3850)
            st.session_state.isConnected = True
            st.success('Connected')
            GetStatus()

def PortName():
    if int(port) <= int(st.session_state.giports):
        return "interface Gi1/0/"+str(port)
    elif int(port) > int(st.session_state.giports):
        return "interface Te1/0/"+str(port)

def VlanConfig():
    print("Setting Vlan")
    vlanCommands = [PortName(),
                    'switchport mode access',
                    'switchport access vlan ' + str(vlan)]

    output = st.session_state.net_connect.send_config_set(vlanCommands)
    global outputMsg 
    st.session_state.outputMsg = output
    print(st.session_state.outputMsg)

def TrunkConfig():
    print("Setting Trunk")
    trunkCommands = [PortName(),
                     'switchport mode trunk']
    output = st.session_state.net_connect.send_config_set(trunkCommands)
    global outputMsg 
    st.session_state.outputMsg = output
    print(st.session_state.outputMsg)

def NameConfig():
    print("Setting Name")

    trunkCommands = [PortName(),
                     'description ' + portName]
    output = st.session_state.net_connect.send_config_set(trunkCommands)
    global outputMsg 
    st.session_state.outputMsg = output
    print(st.session_state.outputMsg)

def GetStatus():
    print("Getting Status")
    output = st.session_state.net_connect.send_command('show interface status')
    global outputMsg 
    st.session_state.outputMsg = output
    StatusDisplay(st.session_state.outputMsg)
    st.toast("Status Updated")

def WriteConfig():
    print("Writing Config")
    output = st.session_state.net_connect.send_command('wr')
    global outputMsg 
    st.session_state.outputMsg = output
    StatusDisplay(st.session_state.outputMsg)

# End of NetMiko / Switch interaction
#################################
# Pandas DataFrame and Status parsing
    
def StatusDisplay(rawData = ""):

    if rawData.startswith('\n'):
        rawData = rawData[1:] 

    lines = rawData.splitlines()

    #ChatGPT generated RegEx
    pattern = r'(\w+\d\/\d\/\d+)\s+(.+?)\s+(.+?)\s+(1|2|3|4|trunk)\s+(?:\w+\s)?(?:\w+\s)?' 
    
    processedData = []

    #[:49] to only show the primary 48 ports
    for line in lines[:49]:
        match = re.match(pattern, line)
        if match:
            processedData.append(match.groups())

    st.session_state.statusData = pd.DataFrame(processedData, 
                    columns=['Port', 'Name', 'Status', 'Vlan'])

# End of Pandas DataFrame and Status parsing
##################################
# StreamLit Web interface
    
#Resize buttons by fitting to columns
b1, b2, b3, b4, b5, b6, b7, b8, b9, b10 = st.columns(10)

with b1:
    if st.button("Connect",use_container_width=True):
        ConnectToSwitch()
        isConnected = True
with b2:
    if st.button("Write Config",use_container_width=True) and st.session_state.isConnected == True:
        WriteConfig()


portName = st.text_input(label="Name")

task = st.radio("Task",
                ["Vlan", "Trunk", "Name"],
                horizontal=True, index = None)
vlan = 'None'
if task == "Vlan":
    vlan = st.radio("VLAN",
            [1,2,3,4],
            horizontal=True)    
    
port = st.radio('Switch Port', 
    [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48],
    horizontal=True, index= None)

st.text("Task: " +str(task) + "\nVLAN: " + str(vlan) + "\nPort: " + str(port))

#Resize buttons by fitting to columns
c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(10)

def RunCheck():
    return all((
        st.session_state.isConnected,
        task != None,
        port != None
    ))

def SafetyCheck():
    value = st.session_state.statusData.at[port-1, "Name"]
    if value == "Router" and task != "Name":
        st.warning(f"That port is named {value}. If you really want to modify it, change its name temporarily.")
        print("Blocked config of " + value)
        return False
    else:
        return True

with c1:    
    if st.button("Run",use_container_width=True) and RunCheck() and SafetyCheck():

        if task == "Trunk":
            with st.spinner(text="Running.."):
                TrunkConfig()
                st.toast("Done")
                GetStatus()

        if task == "Name":
            with st.spinner(text="Running.."):
                NameConfig()
                st.toast("Done")
                GetStatus()

        if vlan != None and task == "Vlan":
            with st.spinner(text="Running.."):
                VlanConfig()
                st.toast("Done")
                GetStatus()

with c2:
    if st.button("Get Status",use_container_width=True) and st.session_state.isConnected == True:
        with st.spinner(text="Running.."):
            GetStatus()
                

st.dataframe(st.session_state.statusData, hide_index=True, use_container_width=True)

st.text("Switch Output:\n" + st.session_state.outputMsg)

# End of StreamLit Web interface
##################################