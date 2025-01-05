#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

from camera import Camera
from detector import Detector
from calibration import Calibration

import sys
from TouchStyle import *
from PyQt5 import QtCore, QtGui
import cv2
import numpy

class FtcGuiApplication(TouchApplication):
    def __init__(self, application):
        TouchApplication.__init__(self, application)

        self.camera = Camera()
        self.detector = Detector()
        self.calib = Calibration()
        self.calib.load(os.path.dirname(__file__) + "/calibration.json")

        self.linethickness = 3
        
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
        markerCorners, markerIds, rejectedCandidates = self.detector.detect(im)



        detected = ""
        orientation = ""
        if markerIds is not None:
            detected = str(markerIds)
            for corners in markerCorners:
                cv2.polylines(im, numpy.round(corners).astype(int), isClosed=True,
                              color=(255, 255, 255), thickness=self.linethickness)
                    
            if self.calib.valid():
                poses = self.calib.estimatePose(markerCorners)

                for pose in poses:
                    cv2.drawFrameAxes(im, self.calib.cameraMatrix(), None,
                                      pose["R"], pose["T"], length=15, thickness=self.linethickness);
                
                    angle_dist = self.calib.poseToAngleDist(pose)
                    orientation = u"{:.1f}cm, {:.1f}\N{DEGREE SIGN}".format(angle_dist["dist_cm"],
                                                            angle_dist["hori_angle"])

        # visualize make sure image persists in memory as Qt will not copy it
        f = 220/im.shape[1]
        self.im = cv2.resize(im, dsize=None, fx=f, fy=f)
        qim = QImage(self.im.data, self.im.shape[1], self.im.shape[0], self.im.strides[0],
                     QImage.Format_BGR888)
        pix = QtGui.QPixmap.fromImage(qim)
        self.image.setPixmap(pix)

        self.detected.setText(detected)
        self.orientation.setText(orientation)

        
if __name__ == "__main__":
    f = FtcGuiApplication(sys.argv)
