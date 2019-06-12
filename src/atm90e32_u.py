
from machine import Pin, SPI
import math
import time
import struct
from atm90e32_registers import *

SPI_WRITE = 0
SPI_READ = 1

class ATM90e32:
    ##############################################################################

    def __init__(self, linefreq, pgagain, ugain, igainA, igainB, igainC):
        self._linefreq = linefreq
        self._pgagain = pgagain
        self._ugain = ugain
        self._igainA = igainA
        self._igainB = igainB
        self._igainC = igainC

        # Chip select pin
        self.cs = Pin(15, Pin.OUT)
        self.cs.on()
        # Doc on esp8266 SPI hw init: http://bit.ly/2ZhqeRB
        self.spi = SPI(1, baudrate=200000, polarity=1, phase=1)

        self._init_config()

    def _init_config(self):
        # CurrentGainCT2 = 25498  #25498 - SCT-013-000 100A/50mA
        if (self._linefreq == 4485 or self._linefreq == 5231):
            # North America power frequency
            FreqHiThresh = 61 * 100
            FreqLoThresh = 59 * 100
            sagV = 90
        else:
            FreqHiThresh = 51 * 100
            FreqLoThresh = 49 * 100
            sagV = 190

        # calculation for voltage sag threshold - assumes we do not want to go under 90v for split phase and 190v otherwise
        # sqrt(2) = 1.41421356
        fvSagTh = (sagV * 100 * 1.41421356) / (2 * self._ugain / 32768)
        # convert to int for sending to the atm90e32.
        vSagTh = self._round_number(fvSagTh)

        self._spi_rw(SPI_WRITE, SoftReset, 0x789A)   # Perform soft reset
        # enable register config access
        self._spi_rw(SPI_WRITE, CfgRegAccEn, 0x55AA)
        self._spi_rw(SPI_WRITE, MeterEn, 0x0001)   # Enable Metering

        self._spi_rw(SPI_WRITE, SagTh, vSagTh)         # Voltage sag threshold
        # High frequency threshold - 61.00Hz
        self._spi_rw(SPI_WRITE, FreqHiTh, FreqHiThresh)
        # Lo frequency threshold - 59.00Hz
        self._spi_rw(SPI_WRITE, FreqLoTh, FreqLoThresh)
        self._spi_rw(SPI_WRITE, EMMIntEn0, 0xB76F)   # Enable interrupts
        self._spi_rw(SPI_WRITE, EMMIntEn1, 0xDDFD)   # Enable interrupts
        self._spi_rw(SPI_WRITE, EMMIntState0, 0x0001)  # Clear interrupt flags
        self._spi_rw(SPI_WRITE, EMMIntState1, 0x0001)  # Clear interrupt flags
        # ZX2, ZX1, ZX0 pin config
        self._spi_rw(SPI_WRITE, ZXConfig, 0x0A55)

        # Set metering config values (CONFIG)
        # PL Constant MSB (default) - Meter Constant = 3200 - PL Constant = 140625000
        self._spi_rw(SPI_WRITE, PLconstH, 0x0861)
        # PL Constant LSB (default) - this is 4C68 in the application note, which is incorrect
        self._spi_rw(SPI_WRITE, PLconstL, 0xC468)
        # Mode Config (frequency set in main program)
        self._spi_rw(SPI_WRITE, MMode0, self._linefreq)
        # PGA Gain Configuration for Current Channels - 0x002A (x4) # 0x0015 (x2) # 0x0000 (1x)
        self._spi_rw(SPI_WRITE, MMode1, self._pgagain)
        # Active Startup Power Threshold - 50% of startup current = 0.9/0.00032 = 2812.5
        self._spi_rw(SPI_WRITE, PStartTh, 0x0AFC)
        # Reactive Startup Power Threshold
        self._spi_rw(SPI_WRITE, QStartTh, 0x0AEC)
        # Apparent Startup Power Threshold
        self._spi_rw(SPI_WRITE, SStartTh, 0x0000)
        # Active Phase Threshold = 10% of startup current = 0.06/0.00032 = 187.5
        self._spi_rw(SPI_WRITE, PPhaseTh, 0x00BC)
        self._spi_rw(SPI_WRITE, QPhaseTh, 0x0000)    # Reactive Phase Threshold
        # Apparent  Phase Threshold
        self._spi_rw(SPI_WRITE, SPhaseTh, 0x0000)

        # Set metering calibration values (CALIBRATION)
        self._spi_rw(SPI_WRITE, PQGainA, 0x0000)     # Line calibration gain
        self._spi_rw(SPI_WRITE, PhiA, 0x0000)        # Line calibration angle
        self._spi_rw(SPI_WRITE, PQGainB, 0x0000)     # Line calibration gain
        self._spi_rw(SPI_WRITE, PhiB, 0x0000)        # Line calibration angle
        self._spi_rw(SPI_WRITE, PQGainC, 0x0000)     # Line calibration gain
        self._spi_rw(SPI_WRITE, PhiC, 0x0000)        # Line calibration angle
        # A line active power offset
        self._spi_rw(SPI_WRITE, PoffsetA, 0x0000)
        # A line reactive power offset
        self._spi_rw(SPI_WRITE, QoffsetA, 0x0000)
        # B line active power offset
        self._spi_rw(SPI_WRITE, PoffsetB, 0x0000)
        # B line reactive power offset
        self._spi_rw(SPI_WRITE, QoffsetB, 0x0000)
        # C line active power offset
        self._spi_rw(SPI_WRITE, PoffsetC, 0x0000)
        # C line reactive power offset
        self._spi_rw(SPI_WRITE, QoffsetC, 0x0000)

        # Set metering calibration values (HARMONIC)
        # A Fund. active power offset
        self._spi_rw(SPI_WRITE, POffsetAF, 0x0000)
        # B Fund. active power offset
        self._spi_rw(SPI_WRITE, POffsetBF, 0x0000)
        # C Fund. active power offset
        self._spi_rw(SPI_WRITE, POffsetCF, 0x0000)
        # A Fund. active power gain
        self._spi_rw(SPI_WRITE, PGainAF, 0x0000)
        # B Fund. active power gain
        self._spi_rw(SPI_WRITE, PGainBF, 0x0000)
        # C Fund. active power gain
        self._spi_rw(SPI_WRITE, PGainCF, 0x0000)

        # Set measurement calibration values (ADJUST)
        self._spi_rw(SPI_WRITE, UgainA, self._ugain)      # A Voltage rms gain
        # A line current gain
        self._spi_rw(SPI_WRITE, IgainA, self._igainA)
        self._spi_rw(SPI_WRITE, UoffsetA, 0x0000)    # A Voltage offset
        self._spi_rw(SPI_WRITE, IoffsetA, 0x0000)    # A line current offset
        self._spi_rw(SPI_WRITE, UgainB, self._ugain)      # B Voltage rms gain
        # B line current gain
        self._spi_rw(SPI_WRITE, IgainB, self._igainB)
        self._spi_rw(SPI_WRITE, UoffsetB, 0x0000)    # B Voltage offset
        self._spi_rw(SPI_WRITE, IoffsetB, 0x0000)    # B line current offset
        self._spi_rw(SPI_WRITE, UgainC, self._ugain)      # C Voltage rms gain
        # C line current gain
        self._spi_rw(SPI_WRITE, IgainC, self._igainC)
        self._spi_rw(SPI_WRITE, UoffsetC, 0x0000)    # C Voltage offset
        self._spi_rw(SPI_WRITE, IoffsetC, 0x0000)    # C line current offset

        self._spi_rw(SPI_WRITE, CfgRegAccEn, 0x0000)  # end configuration
    #####################################################################################
    @property
    def lastSpiData(self):
        reading = self._spi_rw(SPI_READ, LastSPIData, 0xFFFF)
        return reading
    #####################################################################################
    @property
    def sys_status0(self):
        reading = self._spi_rw(SPI_READ, EMMIntState0, 0xFFFF)
        return reading
    #####################################################################################
    @property
    def sys_status1(self):
        reading = self._spi_rw(SPI_READ, EMMIntState1, 0xFFFF)
        return reading
     #####################################################################################

    @property
    def meter_status0(self):
        reading = self._spi_rw(SPI_READ, EMMState0, 0xFFFF)
        return reading
    #####################################################################################
    @property
    def meter_status1(self):
        reading = self._spi_rw(SPI_READ, EMMState1, 0xFFFF)
        return reading
    #####################################################################################
    @property
    def line_voltageA(self):
        reading = self._spi_rw(SPI_READ, UrmsA, 0xFFFF)
        return reading / 100.0
    #####################################################################################
    @property
    def line_voltageB(self):
        reading = self._spi_rw(SPI_READ, UrmsB, 0xFFFF)
        return reading / 100.0
    #####################################################################################
    @property
    def line_voltageC(self):
        reading = self._spi_rw(SPI_READ, UrmsC, 0xFFFF)
        return reading / 100.0
    #####################################################################################
    @property
    def line_currentA(self):
        reading = self._spi_rw(SPI_READ, IrmsA, 0xFFFF)
        return reading / 1000.0
    #####################################################################################
    @property
    def line_currentC(self):
        reading = self._spi_rw(SPI_READ, IrmsC, 0xFFFF)
        return reading / 1000.0
    #####################################################################################
    @property
    def frequency(self):
        reading = self._spi_rw(SPI_READ, Freq, 0xFFFF)
        return reading / 100.0
    #####################################################################################
    @property
    def active_power(self):
        reading = self._read32Register(PmeanT, PmeanTLSB)
        return reading * 0.00032
    #####################################################################################
    # do the SPI read or write request.
    #####################################################################################
    def _spi_rw(self, rw, address, val):

        # Set read/write flag
        address |= rw << 15
        # Enable SPI and wait for SPI to activate
        self.cs.off()
        time.sleep_us(10)
        # pack the address into a the bytearray.  It is an unsigned short(H) that needs to be in MSB(>)
        two_byte_buf = struct.pack('>H', address)
        # send address
        self.spi.write(two_byte_buf)
        # wait for data to become valid (4uS) - see http://bit.ly/2Zh6VI9
        time.sleep_us(4)
        if(rw):  # read
            # Get the unsigned short register values sent from the atm90e32
            results_buf = self.spi.read(2)
            result = struct.unpack('>H', results_buf)[0]
        else:
            # pack the address into a the bytearray.  It is an unsigned short(H) that needs to be in MSB(>)
            two_byte_buf = struct.pack('>H', val)
            self.spi.write(two_byte_buf)
            result = 0
        # Put cs back to HIGH - SPI bytes have been written/read.
        self.cs.on()
        return result

    ###################################################################################

    def _round_number(self, f_num):
        if f_num - math.floor(f_num) < 0.5:
            return math.floor(f_num)
        return math.ceil(f_num)

    ###################################################################################
    def _read32Register(self, regh_addr, regl_addr):
        val_h = self._spi_rw(SPI_READ, regh_addr, 0xFFFF)
        val_l = self._spi_rw(SPI_READ, regl_addr, 0xFFFF)
        val = val_h << 16
        val |= val_l  # concatenate the 2 registers to make 1 32 bit number
        # flip the bits...different than Arduino...
        val = val ^ 0xffffffff
        return (val)
