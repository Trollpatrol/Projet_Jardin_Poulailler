import time
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import RPi.GPIO as GPIO
from gpiozero import Motor
from sunraise_sunset_hatley import sunraise_sunset_hatley

#set GPIO numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set GPIO inputs

#set GPIO outputs


#set time and date variables
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

