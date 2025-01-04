#! /usr/bin/env python3

import os
import ftrobopy
import numpy
import time

from camera import Camera
from detector import Detector
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

def set_motors(dist):
    assert(dist.shape[0] == 1)
    txt.SyncDataBegin()
    for i in range(len(motors)):
        x = 300
        s = max(-512, min(512, int(x*dist[0][i])))
        motors[i].setSpeed(s)
    txt.SyncDataEnd()

def add_component(measurement, target, threshold, index):
    retval = numpy.array([[0, 0,  0]])
    offset = target - measurement
    if abs(offset) > threshold:
        retval[0][index] = 1 if offset < 0 else -1
    return retval

while True:

    im = camera.getImage()
    markerCorners, markerIds, rejectedCandidates = detector.detect(im)

    detected = ""
    orientation = ""
    move = numpy.array([[0, 0, 0]]) #fwd, right, turn
    if markerIds is not None:
        poses = calib.estimatePose(markerCorners)
        angle_dist = calib.poseToAngleDist(poses[0])
        detections = "{}  h: {}° v: {}° d: {}cm".format(
            markerIds[0],
            angle_dist["hori_angle"],
            angle_dist["vert_angle"],
            angle_dist["dist_cm"]
        )
        print(detections)

        move += add_component(angle_dist["hori_angle"], target=0, threshold=3, index=2)
        move += add_component(angle_dist["dist_cm"], target=100, threshold=5, index=0)

    print(move)

    dist = move.dot(motions)
    set_motors(dist)
    time.sleep(0.2)
    set_motors(numpy.array([[0, 0, 0, 0]]))

    # not let's calibrate the moto speeds
