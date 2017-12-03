#run with: sudo nohup python alt_recorder.py &

import csv
import logging
import sys
import time
import datetime
from Adafruit_BME280 import *
from Adafruit_BNO055 import BNO055

csv.register_dialect(
    'mydialect',
    delimiter = ',',
    quotechar = '"',
    doublequote = True,
    skipinitialspace = True,
    lineterminator = '\n',
    quoting = csv.QUOTE_MINIMAL
)

def csvHandler():
	with open('rocketData.csv', 'wb') as csvfile:
		print "CSV file rocketData.csv successfully made"
		database= csv.writer(csvfile, dialect='mydialect')
		header_bme = ['Time Since Start','Sensor Time','Temp (C)','Pressure (hPa)','Altitude (m)' ,'Humidity (%)']
		header_bno = ['BNO_temp','Euler_heading (deg)','Euler_roll (deg)','Euler_pitch (deg)','Quat_x',\
				'Quat_y','Quat_z', 'Quat_w','Mag_x (mT)', 'Mag_y (mT)', 'Mag_z (mT)', 'Gyro_x (deg/s)',\
				'Gyro_y (deg/s)','Gyro_z (deg/s)', 'totalAccel_x (m/s^2)','totalAccel_y (m/s^2)',\
				'totalAccel_z (m/s^2)', 'linAccel_x (m/s^2)', 'linAccel_y (m/s^2)',\
				'linAccel_z (m/s^2)', 'gravAccel_x (m/s^2)', 'gravAccel_y (m/s^2)',\
				'gravAccel_z (m/s^2)']
		database.writerow(header_bme+header_bno)
		csvfile.flush()
		print "File Header Made"
		print "** START RECORDING THE STOPWATCH NOW, RECORD ALL TIMES WITH POSITION "
		try:
			while(1):
				database.writerow(sensorHandler())
				csvfile.flush()
				time.sleep(0.1)
		except KeyboardInterrupt:
			print "Altitiude Recording Stoped"
	quit()

def getSecSinceReference():
	return (datetime.datetime.now()-referenceTime).total_seconds()

def bnoHandler():
	bnoData = []
	bnoDataTmp = []
	#temp (C)
	bnoData.append(bno.read_temp())
	#[heading,roll,pitch] (degrees)
	for i in bno.read_euler():
		bnoData.append("{0:0.2f}".format(i))
	#[x,y,z,w] ()
	bnoDataTmp = []
	bnoDataTmp += bno.read_quaternion()
	#[x,y,z] (micro-Teslas)
	bnoDataTmp += bno.read_magnetometer()
	#[x,y,z] (degrees per second)
	bnoDataTmp += bno.read_gyroscope()
	#[x,y,z] (m/s^2) 
	bnoDataTmp += bno.read_accelerometer()
	#[x,y,z] (m/s^2) (accel from movement, not gravity)
	bnoDataTmp += bno.read_linear_acceleration()
	#[x,y,z] (m/s^2) (accel from just gravity)
	bnoDataTmp += bno.read_gravity()
	for i in bnoDataTmp:
		bnoData.append(str(i))
	return bnoData

def bmeHandler():
	return ['{0:0.3f}'.format(bme.t_fine),\
		'{0:0.3f}'.format(bme.read_temperature()),\
		'{0:0.2f}'.format(bme.read_pressure()/100.0),\
		'{0:0.2f}'.format(bme.read_altitude()),\
		'{0:0.2f}'.format(bme.read_humidity())\
		]


def sensorHandler():
	sensorData = bmeHandler()+bnoHandler()
	return [getSecSinceReference()]+sensorData




bme = BME280(mode=BME280_OSAMPLE_8)
bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)

# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
	logging.basicConfig(level=logging.DEBUG)
while True:
	try:
		if not bno.begin():
			while not bno.begin() or bno.get_system_status()[0] == 0x01:
				pass
		break
	except:
		print "init error"
while(1):
	try:
		bno.set_calibration(bno.get_calibration())
		break
	except:
		print("Calibration error")
referenceTime = datetime.datetime.now()
csvHandler()
