import cv2

# wrapper class around cv2 / ftrobopy
class Camera:

    def __init__(self, txt=None):
        self.txt=txt

        if self.txt is not None:
            import ftrobopy
            self.txt.startCameraOnline()
        else:
            self.cvcam = cv2.VideoCapture(0)
            
            if os.path.isfile("/etc/fw-ver.txt"):
                self.cvcam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                self.cvcam.set(cv2.CAP_PROP_FPS, 1) # no impact
                self.cvcam.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                if False:
                    self.cvcam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                    self.cvcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

            print("Resolution is %d x %d" % (self.cvcam.get(cv2.CAP_PROP_FRAME_WIDTH),
                                             self.cvcam.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        
    def getImage(self):
        image = None
        
        if self.cvcam:
            while True:
                t1 = datetime.now()
                status = self.cvcam.grab()
                t2 = datetime.now()
                dt = t2-t1
                #print("{} {}".format(status, dt))
                if dt.total_seconds() > 0.01:
                    # discard buffer
                    break
            image = self.cvcam.retrieve()
            status, image = self.cvcam.read()

        elif self.txt:

            while True:
                jpg = self.txt.getCameraFrame()
                if jpg is not None:
                    image = cv2.imdecode(numpy.frombuffer(bytearray(jpg)), cv2.IMREAD_COLOR)
                    break

        else:
            image = cv2.imread('singlemarkersoriginal.jpg')

        return image


