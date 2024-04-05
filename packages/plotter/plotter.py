#!/usr/bin/python3

import ftrobopy
import time
import os.path
from move_sync import move_sync
from plt_reader import plt_commands

def sign(x):
  if x >= 0:
    return 1
  else:
    return -1

class Plotter:

  def __init__(self, txt_hostname = None, init = True):
  
    if txt_hostname is None:
      txt_hostname = "localhost"

    self.txt = ftrobopy.ftrobopy(txt_hostname, 65000)

    self.my = self.txt.motor(1)
    self.mx = self.txt.motor(2)
    self.mz = self.txt.motor(3)
    self.iy = self.txt.input(1)
    self.ix = self.txt.input(2)
    self.iz = self.txt.input(3)

    self.px = 0
    self.py = 0
    self.up = False

    if init:
      self.init()

  def pen(self, up):
    if self.iz.state() == up:
      self.up = up
      return

    if up:
      self.mz.setSpeed(512)
    else:
      self.mz.setSpeed(-512)
    while self.iz.state() != up:
      self.txt.updateWait()
    self.mz.stop()
    self.txt.updateWait()
    self.up = up

    
  def init(self):
    self.pen(up = False)
    self.pen(up = True)

    move_x = not self.ix.state()
    move_y = not self.iy.state() 
    
    if move_x:
      self.mx.setSpeed(-256)
      
    if move_y:
      self.my.setSpeed(256)

    while move_x or move_y:
      if move_x and self.ix.state():
        self.mx.stop()
        move_x = False
        print("x axis inited")
      if move_y and self.iy.state():
        self.my.stop()
        move_y = False
        print("y axis inited")
        
    self.move(-200, 0, False)
    self.move(0, 200, False)
    self.px = 0
    self.py = 0


  def go(self, x, y):
    print("Go to %d %d" % (x, y))
    
    self.move(x-self.px, y-self.py)

    
  def move(self, dx, dy, emergency = True):
    print("Moving %d %d (check = %s)" % (dx, dy, emergency))
    
    if (dx == 0 and dy == 0):
        return

    if dx and dy:
      if not self.up and abs(dx*dx + dy*dy) > 10*10 \
         and abs(dx) > 5 and abs(dy) > 5:
        self.txt.incrCounterCmdId(0)
        self.txt.incrCounterCmdId(1)
        sensor_y=6
        sensor_x=5
        [dx, dy] = move_sync(self.txt, self.my, self.mx, -dy, -dx, sensor_y, sensor_x)
        self.px -= dy
        self.py -= dx
        return
      else:
        self.mx.setDistance(abs(dx))
        self.my.setDistance(abs(dy))      
      
    self.mx.setDistance(abs(dx))
    self.my.setDistance(abs(dy))      
    self.txt.updateWait()
        
    if dx > 0:
      self.mx.setSpeed(-512)
    if dx < 0:
      self.mx.setSpeed(512)
      
    if dy > 0:
      self.my.setSpeed(-512)
    if dy < 0:
      self.my.setSpeed(512)

    while True:
      self.txt.updateWait()
      if (dx == 0 or self.mx.getCurrentDistance() >= abs(dx)) and \
         (dy == 0 or self.my.getCurrentDistance() >= abs(dy)):
         break
      
      if emergency and (self.ix.state() or self.iy.state()):
        print("emergency stop!")
        exit(1)

    print("%d %d %d %d" % (dx, self.mx.finished(), dy, self.my.finished()))
      
    self.txt.updateWait(0.01)
    
    if dx:
      self.px += sign(dx) * self.mx.getCurrentDistance()
    if dy:
      self.py += sign(dy) * self.my.getCurrentDistance()

    self.mx.stop()
    self.my.stop()
    self.txt.updateWait()

    
  def home(self):
    print("home")
    self.move(-self.px, -self.py)
    
    
  def test(self):
    for i in range(100):
      p.pen(up = True)
      print("up")
    
      time.sleep(1)
  
      p.pen(up = False)
      print("down")
  
      time.sleep(1)

    
  def rect(self):
    self.pen(up = False)
    self.go(-1000, 0)
    self.go(-1000, 500)
    self.go(    0, 500)
    self.go(    0, 0)
    self.go(-1000, 500)
    self.pen(up = True)
    self.go(    0, 500)
    self.pen(up = False)
    self.go(-1000,    0)
    self.pen(up = True)

  def house(self):
    self.pen(up = False)
    self.move(-1000,  1000)
    self.move(  500,   500)    
    self.move(  500,  -500)
    self.move(-1000, -1000)
    self.move( 1000,     0)
    self.move(    0,  1000)
    self.move(-1000,     0)
    self.move(    0, -1000)
    self.pen(up = True)

  def shutdown(self):
    self.home()
    self.txt.stopOnline()
    time.sleep(0.1)
    

if __name__ == '__main__':
  if os.path.isfile('/etc/fw-ver.txt') :
    p = Plotter('localhost', True)
  else:
    p = Plotter('txt3.lan', True)

  if True:
    p.rect()

  if False:
    p.test()

  if False:
    for i in range(10):
      p.pen(True)
      p.pen(False)

  if False:
    for i in range(10):
      p.move(-2, 0)
      p.move(2, 0)

  if False:
    p.house()
    p.home()

  if False:
    cmds = plt_commands('data/Weltkarte.plt', max_height = 4000, max_width = 5000)
    for i in range(len(cmds)):
      cmd = cmds[i]
      #print(cmd[0])
      print("% 6d/% 6d" % (i+1, len(cmds)))
      (cmd[1])(p)

  p.shutdown()
  
  
