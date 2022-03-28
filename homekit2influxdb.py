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
import subprocess
import platform


# function ping test
def pingTest(pingHost):
	try:
		output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', pingHost), shell=True)#    except Exception as e:
	except Exception as e:
		return False
	return True


# debug enviroment variables
showraw = False
debug_str=os.getenv("DEBUG", None)
if debug_str is not None:
	debug = debug_str.lower() == "true"
else:
	debug = False

# getmac enviroment variables
getmac_str=os.getenv("GETMAC", None)
if getmac_str is not None:
	getmac = getmac_str.lower() == "true"
else:
	getmac = False


# HomeKit envionment variables
homekit_ip_list_str=os.getenv('HOMEKIT_IP_LIST', "")
homekit_host_list_str=os.getenv('HOMEKIT_HOST_LIST', "")
homekit_mac_list_str=os.getenv('HOMEKIT_MAC_LIST', "")
homekit_add_list_str=os.getenv('HOMEKIT_ADD_LIST', "")

homekit_ip_list=eval(homekit_ip_list_str)
homekit_host_list=eval(homekit_host_list_str)
homekit_mac_list=eval(homekit_mac_list_str)
homekit_add_list=eval(homekit_add_list_str)


# influxDBv2 envionment variables
influxdb2_host=os.getenv('INFLUXDB2_HOST', "localhost")
influxdb2_port=int(os.getenv('INFLUXDB2_PORT', "8086"))
influxdb2_org=os.getenv('INFLUXDB2_ORG', "Home")
influxdb2_token=os.getenv('INFLUXDB2_TOKEN', "token")
influxdb2_bucket=os.getenv('INFLUXDB2_BUCKET', "DEV")


# hard encoded envionment varables


# report debug/domac status
if debug:
	print ( " debug: TRUE" )
else:
	print ( " debug: FALSE" )

if getmac:
	print ( "getmac: TRUE" )
else:
	print ( "getmac: FALSE" )


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
	if getmac:
		mac = get_mac_address(ip=ipaddress)
	else:
		mac=homekit_mac_list[position]	
	if debug:
		print ("   MAC: "+mac)
       
	# get sensor values
	for sensor in [0,1]:
		value=ds['accessories'][1]['services'][sensor+1]['characteristics'][0]['value']
        	
		senddata["measurement"]=sensorList[sensor].lower()
#		senddata["time"]=time
		senddata["tags"]={}
		senddata["tags"]["source"]="HomeKit"
		senddata["tags"]["host"]=host
		senddata["tags"]["hardware"]=mac
		senddata["fields"]={}
		
		if sensorList[sensor] == "Temperature":
			value=float(round(value,1))
			senddata["fields"]["temp"]=value
		else:
			value=int(value)
			senddata["fields"]["percent"]=value
		
		if debug:
			print ("INFLUX: "+influxdb2_bucket)
			print (json.dumps(senddata,indent=4))
		write_api.write(bucket=influxdb2_bucket, org=influxdb2_org, record=[senddata])

	# do additional temperature sensors
	if homekit_add_list[position] != "":
		if debug:
			print ("ADD: "+homekit_add_list[position][0]+" - "+homekit_add_list[position][1])
		value=ds['accessories'][2]['services'][1]['characteristics'][0]['value']
		if homekit_add_list[position][1] == "Temperature":
			value=float(round(value,1))
		else:
			value=int(value)

		senddata={}
		senddata["measurement"]=homekit_add_list[position][1].lower()
		senddata["tags"]={}
		senddata["tags"]["source"]="docker homekit-influxdbv2"
		senddata["tags"]["origin"]="HomeKit"
		senddata["tags"]["host"]=homekit_add_list[position][0]
		senddata["tags"]["hardware"]=mac
		senddata["fields"]={}
		senddata["fields"]["temp"]=value
		if debug:
			print ("INFLUX: "+influxdb2_bucket)
			print (json.dumps(senddata,indent=4))
		write_api.write(bucket=influxdb2_bucket, org=influxdb2_org, record=[senddata])
	else:
		if debug:
			print ("ADD: NULL")
		
