#!/usr/bin/python3

import cv2
import numpy

parameters = cv2.aruco.DetectorParameters()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

size = 6
# 15mm

# https://fischerfriendsman.de/index.php?p=2&sp=5&add=100:2822#R2822
parts = numpy.array([
    [0,   4, 1, 133008],
    [0,   3, 2,  38237],
    [0,   3, 1,  38261],
    [0,   2, 2,  38265],
    [0,   1, 1,  36911],
    [255, 1, 1,  38263]
])


order = numpy.full((parts.shape[0], 1), 0)

for id in range(5):

    code = dictionary.drawMarker(id, size)

    free = numpy.full((size, size), True)
    for idx, row in enumerate(parts):
        color, sy, sx, partnumber = row
        for i in range(size-sy+1):
            ai = numpy.arange(i, i+sy)

            for j in range(size-sx+1):
                aj = numpy.arange(j, j+sx)

                def try_fit(r1, r2):
                    r12 = numpy.ix_(r1, r2)
                    if numpy.all(code[r12] == color) and numpy.all(free[r12]):
                        #print("fitting {} ({},{}) to ({},{})".format(color, sy, sx, r1, r2))
                        free[r12] = False
                        order[idx, 0] += 1

                try_fit(ai, aj)
                try_fit(aj, ai)

    assert(numpy.all(free == False))

for idx in range(order.shape[0]):
    print("% 10d  %d" % (parts[idx, 3], order[idx]))
        
