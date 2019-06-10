#!/usr/bin/env python

import minimalmodbus
import socket
import serial
import paho.mqtt.client as paho
import time
import simplejson as json
from datetime import datetime
from influxdb import InfluxDBClient

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 0.2
instrument.mode = minimalmodbus.MODE_RTU



dbname = 'powerwall'
dbuser = 'admin'
influxdb_client = None

influx_host="localhost"
influx_port=8086
broker="192.168.1.30"

def _intToBin(toConvert):
    #Here you convert the int value to binary, after that to string getting from index 2 to 10
    MSByte = str(bin(toConvert))[2:10]
    #Here you convert the int value to binary, after that to string getting from index 10 to 18
    LSByte = str(bin(toConvert))[10:18]
    final = MSByte+LSByte
    return final

while True:
	try:
            voltage = instrument.read_register(4097-1, numberOfDecimals=2, functioncode=4, signed=False)
            print("Voltage: " + str(voltage) + "V")
            currentpack = instrument.read_register(4098-1, numberOfDecimals=2, functioncode=4, signed=True)
            print("Current of pack: " + str(currentpack) + "A")
            capacity = instrument.read_register(4099-1, numberOfDecimals=2, functioncode=4, signed=False)
            print("Capacity: " + str(capacity) + "AH")
            avgtempcell = instrument.read_register(4100-1, numberOfDecimals=1, functioncode=4, signed=True)
            print("Avg cell temp: " + str(avgtempcell) + "C")
            avgtempenv = instrument.read_register(4101-1, numberOfDecimals=1, functioncode=4, signed=True)
            print("Avg env temp: " + str(avgtempenv) + "C")
            soc = instrument.read_register(4105-1, numberOfDecimals=1, functioncode=4, signed=False)
            print("SOC: " + str(soc) + "%")
            soh = instrument.read_register(4106-1, numberOfDecimals=1, functioncode=4, signed=False)
            print("SOH: " + str(soh) + "%")
            fullcharge = instrument.read_register(4107-1, numberOfDecimals=2, functioncode=4, signed=False)
            print("Full charge: " + str(fullcharge) + "AH")
            cycle = instrument.read_register(4108-1, numberOfDecimals=0, functioncode=4, signed=False)
            print("Cycle count: " + str(cycle) + "#")
            warn = _intToBin(instrument.read_register(4102-1, numberOfDecimals=0, functioncode=4, signed=False))
            print("Warn: " + str(warn) + "bit")
            protect = _intToBin(instrument.read_register(4103-1, numberOfDecimals=0, functioncode=4, signed=False))
            print("Protect: " + str(protect) + "bit")
            status = _intToBin(instrument.read_register(4104-1, numberOfDecimals=0, functioncode=4, signed=False))
            print("Status: " + str(status) + "bit")

            json_body = [
                {
                    "measurement": "battery",
                    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "voltage": voltage,
                        "currentpack": currentpack,
                        "capacity": capacity,
                        "avgtempcell": avgtempcell,
                        "avgtempenv": avgtempenv,
                        "soc": soc,
                        "soh": soh,
                        "fullcharge": fullcharge,
                        "cycle": cycle,
                        "warn": warn,
                        "protect": protect,
                        "status": status
                      }
                }
            ]
            # MQTT
	    print("Preparing MQTT")
            client= paho.Client("victorpi")
            client.connect(broker)
            client.loop_start()
            time.sleep(2)
            client.publish("victpower/", json.dumps(json_body[0]['fields']))
            client.loop_stop()
            #Influxdb
	    print("Preparing influxdb")
	    influxdb_client = InfluxDBClient(host=influx_host, port=influx_port)
    	    influxdb_client.switch_database(database=dbname)
            response = influxdb_client.write_points(points=json_body)
            print "write_operation response", response
            # Get some sleep for the next reading
            time.sleep(120)

	except Exception, e:
		print(str(e))
