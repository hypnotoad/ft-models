#!/usr/bin/python3

# originally from https://forum.ftcommunity.de/viewtopic.php?f=8&t=8046#p64119

import smbus

class Gestensensor:
    def __init__(self, bus_id, address = 0x39):
        self.bus = smbus.SMBus(bus_id)
        self.address = address

        #0x80 Aktivierungsregister, Sensor einschalten, Funktionen aktivieren
        self.bus.write_byte_data(self.address, 0x80, 0x07)

        #0x8F Steuerregister 1 Funktionsparameter des ICs einstellen.
        #0/1 Verst????rkung Farb- und Lichtsensor (00=1x, 01=4x, 10=16x, 11=64x)
        #2/3 Verst????rkung Ann????herungssensor (00=1x, 01=2x, 10=4x, 11=8x)
        #4/5 reserviert
        #6/7 Stromst????rke LED (00=100mA, 01=50mA, 10=25mA, 11=12,5mA)

        self.bus.write_byte_data(self.address, 0x8f, 0x0f)


    def proximity(self):
        return self.bus.read_byte_data(self.address, 0x9c)


    def crgb(self):
        # c is unfiltered total brightness without a filter
        # returns 16 bit crgb values
        cl = self.bus.read_byte_data(self.address, 0x94)
        ch = self.bus.read_byte_data(self.address, 0x95)
        rl = self.bus.read_byte_data(self.address, 0x96)
        rh = self.bus.read_byte_data(self.address, 0x97)
        gl = self.bus.read_byte_data(self.address, 0x98)
        gh = self.bus.read_byte_data(self.address, 0x99)
        bl = self.bus.read_byte_data(self.address, 0x9a)
        bh = self.bus.read_byte_data(self.address, 0x9b)
        # max value is 1025
        crgb = [cl + (ch << 8), rl + (rh << 8), gl + (gh << 8), bl + (bh<<8)]
        return [x / 1025 for x in crgb]

    def crgbToHsv(self, crgb):
        import colorsys
        return colorsys.rgb_to_hsv(crgb[1], crgb[2], crgb[3])

    def hueDiff(self, hsv1, hsv2):
        h1 = hsv1[0]
        h2 = hsv2[0]
        assert(h1 <= 1)
        assert(h2 <= 1)
        assert(h1 >= 0)
        assert(h2 >= 0)

        d = abs(h1-h2)
        if d > 0.5:
            d = 1-d
        return d*2


if __name__ == '__main__':
    import time
    g = Gestensensor(1)
    red = g.crgbToHsv([1, 1, 0, 0])
    blue = g.crgbToHsv([1, 0, 0, 1])
    print("red: %s, blue: %s" % (red, blue))
    while True:
        p = g.proximity()
        crgb = g.crgb()
        hsv = g.crgbToHsv(crgb)
        color = "red" if g.hueDiff(red, hsv) < g.hueDiff(blue, hsv) else "blue"
        print("%s - proximity: % 3d, crgb: %s hsv: %s" % (color, p, crgb, hsv))
        time.sleep(1)
    
