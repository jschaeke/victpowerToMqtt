#!/usr/bin/env python

import minimalmodbus
import socket
import serial
import paho.mqtt.client as paho
import time

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 0.2
instrument.mode = minimalmodbus.MODE_RTU

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


        	client= paho.Client("victorpi")
        	client.connect(broker)
        	client.loop_start()
        	time.sleep(2)
        	client.publish("victpower/",
			'{"voltage":' + str(voltage) +
			',"currentpack":' + str(currentpack) +
			',"capacity":' + str(capacity) +
                	',"avgtempcell":' + str(avgtempcell) +
                	',"avgtempenv":' + str(avgtempenv) +
                	',"soc":' + str(soc) +
                	',"soh":' + str(soh) +
                	',"fullcharge":' + str(fullcharge) +
                	',"cycle":' + str(cycle) +
                	',"warn":' + str(warn) +
                	',"protect":' + str(protect) +
                	',"status":' + str(status) +
			'}')
        	client.loop_stop()
		time.sleep(120)

	except Exception, e:
		print(str(e));
