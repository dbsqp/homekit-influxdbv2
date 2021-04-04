# homekit-influxdbv2
Fetch data from LAN HomeKit accessories via REST API and push to influxdb v2 bucket.

## HomeKit Accessories
- Get IP address of temperature/humidity sensors
- Create list of IPs: ['IP1','IP2', ...]
- Create list of rooms (mapped to hosts in Influx): ['Room1','Room2', ...]

## InfluxDBv2 Setup
Setup InfluxDBv2, create bucket and create a token with write permissions for bucket.

## Docker Setup
```
$ docker run -d \
 -e HOMEKIT_IP_LIST="['<IP1>','<IP2>',...]" \
 -e HOMEKIT_HOST_LIST="['<Room1>','<Room2>',...]" \
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
To report out MAC address in module tag enable getmac. Note docker container network needs to at host level:
```
-e GETMAC="TRUE" \
--network host
```

