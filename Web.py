import streamlit as st
from netmiko import ConnectHandler
from dotenv import load_dotenv
import os
import pandas as pd
import re
from time import sleep

st.set_page_config(layout='wide')

def LoadGiports():
    load_dotenv()
    return os.getenv("giports")

st.session_state.setdefault("isConnected", False)
st.session_state.setdefault("statusData", pd.DataFrame())
st.session_state.setdefault("outputMsg", '')
st.session_state.setdefault("outputStatus", '')
st.session_state.setdefault("giports", LoadGiports())

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
            GetStatus()

def DisconnectFromSwitch():
    print("Disconnecting")
    st.session_state.net_connect.disconnect()
    st.session_state.isConnected = False

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
    global outputStatus 
    st.session_state.outputStatus = output
    StatusDisplay(st.session_state.outputStatus)
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
b1, b2, b3, b4= st.columns([1,1,2,1])

with b1:
    if st.session_state.isConnected == False:
        if st.button("Connect",use_container_width=True):
            ConnectToSwitch()
            st.toast("Connected")
            st.rerun()
                        
    elif st.session_state.isConnected == True:
        if st.button("Disconnect", use_container_width=True):
            DisconnectFromSwitch()
            st.session_state.outputMsg = ''
            st.toast("Disconnected")
            st.rerun()

with b2:
    if st.button("Write Config",use_container_width=True) and st.session_state.isConnected == True:
        WriteConfig()

with b3:
    global outputMsg
    #st.info requires replacing a single new line with "  \n" to actually render on a new line
    st.info("Command output:  \n" + st.session_state.outputMsg.replace("\n","  \n"))

with b4:
    if st.session_state.isConnected == True:
        st.success("Connected")
    elif st.session_state.isConnected == False:
        st.info("Not Connected")

if st.session_state.isConnected:
    
    with b1:
        task = st.radio("Task",
                    ["Vlan", "Trunk", "Name"],
                    horizontal=True, index = None)
    
    with b1:
        if task == "Name":
            portName = st.text_input(label="Name",max_chars=18)
    
    vlan = None
    if task == "Vlan":
        vlan = st.radio("VLAN",
                [1,2,3,4],
                horizontal=True)    

    port = st.radio('Switch Port', 
        [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48],
        horizontal=True, index= None)

st.divider()

try:
    st.text("Task: " + str(task) + "\nVLAN: " + str(vlan) + "\nPort: " + str(port))
except:
    print("Selections not loaded yet.")

#Resize buttons by fitting to columns
c1, c2, c3 = st.columns([1,1,3])

def RunCheck():
    return all((
        st.session_state.isConnected,
        task is not None,
        port is not None
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
      
        try:
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

            if vlan is not None and task == "Vlan":
                with st.spinner(text="Running.."):
                    VlanConfig()
                    st.toast("Done")
                    GetStatus()
        except:
            st.warning("Connection Issue.")
            DisconnectFromSwitch()
            st.session_state.outputMsg = ''
            st.toast("Disconnected")
        st.rerun()

with c2:
    if st.button("Get Status",use_container_width=True) and st.session_state.isConnected == True:
        with st.spinner(text="Running.."):
            GetStatus()
                       
st.dataframe(st.session_state.statusData, hide_index=True, use_container_width=True)

st.divider()

st.text("Raw Status Output:\n" + st.session_state.outputStatus)

# End of StreamLit Web interface
##################################