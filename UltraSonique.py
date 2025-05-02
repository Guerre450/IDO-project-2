
# Vcc = 5v
# GND = gnd
# ECHO = 14
# Trig = 15


#Libraries
import RPi.GPIO as GPIO
import time
import threading


class DetectorHandler(threading.Thread):

    def run(self):
        global distance
        self.kill = False


        self.value = 100
        refreshRateInSeconds = 0.05
        while not self.kill:
                self.value = distance()
                time.sleep(refreshRateInSeconds)



#Source : https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
 


def distance() -> float:
    #GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)
    
    #set GPIO Pins
    GPIO_TRIGGER = 21
    GPIO_ECHO = 20
    
    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
    searchStartTime = StartTime
    timeoutTime = 0.35
    # save awwaStartTime
    while GPIO.input(GPIO_ECHO) == 0 :
        StartTime = time.time()
        if (time.time()- searchStartTime) > timeoutTime:
             return 3000
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        if (time.time() - searchStartTime) > timeoutTime:
             return 3000
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
#print(distance())