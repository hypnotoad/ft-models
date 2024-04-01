import cv2
import numpy
from PyQt5.QtGui import QImage

class Plotter:

  def __init__(self, width=4000, height=4000, flip_y = False):
    self.flip_y = flip_y
    self.size = (height, width)
    self.image  = numpy.full(self.size, 255, dtype=numpy.uint8)
    self.pen_is_up = True
    self.position = (0, 0)

  def pen(self, up):
    self.pen_is_up = up
    
  def init(self):
    self.pen(True)
    self.go(0,0)

  def go(self, x, y):
    if self.flip_y:
      to = (-x, self.size[0]-y)
    else:
      to = (-x, y)
    if not self.pen_is_up:
      cv2.line(self.image, self.position, to, color=(0, 0, 0))
    self.position = to

  def move(self, dx, dy, emergency = True):
    self.go(self.position[0]+dx, self.position[1]+dy)
    
  def home(self):
    self.go(0, 0)

  def get_cv2_preview(self, width, height):
    factor = min(width / self.image.shape[1], height / self.image.shape[0])
    return cv2.resize(self.image, None, fx=factor, fy=factor, interpolation = cv2.INTER_AREA)

  def get_qt_preview(self, width, height):
    cv_img = self.get_cv2_preview(width, height)
    return QImage(cv_img.data, cv_img.shape[1], cv_img.shape[0], QImage.Format_Grayscale8).copy()


