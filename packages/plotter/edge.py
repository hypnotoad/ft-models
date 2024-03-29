import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

thr1 = 100
thr2 = 200

img = cv.imread('face.jpg', cv.IMREAD_GRAYSCALE)
assert img is not None, "file could not be read, check with os.path.exists()"
edges = cv.Canny(img, thr1, thr2)

contours, hierarchy = cv.findContours(edges, cv.RETR_LIST,
                                 cv.CHAIN_APPROX_TC89_L1)

sum_length = sum([len(x) for x in contours])
mean_length = sum_length / len(contours)
print("{} contours were extracted with a total of {} points".
      format(len(contours), sum_length))

longcontours = [x for x in contours if len(x) > mean_length]
print("{} contours are longer than the mean {}".
      format(len(longcontours), mean_length))

cimg  = np.full(img.shape, 255, dtype=img.dtype)
cimg2 = np.full(img.shape, 255, dtype=img.dtype)
cv.drawContours(cimg, contours, -1, (0, 0, 0), 2)
cv.drawContours(cimg2, longcontours, -1, (0, 0, 0), 2)

plt.subplot(221)
plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])

plt.subplot(222)
plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.subplot(223)
plt.imshow(cimg,cmap = 'gray')
plt.title('Contour Image'), plt.xticks([]), plt.yticks([])

plt.subplot(224)
plt.imshow(cimg2,cmap = 'gray')
plt.title('Contour Image'), plt.xticks([]), plt.yticks([])


plt.show()
