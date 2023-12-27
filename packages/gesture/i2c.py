#!/usr/bin/env python3

import ftrobopy

class APDS9960:

    # Register addresses
    REG_ENABLE  = 0x80
    REG_ATIME   = 0x81
    REG_WTIME   = 0x83
    REG_AILTL   = 0x84
    REG_AILTH   = 0x85
    REG_AIHTL   = 0x86
    REG_AIHTH   = 0x87
    REG_PILT    = 0x89
    REG_PIHT    = 0x8B
    REG_PERS    = 0x8C
    REG_CONFIG1 = 0x8D
    REG_PPULSE  = 0x8E
    REG_CONTROL = 0x8F
    REG_CONFIG2 = 0x90
    REG_ID      = 0x92
    REG_STATUS  = 0x93
    REG_CDATAL  = 0x94
    REG_CDATAH  = 0x95
    REG_RDATAL  = 0x96
    REG_RDATAH  = 0x97
    REG_GDATAL  = 0x98
    REG_GDATAH  = 0x99
    REG_BDATAL  = 0x9A
    REG_BDATAH  = 0x9B
    REG_PDATA   = 0x9C
    REG_POFFSET_UR  = 0x9D
    REG_POFFSET_DL  = 0x9E
    REG_CONFIG3 = 0x9F
    REG_GPENTH  = 0xA0
    REG_GEXTH   = 0xA1
    REG_GCONF1  = 0xA2
    REG_GCONF2  = 0xA3
    REG_GOFFSET_U   = 0xA4
    REG_GOFFSET_D   = 0xA5
    REG_GOFFSET_L   = 0xA7
    REG_GOFFSET_R   = 0xA9
    REG_GPULSE  = 0xA6
    REG_GCONF3  = 0xAA
    REG_GCONF4  = 0xAB
    REG_GFLVL   = 0xAE
    REG_GSTATUS = 0xAF
    REG_IFORCE  = 0xE4
    REG_PICLEAR = 0xE5
    REG_CICLEAR = 0xE6
    REG_AICLEAR = 0xE7
    REG_GFIFO_U = 0xFC
    REG_GFIFO_D = 0xFD
    REG_GFIFO_L = 0xFE
    REG_GFIFO_R = 0xFF

    # Enable register bits
    ENABLE_GEN  = 0b01000000    # Gesture enable
    ENABLE_PIEN = 0b00100000    # Proximity Interrupt Enable
    ENABLE_AIEN = 0b00010000    # ALS Interrupt Enable
    ENABLE_WEN  = 0b00001000    # Wait Enable
    ENABLE_PEN  = 0b00000100    # Proximity Enable
    ENABLE_AEN  = 0b00000010    # ALS Enable
    ENABLE_PON  = 0b00000001    # Power ON

    # Congiguration register 2
    CONFIG2_LEDBOOST_150 = (1 << 4) # LED boost 150%
    CONFIG2_LEDBOOST_200 = (2 << 4) # LED boost 300%
    CONFIG2_LEDBOOST_300 = (3 << 4) # LED boost 300%

    GCONFIG3_GDIMS_LR = 2
    GCONFIG3_GDIMS_UD = 1 # 01
    GCONFIG4_GMODE = 1 # Gesture mode

    def __init__(self, i2c_addr = 0x39):
        self.i2c_addr = i2c_addr
        self.debug = True
        self.txt = ftrobopy.ftrobopy('txt4.lan')

    def _write(self, register, data8):
        self.txt.i2c_write(self.i2c_addr, register, data8, debug=self.debug)

    def _read(self, register):
        self.txt.i2c_read(self.i2c_addr, register, debug=self.debug)

    def initialize(self):
        if (self.get_device_id() != 0xAB):
            return False
        self._write(self.REG_ENABLE,
            self.ENABLE_PON | self.ENABLE_PEN | self.ENABLE_GEN)
        self._write(self.REG_CONFIG2,
            self.CONFIG2_LEDBOOST_300)
        self._write(self.REG_GOFFSET_U, 70)
        self._write(self.REG_GOFFSET_D, 0)
        self._write(self.REG_GOFFSET_L, 10)
        self._write(self.REG_GOFFSET_R, 34)
        self._write(self.REG_CONFIG3,
            self.GCONFIG3_GDIMS_UD | self.GCONFIG3_GDIMS_LR)
        self._write(self.REG_GCONFIG4, GCONFIG4_GMODE)

    def get_device_id(self):
        return self._read(self.REG_ID)

    def gesture(self):
        level = self._read(self.REG_GFLVL)
        if (level == 0):
            return # no data
        self.fifo_u = self._read(self.REG_GFIFO_U)
        self.fifo_d = self._read(self.REG_GFIFO_D)
        self.fifo_l = self._read(self.REG_GFIFO_L)
        self.fifo_r = self._read(self.REG_GFIFO_R)

if __name__ == '__main__':
    sensor = APDS9960()
    print("device ID: {}".format(sensor.get_device_id()))
    sensor.initialize()
    while True:
        sensor.gesture()
        print(sensor.fifo_u)

