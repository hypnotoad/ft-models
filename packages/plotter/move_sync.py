def sign(x):
  if x >= 0:
    return 1
  else:
    return -1

def move_sync(txt, m1, m2, s1, s2, sn1=6, sn2=5):
    s1 = int(round(s1))
    s2 = int(round(s2))
    # sn1 = 4 + motornummer von m2
    # sn2 = 4 + motornummer von m1

    if abs(s1) > abs(s2):
        #print("flipping")
        n = move_sync(txt, m2, m1, s2, s1, sn2, sn1)
        return [n[1], n[0]]

    inject_delta = 3
    goal_m1 = abs(s1)
    goal_m2 = abs(s2)
    speed = 512

    #print("move_sync(%s, %s)" % (s1, s2))
    m1.setDistance(0, sn=sn1) # there is a counter reset if we change sn. m1 has sn1 and m2 hasn't
    txt.updateWait()
    m2.setDistance(goal_m2)
    txt.updateWait()
    
    m1_speed_magnitude = max([150, round(speed/goal_m2*goal_m1)])
    m1.setSpeed(sign(s1)*m1_speed_magnitude)
    m2.setSpeed(sign(s2)*speed)
    txt.updateWait()

    inject = 0
    sz1 = 0
    sz2 = 0
    prev_c1 = 0
    prev_c2 = 0
    while True:
        action=""
        txt.updateWait()
        c1 = m1.getCurrentDistance()
        c2 = m2.getCurrentDistance()
        if c2 >= goal_m2:
            break

        if prev_c1 > c1:
            print("COUNTER RESET DETECTED (prev %d, curr %d)" % (prev_c1, c1))

        dc = inject_delta
        #next_c1 = c1 + dc / goal_m2 * goal_m1
        next_c1 = c1 + (c1 - prev_c1)
        next_c2 = c2 + (c2 - prev_c2)
        togo_c1 = goal_m1 - c1
        togo_c2 = goal_m2 - c2
        
        #diff  = c1 - c2/goal_m2*goal_m1
        soll_c1 = c2 / goal_m2*goal_m1
        soll_next_c1 = next_c2 / goal_m2*goal_m1
        if togo_c1 < c1:
            action += "limiting, "
            soll_next_c1 = goal_m1 - max([0, togo_c2/goal_m2*goal_m1])
        diff = next_c1 - soll_next_c1
        #diff = c1 - soll_c1
        #print("ist %.1f - soll %.1f = diff %.1f)" % (c1, soll_c1, diff))

        # the correction is in the c2 domain
        correction = round(diff / goal_m1 * goal_m2)

        if c1 >= goal_m1:
            m1.setSpeed(0)
            
        if True or c2 >= inject:
            if correction > 0:
                sz1 = c1-correction-c2 + sz2
                m1.setDistance(correction, sn=sn1)
                txt.updateWait()
                action += "inject, "
            elif correction < 0:
#               sz2 = c1+correction-c1 + sz1
#               m1.setDistance(correction, sn=sn1)
#               txt.updateWait()
                action += "negative correction, "
            inject = next_c2

        err = c1 - sz1 - c2 -sz2
        #print("%d - %d == %d - %d (%d => %d) %s" % (c1, sz1, c2, sz2,  err, correction, action))

        prev_c1 = c1
        prev_c2 = c2



    m1.setSpeed(0)
    m2.setSpeed(0)
    #m1.stop()
    #m2.stop()
    txt.updateWait(0.05)
    c1 = m1.getCurrentDistance()
    c2 = m2.getCurrentDistance()

    txt.incrCounterCmdId(0)
    txt.incrCounterCmdId(1)
    txt.updateWait()

    return [c1*sign(s1), c2*sign(s2)]


if __name__ == "__main__":
    import ftrobopy
    txt=ftrobopy.ftrobopy('auto', use_TransferAreaMode=True)
    txt.updateWait()

    print("big")
    print(move_sync(txt, txt.motor(1), txt.motor(2), -1190, 1790, 6, 5))
    print(move_sync(txt, txt.motor(1), txt.motor(2), 1190, -1790, 6, 5))
    
    print("small")
    print(move_sync(txt, txt.motor(1), txt.motor(2), 7.0, 16.0, 6, 5))
    print(move_sync(txt, txt.motor(1), txt.motor(2), -7, -16, 6, 5))
    print(move_sync(txt, txt.motor(1), txt.motor(2), 7, -16, 6, 5))
    print(move_sync(txt, txt.motor(1), txt.motor(2), -7.0, 16, 6, 5))
    exit(0)

    print("4 cases")
    print(move_sync(txt, txt.motor(1), txt.motor(2), 100, 50, 6, 5))
    print(move_sync(txt, txt.motor(1), txt.motor(2), 50, 100, 6, 5))
    print(move_sync(txt, txt.motor(1), txt.motor(2), -100, 50, 6, 5))
    print(move_sync(txt, txt.motor(1), txt.motor(2), -50, 100, 6, 5))

    for pos_abs in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        print(move_sync(txt, txt.motor(1), txt.motor(2), pos_abs, 100, 6, 5))
        print(move_sync(txt, txt.motor(1), txt.motor(2), -pos_abs, 100, 6, 5))

    exit(0)
    for pos_abs in [1, 2, 3, 5, 7, 10, 20, 50, 100]:
        for i in range(3):
            rel = pos_abs - curr_pos 
            curr_pos += move_rel(txt, m1, rel)
            rel = 0 - curr_pos 
            curr_pos += move_rel(txt, m1, rel)
            print("abs: %d" % curr_pos)
