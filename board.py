"""
Copyright (C) 2016  Sota Kaneko

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import RPi.GPIO as GPIO
from time import sleep , time
from sys import exit
from threading import Thread

""" --- init --- """
shutd = 0
danger = 0
safe_distance = 15  #Max value is about 70 cm
speed_of_sound = 17150 #At 1 BAR = 17150


#GPIO PIN NUMBERS
acc = 23
acc_led = 18
safemode_toggle = 25
default_led = 4
safemode_led = 22
hibernate_toggle = 17

#GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(acc , GPIO.IN , pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(safemode_toggle , GPIO.IN , pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(hibernate_toggle , GPIO.IN , pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(acc_led , GPIO.OUT)
GPIO.setup(default_led , GPIO.OUT)
GPIO.setup(safemode_led , GPIO.OUT)

""" --- Functions --- """

def forward():
	GPIO.output(acc_led , 1)
	return

def stop():
	GPIO.output(acc_led , 0)
	return

def shutdown():
	global shutd ; shutd = 1
	print "\n\nShutting down...."
	GPIO.cleanup()
	exit()

def hibernate(ty):
	global danger ; danger = 1
	print "\n\nParking Brakes Engaged"
	stop()

	if ty == 0:
		GPIO.output(default_led , 0)
		sleep(0.1)
		GPIO.output(default_led , 1)
		sleep(1)
		GPIO.output(safemode_led , 1)
	elif ty == 2:
		GPIO.output(safemode_led , 0)
		sleep(0.1)
		GPIO.output(safemode_led , 1)
		sleep(1)
		GPIO.output(default_led , 1)
	while True:
		if GPIO.input(hibernate_toggle) == 1:
			GPIO.output(default_led , 0)
			GPIO.output(safemode_led , 0)
			danger = 0
			sleep(0.5)
			print "Brakes Disengaged"
			if ty == 0:
				default()
			elif ty == 1:
				safemode()
		elif GPIO.input(safemode_toggle) == 1 and GPIO.input(hibernate_toggle) == 1:
			shutdown()

def danger_hibernate():
	global danger
	print "\n\nEmergency Brakes Engaged"
	stop()
	GPIO.output(default_led , 0)
	sleep(0.1)
	GPIO.output(default_led , 1)
	sleep(1)
	GPIO.output(safemode_led , 1)
	while True:
		if GPIO.input(hibernate_toggle) == 1:
			GPIO.output(default_led , 0)
			GPIO.output(safemode_led , 0)
			danger = 0
			print "Brakes Disengaged"
			sleep(1)
			default()
		elif GPIO.input(safemode_toggle) == 1 and GPIO.input(hibernate_toggle) == 1:
			shutdown()

def distance():
	global danger ; global shutd ; global safe_distance
	trig = 14
	echo = 15
	trig1 = 2
	echo1 = 3
	safe_guard = 0
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(trig , GPIO.OUT)
	GPIO.setup(trig1 , GPIO.OUT)
	GPIO.setup(echo , GPIO.IN)
	GPIO.setup(echo1 , GPIO.IN)
	GPIO.setup(safe_guard , GPIO.IN)
	GPIO.output(trig , 0)
	GPIO.output(trig1 , 0)


	sleep(1)
	stop_point = 0
	turn = 0
	while True:
		while danger == 0:
			if turn == 0:
				sleep(1)
				GPIO.output(trig , 1)
				if safe_guard = 0:
					print "Please configure the radar correctly, or boot in safe mode."
					shutdown()
				sleep(0.00001)
				GPIO.output(trig , 0)
				while GPIO.input(echo) == 0:
					zero_time = time()

				while GPIO.input(echo) == 1:
					one_time = time()
				turn = 1
				number = "0"
			elif turn == 1:
				sleep(1)
				GPIO.output(trig1 , 1)
				if safe_guard = 0:
					print "Please configure the radar correctly, or boot in safe mode."
					shutdown()
				sleep(0.00001)
				GPIO.output(trig1 , 0)
				while GPIO.input(echo1) == 0:
					zero_time = time()

				while GPIO.input(echo1) == 1:
					one_time = time()
				turn = 0
				number = "1"


			dst_time = one_time - zero_time
			distance = dst_time * speed_of_sound + 1
			if distance > safe_distance:
				stop_point = 0
			elif distance <= safe_distance:
				stop_point = stop_point + 1

			if stop_point == 2:
				print "\n\nOBJECT IN FRONT"
				stop_point = 0
				danger = 1
				break
			print "Distance(%s): %d" % (number , distance)
		if shutd == 1:
			GPIO.cleanup()
			exit(0)

def default():
	global danger
	while True:
		GPIO.output(default_led , 1)
		if GPIO.input(acc) == 1:
			forward()
			if GPIO.input(hibernate_toggle) == 1:
				hibernate(ty = 0)
			elif danger == 1:
				danger_hibernate()
		elif GPIO.input(hibernate_toggle) == 1:
			hibernate(ty = 0)
		elif danger == 1:
			danger_hibernate()
		else:
			GPIO.output(acc_led , 0)

def safemode():
	while True:
		GPIO.output(safemode_led , 1)
		if GPIO.input(acc) == 1:
			forward()
			if GPIO.input(hibernate_toggle) == 1:
				hibernate(ty = 1)
		elif GPIO.input(hibernate_toggle) == 1:
			hibernate(ty = 1)
		else:
			GPIO.output(acc_led , 0)

######### MAIN ##########

radar = Thread(target = distance , args = ())
try:
	print "Booting..."
	GPIO.output(acc_led , 1) ; GPIO.output(default_led , 1) ; GPIO.output(safemode_led , 1)
	sleep(5)
	GPIO.output(acc_led , 1) ; GPIO.output(default_led , 0) ; GPIO.output(safemode_led , 0)
	if GPIO.input(safemode_toggle) == 1:
		print "Booted in safemode"
		print "Press Ctrl + C for remote/emergency shutdown"
		safemode()
	else:
		print "Booted in default mode"
		print "Press Ctrl + C for remote/emergency shutdown"
		radar.start()
		default()
except KeyboardInterrupt:
	shutd = 1
	GPIO.cleanup()
	print "\nRemote Shutdown Complete"
	exit(0)
except:
	shutd = 1
	GPIO.cleanup()
	print "\n\n\n\n!!! Unexcpeted error shutdown !!!"
	exit(0)
