import cv2

parameters = cv2.aruco.DetectorParameters()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

size = 1000

for id in range(10):
    
    img = dictionary.drawMarker(id, size)
    cv2.imwrite("img-%03d.png" % id, img)
