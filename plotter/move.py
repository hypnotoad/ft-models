import time

def speed(c1, cc, c2, dc):
    assert(c1 < c2)

    s_min_acc = 150
    s_min_dec = 100
    s_max = 500
    thresh_acc = 10 
    thresh_dec = 50

    if c1 == cc:#dc == 0:
        return s_min_acc
    if c2 == cc:
        return 0

    f_acc = s_max - s_min_acc
    f_dec = s_max - s_min_dec
    accel = (cc-c1) / thresh_acc
    decel = (c2-cc) / thresh_dec
    vals = [s_min_acc+accel*f_acc, s_min_dec+decel*f_dec, s_max]
    #print(vals)
    return int(min(vals))
    
def calib(txt):
    m1 = txt.motor(1)

    speeds=range(10, 100, 10)
    speeds=[10, 50, 100, 150, 200, 250, 300, 400, 500]

    for speed in speeds:
        txt.incrCounterCmdId(0) # needs to wait some time after that
        txt.updateWait()
        txt.updateWait()
        
        c1 = m1.getCurrentDistance()
        m1.setSpeed(speed)
        for i in range(100):
            txt.updateWait()
            c2 = m1.getCurrentDistance()
            if c1 != c2:
                print("%d: moved %d->%d after %d cycles" % (speed, c1, c2, i))
                break
        m1.setSpeed(0)
        time.sleep(1)

if __name__ == "__main__":
    import ftrobopy
    txt=ftrobopy.ftrobopy('auto', use_TransferAreaMode=True)
    txt.updateWait()
    m1 = txt.motor(1)

    distances=[1, 2, 3, 10, 50, 100, 200]

    for dist in distances:
        txt.incrCounterCmdId(0) # needs to wait some time after that
        txt.updateWait()
        txt.updateWait()
        
        c1 = m1.getCurrentDistance()
        assert(c1 == 0)
        c2 = c1
        direction = -1
        
        for i in range(1000):
            txt.updateWait()
            c2_new = m1.getCurrentDistance()
            dc = c2_new - c2
            c2 = c2_new
            s = speed(c1, c2, c1+dist, dc)
            #print("%d - %d" % (c2, s))
            m1.setSpeed(direction*s)
            if c2-c1 >= dist:
                print("moved %d (%d) after %d cycles" % (c2-c1, dist, i))
                break
        #m1.setSpeed(-direction*100) 
        txt.updateWait(0.1)
        c2 = m1.getCurrentDistance()
        m1.setSpeed(0)
        txt.updateWait()

        time.sleep(1)
        txt.updateWait()
        c3 = m1.getCurrentDistance()
        
        if c3-c2 > 0:
           print("%d: overshoot %d (%d)" % (s, c3, c2))
        if c2-c1 < dist:
           print("%d: target not reched %d (%d)" % (s, c2, c1))
