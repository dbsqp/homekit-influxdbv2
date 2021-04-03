#!/usr/bin/python3
# encoding=utf-8

from pytz import timezone
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import os
import sys
import requests
from getmac import get_mac_address
import subprocess, platform


# function ping test
def pingTest(pingHost):
    try:
        output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', pingHost), shell=True)#    except Exception as e:
    except Exception as e:
	    return False
    return True


# debug enviroment variables
domac = True
showraw = False
debug_str=os.getenv("DEBUG", None)
if debug_str is not None:
  debug = debug_str.lower() == "true"
else:
  debug = False


# HomeKit envionment variables
homekit_ip_list=os.getenv('HOMEKIT_IP_LIST', "")
homekit_host_list=os.getenv('HOMEKIT_HOST_LIST', "")


# influxDBv2 envionment variables
influxdb2_host=os.getenv('INFLUXDB2_HOST', "localhost")
influxdb2_port=int(os.getenv('INFLUXDB2_PORT', "8086"))
influxdb2_org=os.getenv('INFLUXDB2_ORG', "org")
influxdb2_token=os.getenv('INFLUXDB2_TOKEN', "token")
influxdb2_bucket=os.getenv('INFLUXDB2_BUCKET', "Developement")


# hard encoded envionment varables


# report debug status
if debug:
    print ( " debug: TRUE" )
else:
    print ( " debug: FALSE" )


# influxDBv2
influxdb2_url="http://" + influxdb2_host + ":" + str(influxdb2_port)
if debug:
    print ( "influx: "+influxdb2_url )
    print ( "bucket: "+influxdb2_bucket )

client = InfluxDBClient(url=influxdb2_url, token=influxdb2_token, org=influxdb2_org)
write_api = client.write_api(write_options=SYNCHRONOUS)


# fixed sensors
sensorList=['Temperature','Humidity']


# pass data to InfluxDB
for ipaddress in homekit_ip_list:
    senddata={}

    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ") 

    # get host name
    position = homekit_ip_list.index(ipaddress)
    host=homekit_host_list[position]
    if debug:
        print ("\nSensor: "+host+" - "+ipaddress)

    # test if host responde to ping
    if pingTest(ipaddress):
        if debug:
            print ("  PING: OK")
    else:
        if debug:
            print ("  PING: NOK")
        continue

    # get REST API
    url="http://"+ipaddress+":5556/"
    try:
        raw = requests.get(url, timeout=4)
    except requests.exceptions.Timeout as e: 
        if debug:
            print ("   API:",e)
        continue

    if raw.status_code == requests.codes.ok:
        if debug:
            print ("   API: OK ["+str(raw.status_code)+"]")
        ds = raw.json()
        if debug and showraw:
            print ("   RAW:")
            print (json.dumps(ds,indent=4))
    else:
        if debug:
            print ("   API: NOK")
        continue

    # get MAC
    if domac:
        mac = get_mac_address(ip=ipaddress)
        if debug:
            print ("   MAC: "+mac)
       
    # get sendor values
    for sensor in [0,1]:
        value=ds['accessories'][1]['services'][sensor+1]['characteristics'][0]['value']

        if sensorList[sensor] == "Temperature":
        	value=float(round(value,1))
        else:
        	value=int(value)
        	
        senddata["measurement"]=sensorList[sensor]
#        senddata["time"]=time
        senddata["tags"]={}
        senddata["tags"]["source"]="HomeKit"
        senddata["tags"]["host"]=host
        if domac:
            senddata["tags"]["module"]=mac
        senddata["fields"]={}
        senddata["fields"]["value"]=value
        if debug:
            print ("INFLUX: "+influxdb2_bucket)
            print (json.dumps(senddata,indent=4))
        write_api.write(bucket=influxdb2_bucket, org=influxdb2_org, record=[senddata])