# homekit-influxdbv2
Fetch data from LAN HomeKit accessories via REST API and push to influxdb v2 bucket.

## HomeKit Accessories
- Get IP address of temperature/humidity sensors
- Create list of IPs: ['IP1','IP2', ...]
- Create list of rooms (mapped to hosts in Influx): ['Room1','Room2', ...]
- Create list of mac addresses (mapped to hardware in Influx): ['MAC1','MAC2', ...] (optional)


## InfluxDBv2 Setup
Setup InfluxDBv2, create bucket and create a token with write permissions for bucket.

## Docker Setup
```
$ docker run -d \
 -e HOMEKIT_IP_LIST="['<IP1>','<IP2>',...]" \
 -e HOMEKIT_HOST_LIST="['<Room1>','<Room2>',...]" \
 -e HOMEKIT_MAC_LIST="['<MAC1>','<MAC2>',...]" \
 -e INFLUXDB2_HOST="<INFLUXDBv2 SERVER>" \
 -e INFLUXDB2_PORT="8086" \
 -e INFLUXDB2_ORG="Home" \
 -e INFLUXDB2_TOKEN="" \
 -e INFLUXDB2_BUCKET="Staging" \
 --name "HomeKit-InfluxDBv2" \
dbsqp/homekit-influxdbv2:latest
```

## Debug
To report out further details in the log enable debug:
```
 -e DEBUG="TRUE"
```

## Get MAC
To read MAC address via ARP enable getmac. Not possible if docker and devices are on different subnets. Use HOMEKIT_MAC_LIST for manual override. Note docker container network needs to at host level:
```
-e GETMAC="TRUE" \
--network host
```

