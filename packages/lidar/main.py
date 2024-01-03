#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys
import VL53L0X
from TouchStyle import *


class FtcGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.sensor = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)
        self.sensor.open()
        self.sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

        timing = self.sensor.get_timing()
        if timing < 20000:
            timing = 20000
        print("Timing %d ms" % (timing/1000))

        vbox = QVBoxLayout()

        self.pr = QProgressBar()
        self.pr.setFormat("%v mm")
        self.pr.setMaximum(500)
        vbox.addWidget(self.pr)

        self.w = TouchWindow("Lidar Sensor")
        self.w.centralWidget.setLayout(vbox)
        self.w.show()


        self.timer = QTimer()
        self.timer.timeout.connect(self.updateColor)
        self.timer.start(100)

        self.exec()

    def updateColor(self):
        mm = self.sensor.get_distance()
        
        self.pr.setValue(round(mm))
        print("mm: %s" % mm)
        
    def stop(self):
        self.sensor.tof.stop_ranging()
        self.sensor.tof.close()


if __name__ == "__main__":

    f = FtcGuiApplication(sys.argv)
    f.stop()
