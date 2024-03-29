import numpy as np
import cv2 as cv

class Tracer:
    def __init__(self, grayscale, thr1 = 100, thr2 = 200):
        self.thr1 = thr1
        self.thr2 = thr2
        self.img = grayscale

    def extract_contours(self):
        edges = cv.Canny(self.img, self.thr1, self.thr2)

        contours, hierarchy = cv.findContours(edges, cv.RETR_LIST,
                                              cv.CHAIN_APPROX_TC89_L1)
        return contours, edges

    def draw_contours(self, contours, img):
        cv.drawContours(img, contours, -1, (0, 0, 0), 1)
        

if __name__ == "__main__":
    img = cv.imread('face.jpg', cv.IMREAD_GRAYSCALE)
    assert img is not None

    t = Tracer(img)

    contours, edges = t.extract_contours()
    sum_length = sum([len(x) for x in contours])
    mean_length = sum_length / len(contours)
    print("{} contours were extracted with a total of {} points".
          format(len(contours), sum_length))

    longcontours = [x for x in contours if len(x) > mean_length]
    print("{} contours are longer than the mean {}".
          format(len(longcontours), mean_length))

    cimg  = np.full(img.shape, 255, dtype=img.dtype)
    cimg2 = np.full(img.shape, 255, dtype=img.dtype)
    t.draw_contours(contours, cimg)
    t.draw_contours(longcontours, cimg2)

    from matplotlib import pyplot as plt
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
