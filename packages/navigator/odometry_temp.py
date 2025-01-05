import ftrobopy
import numpy

class OdometryTemp:

        def __init__(self, txt):
            self.txt = txt
            self.motors = [txt.motor(i) for i in range(1,5)]
            # fwd, right, turn to the four motors
            self.motions = numpy.array([[ 1,  1,  1,  1 ],
                                        [ 1, -1, -1,  1 ],
                                        [ 1, -1,  1, -1 ]])

            self.speed = 300
            self.min_duration = 0.2
            self.max_duration = 1

            # calibrated empirical at 300:
            self.distances_per_second = (10, None, 12.5)
            self.thresholds = (5, None, 3)

        def set_motors(self, dist):
            if dist is None:
                dist = numpy.array([[0, 0, 0, 0]])
            assert(dist.shape[0] == 1)
            
            self.txt.SyncDataBegin()
            for i in range(len(self.motors)):
                s = max(-512, min(512, int(self.speed*dist[0][i])))
                self.motors[i].setSpeed(s)
            self.txt.SyncDataEnd()

        def compute_speeds_and_duration(self, angle_dist):
            def add_component(measurement, target, index):
                retval = numpy.array([[0, 0,  0]])
                offset = target - measurement
                if abs(offset) > self.thresholds[index]:
                    retval[0][index] = 1 if offset < 0 else -1
                return retval

            move = numpy.array([[0, 0, 0]]) #fwd, right, turn
            move += add_component(angle_dist["hori_angle"], target=0, index=2)
            move += add_component(angle_dist["dist_cm"], target=100, index=0)

            dist = move.dot(self.motions)
            duration = self.min_duration
            return (dist, duration)



if __name__ == "__main__":
    import time
    txt = ftrobopy.ftrobopy()

    odo = OdometryTemp(txt)

    def create_input(dist, angle):
        return {"hori_angle": angle, "dist_cm": dist}

    angle_dist = create_input(110, 0) # 10 forwards
    dist, duration = odo.compute_speeds_and_duration(angle_dist)
    print("{} for {}s".format(dist, duration))

    odo.set_motors(dist)
    time.sleep(duration)
    odo.set_motors(None)

    time.sleep(1)
