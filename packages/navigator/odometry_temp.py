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
            self.max_duration = 2

            # calibrated empirical at 300:
            self.distances_per_second = (10, None, 25)
            self.thresholds = (5, 5, 3)

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

            measurements = (angle_dist["dist_cm"], 0, angle_dist["hori_angle"])
            targets = (100, 0, 0)

            duration = self.min_duration
            move = numpy.array([[0, 0, 0]]) #fwd, right, turn
            for idx in range(3):

                offset = targets[idx] - measurements[idx]
                factor = abs(offset) / self.thresholds[idx]
                if factor > 1:
                    move[0][idx] = 1 if offset < 0 else -1
                    computed_duration = abs(offset) / self.distances_per_second[idx]
                    duration = min(computed_duration/2, self.max_duration)
                    # print("Adding component {}".format(motion_component))
                    break

            dist = move.dot(self.motions)
            return (dist, duration)



if __name__ == "__main__":
    import time
    txt = ftrobopy.ftrobopy()

    odo = OdometryTemp(txt)

    def create_input(dist, angle):
        return {"hori_angle": angle, "dist_cm": dist}

    distances = [(110, 0), (90, 0), (100, 45), (100, -45)]

    for distance in distances:
        angle_dist = create_input(distance[0], distance[1])
        dist, duration = odo.compute_speeds_and_duration(angle_dist)
        print("{} for {}s".format(dist, duration))

        odo.set_motors(dist)
        time.sleep(duration)
        odo.set_motors(None)

    time.sleep(1)
