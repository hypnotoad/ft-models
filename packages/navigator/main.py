#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import detector

import sys
from TouchStyle import *
from PyQt5 import QtCore, QtGui
import cv2

class FtcGuiApplication(TouchApplication):
    def __init__(self, application):
        TouchApplication.__init__(self, application)

        self.camera = detector.Camera()
        self.detector = detector.Detector()

        # create the empty main window
        w = TouchWindow("Navigator")
        vbox = QVBoxLayout()

        self.image = QLabel()
        vbox.addWidget(self.image)

        self.detected = QLabel()
        vbox.addWidget(self.detected)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)
        
        w.centralWidget.setLayout(vbox)
        w.show()
        
        self.exec()

    def update(self):
        im = self.camera.getImage()
        f = 220/im.shape[1]
        
        # make sure image persists in memory as Qt will not copy it
        self.im = cv2.resize(im, dsize=None, fx=f, fy=f)
        qim = QImage(self.im.data, self.im.shape[1], self.im.shape[0], self.im.strides[0],
                     QImage.Format_BGR888)
        pix = QtGui.QPixmap.fromImage(qim)
        self.image.setPixmap(pix)

        markerCorners, markerIds, rejectedCandidates = self.detector.detect(im)

        if markerIds is not None:
            detected = str(markerIds)
        else:
            detected = ""
        self.detected.setText(detected)

        
if __name__ == "__main__":
    f = FtcGuiApplication(sys.argv)
