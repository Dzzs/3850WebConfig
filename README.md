# 3850WebConfig

This tool allows you to effortlessly control your 3850 switch configuration directly from a web browser. 

Key features include:
Modify Switchport Settings: Easily change switchport names (descriptions), assign VLANs, and configure trunk status.
Comprehensive Port View: Get a status overview of all 48 ports.
Direct Configuration Updates: Write and apply configuration changes instantly.

Important:
Before clicking 'Run', thoroughly review the information above the button. Incorrect changes can disrupt network connectivity.

### Prerequisite
The machine running the container must have password-based SSH access to your switch.

## Docker Compose
Tested on AMD64 and ARM64 (Raspberry Pi 4).
```
services:
  3850webconfig:
    image: ghcr.io/dzzs/3850webconfig:main
    container_name: 3850webconfig
    environment:
      - host=192.168.1.1 #Enter switch's IP
      - username=SSHUsername #Username used to SSH into the switch
      - password=SSHPassword #Password used to SSH into the switch
      - giports=36 #Number of GI ports
      - PYTHONUNBUFFERED=1 #Optional for some logging to docker console
    ports:
      - 8080:8501  
    restart: unless-stopped
```

## Usage
- Click the 'Connect' button.
- Select the appropriate 'Task' option.
- Complete any required fields or, if you are changing a name, enter the new name.
- Status updates with most actions, but you can click 'Get Status' any time to update the information table as well.

### Landing Page
![image](https://github.com/Dzzs/3850WebConfig/assets/11656216/64253cb2-8261-4a43-90f7-4edb74726553)

### In Use
![image](https://github.com/Dzzs/3850WebConfig/assets/11656216/905c3f99-515e-4572-9c50-696cbb55b538)

# Disclaimer
While this tool is designed to be helpful, I cannot be held responsible for any network issues that may arise from its use. Please use it with caution and understand that it is not intended for production environments.
