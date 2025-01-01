import cv2
import numpy
            
# wrapper class around cv2 / ftrobopy / static test image
class Camera:

    def __init__(self, txt=None, testimage=None):
        self.txt = None
        self.cvcam = None
        self.testimage = None

        if testimage is not None:
            self.testimage = testimage
            
        elif txt is not None:
            import ftrobopy
            self.txt = txt
            self.txt.startCameraOnline(width=640, height=480, fps=20)
            
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
            return image

        if self.txt:

            tries=30
            for t in range(tries):
                jpg = self.txt.getCameraFrame()
                if jpg is not None:
                    img = cv2.imdecode(numpy.frombuffer(bytearray(jpg)), cv2.IMREAD_COLOR)
                    if img.size != 0:
                        return img
                print("Retrying {}/{}".format(t+1, tries))

        if self.testimage:
            return cv2.imread(self.testimage)

        print("WARNING: Giving up!")
        return None


if __name__ == "__main__":
    import ftrobopy
    hostname = 'txt2.lan'
    outfilename = 'out.jpg'

    while True:
        txt = ftrobopy.ftrobopy(hostname)
        cam = Camera(txt)
        img = cam.getImage()

        if img is not None:
            cv2.imwrite(outfilename, img)
            exit(0)
    
    
    
