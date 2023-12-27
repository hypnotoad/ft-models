#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import gestensensor
from TouchStyle import *


class FtcGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.sensor = gestensensor.Gestensensor(1)
        self.red = self.sensor.crgbToHsv([1, 1, 0, 0])
        self.blue = self.sensor.crgbToHsv([1, 0, 0, 1])
        self.green = self.sensor.crgbToHsv([1, 0, 1, 0])
        print("red: %s, blue: %s, green: %s" % (self.red, self.blue, self.green))

        vbox = QVBoxLayout()

        self.hsv = QLabel()
        self.hsv.setText("Hue Similarities")
        vbox.addWidget(self.hsv)

        self.pr = QProgressBar()
        self.pr.setFormat("%v")
        self.pr.setStyleSheet("background-color:red;")
        vbox.addWidget(self.pr)

        self.pb = QProgressBar()
        self.pb.setFormat("%v")
        self.pb.setStyleSheet("background-color:blue;")
        vbox.addWidget(self.pb)

        self.pg = QProgressBar()
        self.pg.setFormat("%v")
        self.pg.setStyleSheet("background-color:green;")
        vbox.addWidget(self.pg)
        
        self.w = TouchWindow("Gesture Sensor")
        self.w.centralWidget.setLayout(vbox)
        self.w.show()


        self.timer = QTimer()
        self.timer.timeout.connect(self.updateColor)
        self.timer.start(100)

        self.exec()

    def updateColor(self):
        crgb = self.sensor.crgb()
        hsv = self.sensor.crgbToHsv(crgb)
        r = 1-self.sensor.hueDiff(hsv, self.red)
        b = 1-self.sensor.hueDiff(hsv, self.blue)
        g = 1-self.sensor.hueDiff(hsv, self.green)
        
        self.pr.setValue(round(r*100))
        self.pb.setValue(round(b*100))
        self.pg.setValue(round(g*100))
        print("crgb: %s hsv: %s" % (crgb, hsv))


if __name__ == "__main__":

    FtcGuiApplication(sys.argv)
