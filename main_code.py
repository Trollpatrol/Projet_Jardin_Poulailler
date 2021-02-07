import time
import RPi.GPIO as GPIO
from datetime import date
from datetime import datetime
from datetime import timedelta
from gpiozero import Motor
from sunraise_sunset_hatley import sunraise_sunset_hatley
import threading
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
GTT001 = 4 #temp on irrigation board
GHT002 = 9
FLOAT001 = 7
FLOAT002 = 6
GPU001 = 12
WFT001 = 24 #flow on irrigation board
GPIO.setup(LS001, GPIO.IN)
GPIO.setup(LS002, GPIO.IN)
GPIO.setup(PB001, GPIO.IN)
GPIO.setup(PB002, GPIO.IN)
GPIO.setup(GTT001, GPIO.IN)
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

anvil.server.wait_forever()