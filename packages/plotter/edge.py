import numpy
import cv2
import os
        
class Tracer:
    def __init__(self, grayscale, thr1 = 100, thr2 = 200):
        self.thr1 = thr1
        self.thr2 = thr2
        self.img = grayscale

    def extract_contours(self):
        edges = cv2.Canny(self.img, self.thr1, self.thr2)
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST,
                                   cv2.CHAIN_APPROX_TC89_L1)
        return contours, edges

    def draw_contours(self, contours, img):
        cv2.drawContours(img, contours, -1, (0, 0, 0), 1)

    def plt_commands(self, contours, max_height = 2000, max_width = 2000, border = 200):
        # Returns an output compatible to plt_reader.plt_commands
        scale = min([max_width / self.img.shape[1], max_height / self.img.shape[0]])
        def transform(coord):
            x=coord[0] * scale - border - max_width
            y=coord[1] * scale + border
            return [x, y]
        cmds=[]
        cmds.append(["PI", lambda p: p.init()])
        #print(contours)
        for contour in contours:
            first = True
            for coord in contour:
                #print(coord)
                [x, y] = transform(coord[0])
                if first:
                    cmds.append(["PA (%d, %d)" % (x, y), lambda p, x=x, y=y: p.go(round(x), round(y))])
                    cmds.append(["PD", lambda p: p.pen(False)])
                    first = False
                else:
                    cmds.append(["PD (%d, %d)" % (x, y), lambda p, x=x, y=y: p.go(round(x), round(y))])
            cmds.append(["PU", lambda p: p.pen(True)])
            
        return cmds


        
if __name__ == "__main__":
    print("Opencv version: {}".format(cv2.__version__))
    
    img = cv2.imread('tree.jpg', cv2.IMREAD_GRAYSCALE)
    assert img is not None

    max_area = 540*360
    area = img.shape[0]*img.shape[1]
    if area > max_area:
        scale = numpy.sqrt(max_area / area)
        print("Scaling down to {}%".format(scale*100))
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation = cv2.INTER_AREA)

    t = Tracer(img)

    contours, edges = t.extract_contours()

    sum_length = sum([len(x) for x in contours])
    mean_length = sum_length / len(contours)
    print("{} contours were extracted with a total of {} points".
          format(len(contours), sum_length))

    longcontours = [x for x in contours if len(x) > mean_length]
    print("{} contours are longer than the mean {}".
          format(len(longcontours), mean_length))

    if False:
        from matplotlib import pyplot as plt

        cimg  = numpy.full(img.shape, 255, dtype=img.dtype)
        cimg2 = numpy.full(img.shape, 255, dtype=img.dtype)
        t.draw_contours(contours, cimg)
        t.draw_contours(longcontours, cimg2)

        plt.subplot(221)
        plt.imshow(img,cmap = 'gray')
        plt.title('Original Image'), plt.xticks([]), plt.yticks([])

        plt.subplot(222)
        plt.imshow(edges,cmap = 'gray')
        plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

        plt.subplot(223)
        plt.imshow(cimg,cmap = 'gray')
        plt.title('All Contours'), plt.xticks([]), plt.yticks([])

        plt.subplot(224)
        plt.imshow(cimg2,cmap = 'gray')
        plt.title('Long Contours'), plt.xticks([]), plt.yticks([])

        plt.show()

    if sum_length < 5000:
        cmds = t.plt_commands(contours)
    else:
        print("Plotting long contours")
        cmds = t.plt_commands(longcontours)

    if os.path.isfile('/etc/fw-ver.txt'):
        import plotter

        plotter = plotter.Plotter('localhost', True)
    else:
        import dummy_plotter
        plotter = dummy_plotter.Plotter()
        
    tasks = [lambda cmd=cmd: (cmd[1])(plotter) for cmd in cmds]
    for task in tasks:
        task()
