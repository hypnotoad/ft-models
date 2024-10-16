import cv2
from datetime import datetime

parameters = cv2.aruco.DetectorParameters()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

cam = None
#cam = cv2.VideoCapture(0)
I=cv2.imread('singlemarkersoriginal.jpg')
    
while True:
    print('read')
    if cam is not None:
        ret, I = cam.read()
        if not ret:
            print("failed to grab frame")
            continue
#    cv2.imshow("test", I)
    start=datetime.now()
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(I)
    print(datetime.now()-start)
    
    print(markerCorners)
