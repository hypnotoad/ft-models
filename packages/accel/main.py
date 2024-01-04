#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys
import ADXL345
from TouchStyle import *

class FloatBar(QProgressBar):
    def __init__(self, minimum, maximum):
        super(FloatBar, self).__init__()
        #self.valueChanged.connect(self.onValueChanged)
        self.minimum = minimum
        self.range = maximum - minimum

    #def onValueChanged(self, value):
    #    self.setFormat('%.02f%%' % (self.prefixFloat))

    def setValue(self, value):
        QProgressBar.setValue(self, int(100*(value-self.minimum)/self.range))
        
class FtcGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.sensor = ADXL345.ADXL345()

        vbox = QVBoxLayout()

        self.x = FloatBar(-10, 10)
        vbox.addWidget(self.x)

        self.y = FloatBar(-10, 10)
        vbox.addWidget(self.y)

        self.z = FloatBar(-10, 10)
        vbox.addWidget(self.z)
        
        self.w = TouchWindow("Lidar Sensor")
        self.w.centralWidget.setLayout(vbox)
        self.w.show()


        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        self.exec()

    def update(self):
        axes = self.sensor.get_all_axes()
        self.x.setValue(axes['x'])
        self.y.setValue(axes['y'])
        self.z.setValue(axes['z'])
        


if __name__ == "__main__":

    f = FtcGuiApplication(sys.argv)

