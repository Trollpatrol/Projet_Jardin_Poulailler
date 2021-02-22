import time
import RPi.GPIO as GPIO
from datetime import date
from datetime import datetime
from datetime import timedelta
from gpiozero import Motor
from sunraise_sunset_hatley import sunraise_sunset_hatley
import threading
#for GTT001 and GTT002
from w1thermsensor import W1ThermSensor
#for GHT001
import board
import busio
from adafruit_htu21d import HTU21D
#for Anvil server
import anvil.server
anvil.server.connect('TQ6PCXQLJY54QWZGKZQHC3GM-O2TT5S2TVWUJ6HFQ')

#set GPIO numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set GPIO inputs
LS001 = 17
LS002 = 18
PB001 = 11
PB002 = 8
GHT002 = 9
FLOAT001 = 7
FLOAT002 = 6
GPU001 = 12
WFT001 = 24 #flow on irrigation board
GPIO.setup(LS001, GPIO.IN)
GPIO.setup(LS002, GPIO.IN)
GPIO.setup(PB001, GPIO.IN)
GPIO.setup(PB002, GPIO.IN)
GPIO.setup(GHT002, GPIO.IN)
GPIO.setup(FLOAT001, GPIO.IN)
GPIO.setup(FLOAT002, GPIO.IN)
GPIO.setup(GPU001, GPIO.IN)
GPIO.setup(WFT001, GPIO.IN)

#set GPIO outputs
WPU001 = 25
MU001_forward = 22
MU001_backward = 23
WVS001 = 13 #S1 on irrigation board
WVS002 = 16 #S2 on irrigation board
WVS003 = 19 #S3 on irrigation board
GPIO.setup(WPU001, GPIO.OUT)
GPIO.setup(MU001_forward, GPIO.OUT)
GPIO.setup(MU001_backward, GPIO.OUT)
GPIO.setup(WVS001, GPIO.OUT)
GPIO.setup(WVS002, GPIO.OUT)
GPIO.setup(WVS003, GPIO.OUT)

#set coop door motor
door_motor = Motor(forward=MU001_forward, backward=MU001_backward)

#set GTT001
GTT001 = W1ThermSensor()

#set GHT001
i2c = busio.I2C(board.SCL, board.SDA)
GHT001 = HTU21D(i2c)

#set alarm levels
max_time_door = 10

#set global variables
door_status = 'Fermée'
coop_auto_loop = False

#set time and date variables
@anvil.server.callable
def get_date_times():
    global time_now
    global date_now
    global time_open_door
    global time_close_door 
    today_sr, today_ss = sunraise_sunset_hatley()
    time_open_door = today_sr
    time_close_door = today_ss + timedelta(minutes=30)
    today_sr = today_sr.strftime('%H:%M')
    today_ss = today_ss.strftime('%H:%M')
    time_open_door = time_open_door.strftime('%H:%M')
    time_close_door = time_close_door.strftime('%H:%M')
    now = datetime.now()
    date_now = now.strftime('%Y-%m-%d')
    time_now = now.strftime('%H:%M')
    return date_now, time_now, time_open_door, time_close_door

@anvil.server.callable
def open_coop_door():
    global door_status
    door_motor.forward()
    for i in range(0,max_time_door,1):
        i += 1
        time.sleep(1)
        print(i)
        if GPIO.input(LS001):
            door_motor.stop()
            door_status = 'Ouverte'
            return
        if i == max_time_door:
            door_motor.stop()
            door_status = 'Alarme LS001'
        else:
            pass

@anvil.server.callable
def close_coop_door():
    global door_status
    door_motor.backward()
    for i in range(0,max_time_door,1):
        i += 1
        print(i)
        time.sleep(1)
        if GPIO.input(LS002):
            door_motor.stop()
            door_status = 'Fermée'
            return
        if i == max_time_door:
            door_motor.stop()
            door_status = 'Alarme LS002'
        else:
            pass 

def coop_auto_mode():
    global coop_auto_loop
    coop_auto_loop = True
    while coop_auto_loop == True:
        time.sleep(1)
        print('auto mode')
        if time_now == time_open_door:
            open_coop_door()
        if time_now == time_close_door:
            close_coop_door()

@anvil.server.callable
def run_coop_auto():
    global coop_auto_loop
    coop_auto_loop = True
    coop = threading.Thread(target=coop_auto_mode)
    coop.start()

@anvil.server.callable
def kill_coop_auto():
    global coop_auto_loop
    coop_auto_loop = False
    

@anvil.server.callable
def check_door_status():
    return door_status

@anvil.server.callable
def get_soil_temp():
    global soil_temp
    soil_temp = GTT001.get_temperature()
    return soil_temp

@anvil.server.callable
def get_coop_temp_hum():
    global coop_temp
    global coop_hum
    coop_temp = GHT001.temperature
    coop_hum = GHT001.relative_humidity
    return coop_temp, coop_hum
    
anvil.server.wait_forever()