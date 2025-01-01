import json
import numpy
import cv2

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return super().default(obj)

class Calibration():
    def __init__(self, C=None, dist=None, marker_size_cm = 15, image_size = [640, 480]):
        self.C = C
        self.dist = dist
        self.marker_size_cm = marker_size_cm
        self.image_size = image_size
        
    def load(self, filename):
        try:
            with open(filename, "r") as f:
                loaded = json.load(f)
            self.C = numpy.asarray(loaded["camera_matrix"])
            self.dist = numpy.asarray(loaded["distortion"])
            self.image_size = loaded["image_size"]
            self.marker_size_cm = loaded["marker_size_cm"]
        except:
            pass
        
    def save(self, filename):
        calibration = {"camera_matrix": self.C,
                       "distortion": self.dist,
                       "image_size": self.image_size,
                       "marker_size_cm": self.marker_size_cm}
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
    # X_c = [I, 0] * [R, T; 0^T, 1] * [X_m; 1]
    #     = [R, T] * [X_m; 1]
    #     = R*X_m + T
    # Marker coordinates are defined as z=0, the center being in the middle of the marker.
    #
    # [u;v;1] = C * X_c
    #
    # For each marker, a separate pose is returned with R and T, where
    # R is the Rodriguez representation of the matrix R above.
    def estimatePose(self, corners):
        
        d = self.marker_size_cm/2
        marker_points = numpy.array([[-d,  d, 0],
                                     [ d,  d, 0],
                                     [ d, -d, 0],
                                     [-d, -d, 0]],
                                    dtype=numpy.float32)
        poses = []
        for c in corners:
            _, rvec, T = cv2.solvePnP(marker_points, c, self.C, self.dist, False,
                                      cv2.SOLVEPNP_IPPE_SQUARE)
            R, _ = cv2.Rodrigues(rvec)
            poses.append({"R": R,
                          "T": T})

        return poses

    def poseToPlane(self, pose, vertical_offset_cm=0):
        # Returns a 2D pose on the plane. vertical_offset is
        # the upwards distance from camera to the bottom of
        # the marker.
        #
        # calibration defines R,T
        e1 = numpy.array([[1, 0,  0]])
        e2 = numpy.array([[0, 0, -1]])
        e3 = numpy.array([[0, 1,  0]])
        R = numpy.concatenate((e1.T, e2.T, e3.T), axis=1)
        assert(numpy.linalg.det(R) == 1) 
        T = numpy.array([[0, 0, -vertical_offset_cm -self.marker_size_cm/2]]).T
        #print(pose)
        return {"R": numpy.matmul(R, pose["R"]),
                "T": numpy.matmul(R, pose["T"])+T}
    


if __name__ == "__main__":
    c = Calibration()
    c.load("calibration.json")
    print("{}\n{}\n{}".format(c.valid(), c.cameraMatrix(), c.distortion()))
    
