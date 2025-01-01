import cv2
import os
import numpy
import semantic_version
from calibration import Calibration
from datetime import datetime
    

# wrapper call around cv2.aruco
class Detector:
    def __init__(self):
        self.parameters = cv2.aruco.DetectorParameters()
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.is_new_opencv = semantic_version.Version(cv2.__version__) >= semantic_version.Version('4.7.0')

        if self.is_new_opencv:
            self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)
        

    def detect(self, img):
        if self.is_new_opencv:
            return self.detector.detectMarkers(img)
        else:
            return cv2.aruco.detectMarkers(img, self.dictionary)

    def getDictionary(self):
        return self.dictionary

if __name__ == "__main__":
    from camera import Camera
    calibFilename = "calibration.json"
    
    cam = Camera()
    detector = Detector()
    calib = Calibration()
    calib.load(calibFilename)
    
    if not calib.valid():
        board = cv2.aruco.CharucoBoard((5, 3), 10, 5, detector.getDictionary())
        #board = cv2.aruco.CharucoBoard.create(5, 3, 10, 5, dictionary)
        calibrator = cv2.aruco.CharucoDetector(board)
        calibration_flags = 0
    else:
        calibrator = None
    
    start_read_previous = None
    all_obj_points = []
    all_img_points = []
    for bild_nr in range(1000000):
        start_read = datetime.now()
        I = cam.getImage()
        image_size = (I.shape[1], I.shape[0])
        if I is None:
            print("failed to grab frame")
            continue
        start_det=datetime.now()

        detections = "None"
        if calibrator:
            if bild_nr % 10 == 0:
                #charucoCorners, charucoIds, markerCorners, markerIds = board.detectBoard(I)
                charucoCorners, charucoIds, markerCorners, markerIds = calibrator.detectBoard(I)
                detections = str(markerIds)
                #print("{} {}".format(charucoCorners, charucoIds))

                if charucoIds is not None and len(charucoIds) > 3:
                    objPoints, imgPoints = board.matchImagePoints(charucoCorners, charucoIds)
                else:
                    objPoints = []
                    
                if len(objPoints) > 3:
                    print("Matched: {} {}".format(objPoints, imgPoints))
                    all_obj_points.append(objPoints)
                    all_img_points.append(imgPoints)
                else:
                    print("not enought points")
        else:
            markerCorners, markerIds, rejectedCandidates = detector.detect(I)

            if len(markerCorners) > 0:
                poses = calib.estimatePose(markerCorners)
                pose = calib.poseToPlane(poses[0])
                # angles = numpy.arctan2(e_z[0:2], e_z[2]) / numpy.pi * 180
                detections = "{} a=xx, T={}".format(
                    markerIds[0],
                    #angles.transpose(),
                    pose["T"].transpose())
            else:
                detections = str(markerIds)



        done = datetime.now()

        if start_read_previous:
            dl = start_read - start_read_previous
            dr = start_det - start_read
            dd = done - start_det
            print("Loop % 4d, read % 4d, detect % 4d ms: %s" % (dl.total_seconds()*1000, dr.total_seconds()*1000,
                                                                dd.total_seconds()*1000, detections))

        if len(all_obj_points) % 8 == 7:
            print("Computing camera parameters for camera of size {}...".format(image_size))
            retval, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera(all_obj_points, all_img_points, image_size, None, None, flags = calibration_flags)
            print("Calib RMSE {}\nC=\n{}\nDist={}".format(retval, cameraMatrix, distCoeffs))

            calibration = calibration.Calibration(cameraMatrix, distCoeffs)
            calibration.save(calibFilename)
            
            break

        start_read_previous = start_read




