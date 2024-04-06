#!/usr/bin/python3

import ftrobopy
import time
import os

class FtTiming:

  def __init__(self, input_nr):
  
    txt_hostname = os.environ.get('FT_TXT')
    if txt_hostname is None:
      txt_hostname = "localhost"
    try:
      self.txt = ftrobopy.ftrobopy(txt_hostname, 65000)
    except Exception as e:
      print("Could not connect: %s" % e)
      exit(1)

    self.sensor = self.txt.resistor(input_nr)

  def step(self):
    self.txt.updateWait()
    t = time.clock_gettime(time.CLOCK_MONOTONIC)
    v = self.sensor.value()
    return { "time" : t,
             "value" : v}


if __name__ == "__main__":
  timer = FtTiming(1)
  o = None
  while True:
    m = timer.step()
    if (o):
      d = m["time"]-o
      print("%3.6f: %5.1f Ohm" % (d, m["value"]))
    o = m["time"]

    

    
  
