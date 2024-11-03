#! /usr/bin/env python3

import os
import ftrobopy
import numpy

from detector import Camera, Detector
from calibration import Calibration

calib = Calibration()
calib.load(os.path.dirname(__file__) + "/calibration.json")
assert(calib.valid())

camera = Camera()
detector = Detector()


txt = ftrobopy.ftrobopy()

motors = [txt.motor(i) for i in range(1,5)]
motions = numpy.array([[ 1,  1,  1,  1 ],
                       [ 1, -1, -1,  1 ],
                       [ 1, -1,  1, -1 ]])

while True:

    im = camera.getImage()
    markerCorners, markerIds, rejectedCandidates = detector.detect(im)

    detected = ""
    orientation = ""
    if markerIds is not None:
        poses = calib.estimatePose(markerCorners)
        pose = calib.poseToPlane(poses[0])
        print(pose["T"])

        if pose["T"][0] > 0:
            print("right")
            move=numpy.array([[0, 1, 0]])
        else:
            print("left")
            move=numpy.array([[0, -1, 0]])

        dist = move.dot(motions)
    else:
        dist = numpy.array([[0, 0, 0, 0]])
        
    txt.SyncDataBegin()
    for i in range(len(motors)):
        x = 400
        s = min(512, int(x*dist[0][i]))
        motors[i].setSpeed(s)
    txt.SyncDataEnd()
