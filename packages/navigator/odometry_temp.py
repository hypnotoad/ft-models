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
            move = numpy.array([[0, 0, 0]]) #fwd, right, turn
            duration = self.max_duration

            def add_component(measurement, target, index):
                nonlocal move, duration
                
                motion_component = numpy.array([[0, 0,  0]])
                offset = target - measurement
                factor = abs(offset) / self.thresholds[index]
                if factor > 1:
                    motion_component[0][index] = 1 if offset < 0 else -1
                    computed_duration = abs(offset) / self.distances_per_second[index]
                    duration = min([self.max_duration, computed_duration/2, duration])
                move += motion_component

            add_component(angle_dist["hori_angle"], target=0, index=2)
            add_component(angle_dist["dist_cm"], target=100, index=0)

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
