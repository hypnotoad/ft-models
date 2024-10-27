import json
import numpy
import cv2

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return super().default(obj)

class Calibration():
    def __init__(self, C=None, dist=None, marker_size_cm = 10):
        self.C = C
        self.dist = dist
        self.marker_size_cm = marker_size_cm
        
    def load(self, filename):
        try:
            with open(filename, "r") as f:
                loaded = json.load(f)
            self.C = numpy.asarray(loaded["camera_matrix"])
            self.dist = numpy.asarray(loaded["distortion"])
        except:
            pass
        
    def save(self, filename):
        calibration = {"camera_matrix": self.C,
                       "distortion": self.dist}
        with open(filename, "w") as f:
            json.dump(calibration, f, cls=NumpyEncoder)

    def cameraMatrix(self):
        return self.C

    def distortion(self):
        return self.dist

    def valid(self):
        return self.C is not None and self.dist is not None

    # Returns an array of poses computed from the camera calibration
    # and corner points (u;v) of detections. The poses are metric and
    # expressed in marker coordinate systems m:
    # https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html
    # [u;v;1] = C * X_c
    # X_c = R_mc * X_m + T_c
    #
    # For each marker, a separate rotation r_mc and translation T_c is
    # returned, where r_mc is the Rodriguez representation of R_mc.
    def estimatePose(self, corners):
        
        d = self.marker_size_cm/2
        marker_points = numpy.array([[-d,  d, 0],
                                     [ d,  d, 0],
                                     [ d, -d, 0],
                                     [-d, -d, 0]],
                                    dtype=numpy.float32)
        rvecs = []
        tvecs = []

        for c in corners:
            _, R, T = cv2.solvePnP(marker_points, c, self.C, self.dist, False,
                                   cv2.SOLVEPNP_IPPE_SQUARE)
            rvecs.append(R)
            tvecs.append(T)

        return rvecs, tvecs


if __name__ == "__main__":
    c = Calibration()
    c.load("calibration.json")
    print("{}\n{}\n{}".format(c.valid(), c.cameraMatrix(), c.distortion()))
    
