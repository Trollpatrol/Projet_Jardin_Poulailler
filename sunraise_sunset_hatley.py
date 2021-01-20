# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 15:37:13 2020

@author: JN
"""
def sunraise_sunset_hatley():
      import datetime
      from suntime import Sun, SunTimeException

      latitude = 45.307840
      longitude = -71.992140

      sun = Sun(latitude, longitude)

      # Get today's sunrise and sunset in UTC
      today_sr = sun.get_sunrise_time()
      today_ss = sun.get_sunset_time()
      print('Today at Hatley the sun raised at {} and get down at {}'.
            format(today_sr.strftime('%H:%M'), today_ss.strftime('%H:%M')))

      return today_sr, today_ss