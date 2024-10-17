import cv2
import ftrobopy
import semantic_version

class Detector:
    def __init__(self):
        self.parameters = cv2.aruco.DetectorParameters()
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

        if (semantic_version.Version(cv2.__version__) >= semantic_version.Version('4.7.0')):
            self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)
        

    def detect(self, img):
        if (semantic_version.Version(cv2.__version__) >= semantic_version.Version('4.7.0')):
            return self.detector.detectMarkers(I)
        else:
            return cv2.aruco.detectMarkers(img, self.dictionary)

class Camera:

    def __init__(self):
        self.txt=None

        if False:
            self.txt=ftrobopy.ftTXT(directmode=True)
            self.txt.startCameraOnline()

        
        self.cvcam = cv2.VideoCapture(0)
        self.cvcam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        
    def getImage(self):
        image = None
        
        if self.cvcam:
            status, image = self.cvcam.read()

        elif self.txt:
            jpg = self.txt.getCameraFrame()
            if jpg != None:
                image = cv2.imdecode(np.frombuffer(bytearray(jpg)), cv2.IMREAD_COLOR)

        else:
            image = cv2.imread('singlemarkersoriginal.jpg')
            
        return image

if __name__ == "__main__":
    from datetime import datetime
    
    cam = Camera()
    detector = Detector()

    while True:
        print('read')
        I = cam.getImage()
        if I is None:
            print("failed to grab frame")
            continue
        start=datetime.now()
        markerCorners, markerIds, rejectedCandidates = detector.detect(I)
        print(datetime.now()-start)

        print(markerIds)





