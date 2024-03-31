import streamlit as st
from netmiko import ConnectHandler
from dotenv import load_dotenv
import os
import pandas as pd
import re

st.set_page_config(layout='wide')

if "isConnected" not in st.session_state:
    st.session_state.isConnected = False

if "statusData" not in st.session_state:
    st.session_state.statusData = pd.DataFrame()

if "outputMsg" not in st.session_state:
    st.session_state.outputMsg = ''

def ConnectToSwitch():
    print("Connecting")
    load_dotenv()
    cisco_3850 = {
    'device_type': 'cisco_ios',
    'host':   os.getenv("host"),
    'username': os.getenv("username"),
    'password': os.getenv("password"),
    'port' : 22
    } 
    st.session_state.isConnected = True
    st.session_state.net_connect = ConnectHandler(**cisco_3850)    

def VlanConfig():

    if int(port) <= 36:
        interface = "interface Gi1/0/"+str(port)
    elif int(port) >= 37:
        interface = "interface Te1/0/"+str(port)

    vlanCommands = [interface,
                    'switchport mode access',
                    'switchport access vlan ' + str(vlan)]

    output = st.session_state.net_connect.send_config_set(vlanCommands)
    global outputMsg 
    st.session_state.outputMsg = output

def TrunkConfig(port = int):

    if int(port) <= 36:
        interface = "interface Gi1/0/"+str(port)
    elif int(port) >= 37:
        interface = "interface Te1/0/"+str(port)

    trunkCommands = [interface,
                     'switchport mode trunk']

    output = st.session_state.net_connect.send_config_set(trunkCommands)
    global outputMsg 
    st.session_state.outputMsg = output

def NameConfig():

    if int(port) <= 36:
        interface = "interface Gi1/0/"+str(port)
    elif int(port) >= 37:
        interface = "interface Te1/0/"+str(port)

    trunkCommands = [interface,
                     'description ' + portName]
    output = st.session_state.net_connect.send_config_set(trunkCommands)
    global outputMsg 
    st.session_state.outputMsg = output

def GetStatus():
    print("Getting Status")
    output = st.session_state.net_connect.send_command('show interface status')
    global outputMsg 
    st.session_state.outputMsg = output
    StatusDisplay(st.session_state.outputMsg)

#################################

@st.cache_data
def StatusDisplay(rawData = ""):

    if rawData.startswith('\n'):
        rawData = rawData[1:] 

    lines = rawData.splitlines()

    pattern = r'(\w+\d\/\d\/\d+)\s+(.+?)\s+(.+?)\s+(1|2|3|4|trunk)\s+(?:\w+\s)?(?:\w+\s)?' 
    
    processedData = []

    for line in lines[:49]:
        match = re.match(pattern, line)
        if match:
            processedData.append(match.groups())
        #else:  # Line doesn't match
            #print("Non-matching line:", line)

    st.session_state.statusData = pd.DataFrame(processedData, 
                    columns=['Port', 'Name', 'Status', 'Vlan'])

##################################

if st.button("Connect"):
    ConnectToSwitch()
    isConnected = True

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


c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(10)

with c1:    
    if st.button("Run",use_container_width=True):
        if task is not None:
            if port is not None:
                if task == "Trunk":
                    TrunkConfig()
                if task == "Name":
                    NameConfig()
                if vlan is not None:
                    VlanConfig()

with c2:
    if st.button("Get Status",use_container_width=True):
        if st.session_state.isConnected == True:
            GetStatus()

st.dataframe(st.session_state.statusData, hide_index=True, use_container_width=True)
#st.text(st.session_state.outputMsg)
