#/usr/bin/python3

import cv2 as cv
import numpy as np

K=10

img = cv.imread('face.jpg')
vec = img.reshape(img.shape[0]*img.shape[1], img.shape[2])
vec = np.float32(vec)
print(vec.shape)

criteria=(cv.TermCriteria_COUNT, 100, 10)
loss, bestLabels, centers = cv.kmeans(vec, K, None,
                                      criteria=criteria,
                                      attempts=10,
                                      flags=cv.KMEANS_PP_CENTERS)
print("Quantization loss: {}%".format(loss/img.shape[0]/img.shape[1]/255))

labelimg = bestLabels.reshape(img.shape[0], img.shape[1])
v = np.not_equal(labelimg[1:, :-1], labelimg[0:-1, :-1])
h = np.not_equal(labelimg[:-1, 1:], labelimg[:-1, 0:-1])
border = np.logical_or(v, h)
border = np.uint8(border)*128
cv.imshow("border", border)
cv.waitKey(0)


centers = np.uint8(centers)
img2 = centers[bestLabels.flatten()]
         
img2 = img2.reshape(img.shape)
cv.imshow("quantized", img2)
cv.waitKey(0)
         
