# homekit-influxdbv2
Fetch data from the HomeKit REST API and place it in your influxdb.

## HomeKit Accessories
- Get IP address of temperature/humidity sensors
- Create list of IPs: ['10.0.0.1','10.0.0.2']
- Create list of rooms (mapped to hosts): ['Room #1','Room #2']

## InfluxDBv2 Setup
Setup InfluxDBv2, create bucket and create a token with write permissions for said bucket.

## Docker Setup
```
$ docker run -d \
 -e HOMEKIT_IP_LIST="['IP #1','IP #2']" \
 -e HOMEKIT_HOST_LIST="['Room #1','Room #2']" \
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
 -e DEBUG="true"
```
