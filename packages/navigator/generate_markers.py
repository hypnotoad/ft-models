#!/usr/bin/python3

import cv2

parameters = cv2.aruco.DetectorParameters()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

size = 1000

for id in range(50):

    filename = "img-%03d.png" % id
    print(filename)
    img = dictionary.drawMarker(id, size)
    cv2.imwrite(filename, img)

board = cv2.aruco.CharucoBoard.create(5, 3, 10, 5, dictionary)
img = board.draw((1920, 1080))
cv2.imwrite("board.png", img)
