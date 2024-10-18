import cv2

parameters = cv2.aruco.DetectorParameters()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

size = 1000

for id in range(10):
    
    img = dictionary.drawMarker(id, size)
    cv2.imwrite("img-%03d.png" % id, img)

board = cv2.aruco.CharucoBoard.create(5, 3, 10, 5, dictionary)
img = board.draw((1920, 1080))
cv2.imwrite("board.png", img)
