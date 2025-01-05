#! /usr/bin/env python3

import os
import ftrobopy
import time

from odometry_temp import OdometryTemp
from camera import Camera
from detector import Detector
from calibration import Calibration

calib = Calibration()
calib.load(os.path.dirname(__file__) + "/calibration.json")
assert(calib.valid())

camera = Camera()
detector = Detector()


txt = ftrobopy.ftrobopy()
odo = OdometryTemp(txt)

while True:

    im = camera.getImage()
    markerCorners, markerIds, rejectedCandidates = detector.detect(im)

    angle_dist = None
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



    if angle_dist is not None:
        dist, duration = odo.compute_speeds_and_duration(angle_dist)
        print("{} for {:.1f}s".format(dist, duration))

        odo.set_motors(dist)
        time.sleep(duration)
        odo.set_motors(None)

