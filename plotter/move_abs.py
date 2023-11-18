def sign(x):
  if x >= 0:
    return 1
  else:
    return -1

def move_rel(txt, m1, rel, speed = 512):
    steps = abs(rel)
    m1.setDistance(steps)
    m1.setSpeed(sign(rel)*speed)
    #print("setDistance(%d)" % steps)
    #print("setSpeed(%d)" % (sign(rel)*speed))

    while True:
        txt.updateWait()
        dist = m1.getCurrentDistance()
    #    print(". %d" % dist)
        if dist >= steps:
        #if m1.finished():
            print("done: %d/%d" % (dist, rel))
            #print("isfinished(%s)" % m1.finished())
            break

    # regular: 10ms are not enough
    txt.updateWait(0.01)
    x1 = m1.getCurrentDistance() * sign(rel)
    # additional
    for i in range(10):
        txt.updateWait(0.01)
        x2 = m1.getCurrentDistance() * sign(rel)
        #print("> %d" % x2)
        if x1 != x2:
            print("LATE MOVEMENT: %d vs %d" % (x1, x2))
        # SOMETIMES, x1 or x2 are 0!
    m1.stop()
    txt.updateWait()
    return x2



if __name__ == "__main__":
    import plotter
    curr_pos = 0
    p = plotter.Plotter("localhost", False)
    txt = p.txt
    m1 = p.mx
    for pos_abs in [1, 2, 3, 5, 7, 10, 20, 50, 100]:
        for i in range(3):
            rel = pos_abs - curr_pos 
            curr_pos += move_rel(txt, m1, rel)
            rel = 0 - curr_pos 
            curr_pos += move_rel(txt, m1, rel)
            print("abs: %d" % curr_pos)
            
