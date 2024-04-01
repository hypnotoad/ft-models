import math

class Plotter:

  def __init__(self):
    self.distance = None
    self.pen_movements = None
    self.lines = None
    self.position = None
    self.init()

  def __del__(self):
    self.print_stats()

  def print_stats(self):
    print("Distance: {}, Segments: {}, Updowns: {}".format(self.distance, self.lines, self.pen_movements))

  def pen(self, up):
    self.pen_movements += 1
    
  def init(self):
    if self.distance:
        self.print_stats()

    self.distance = 0
    self.pen_movements = 0
    self.lines = 0
    self.position = (0, 0)

  def go(self, x, y):
    self.distance += math.sqrt((x-self.position[0]) ** 2 + (y-self.position[1]) ** 2)
    self.lines += 1
    self.position = (x, y)

  def move(self, dx, dy, emergency = True):
    self.go(self.position[0]+dx, self.position[1]+dy)
    
  def home(self):
    self.go(0, 0)
