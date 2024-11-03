#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import detector
from calibration import Calibration

import sys
from TouchStyle import *
from PyQt5 import QtCore, QtGui
import cv2
import numpy

class FtcGuiApplication(TouchApplication):
    def __init__(self, application):
        TouchApplication.__init__(self, application)

        self.camera = detector.Camera()
        self.detector = detector.Detector()
        self.calib = Calibration()
        self.calib.load(os.path.dirname(__file__) + "/calibration.json")

        # create the empty main window
        w = TouchWindow("Navigator")
        vbox = QVBoxLayout()

        self.image = QLabel()
        vbox.addWidget(self.image)

        self.detected = QLabel()
        vbox.addWidget(self.detected)

        self.orientation = QLabel()
        vbox.addWidget(self.orientation)

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

        detected = ""
        orientation = ""
        if markerIds is not None:
            detected = str(markerIds)
            if self.calib.valid():
                poses = self.calib.estimatePose(markerCorners)
                pose = self.calib.poseToPlane(poses[0])
                #Tc = poses[0]["T"]
                #angles = numpy.arctan2(Tc[0:2], Tc[2]) / numpy.pi * 180
                
                #detected = "T=" + numpy.array_str(Tc[:,0].transpose(), precision=1)
                #orientation = "α=" + numpy.array_str(angles[:,0].transpose(), precision=1)
                detected = "T=" + numpy.array_str(pose["T"][:,0].T, precision=1)

        self.detected.setText(detected)
        self.orientation.setText(orientation)

        
if __name__ == "__main__":
    f = FtcGuiApplication(sys.argv)
