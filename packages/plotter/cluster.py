#/usr/bin/python3

import cv2 as cv
import numpy as np

class Segmenter:
    def __init__(self, image, K=5):
        self.K=K
        self.image=image

    def segment(self):
        img = self.image
        vec = img.reshape(img.shape[0]*img.shape[1], img.shape[2])
        vec = np.float32(vec)

        criteria=(cv.TermCriteria_COUNT, 100, 10)
        loss, bestLabels, centers = cv.kmeans(vec, self.K, None,
                                              criteria=criteria,
                                              attempts=10,
                                              flags=cv.KMEANS_PP_CENTERS)
        #print("Quantization loss: {}%".format(loss/img.shape[0]/img.shape[1]/255))

        labelimg = bestLabels.reshape(img.shape[0], img.shape[1])
        return labelimg, bestLabels, centers

if __name__ == "__main__":
    img = cv.imread('face.jpg')

    s = Segmenter(img)
    labelimg, bestLabels, centers = s.segment()
    
    #v = np.not_equal(labelimg[1:, :-1], labelimg[0:-1, :-1])
    #h = np.not_equal(labelimg[:-1, 1:], labelimg[:-1, 0:-1])
    #border = np.logical_or(v, h)
    #border = np.uint8(border)*128
    #cv.imshow("border", border)
    #cv.waitKey(0)


    centers = np.uint8(centers)
    img2 = centers[bestLabels.flatten()]
         
    img2 = img2.reshape(img.shape)
    cv.imshow("quantized", img2)
    cv.waitKey(0)
         
