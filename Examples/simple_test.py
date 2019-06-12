

from atm90e32_u import ATM90e32


# ***** CALIBRATION SETTINGS *****/
linefreq = 4485  # 4485 for 60 Hz (North America)
# 389 for 50 hz (rest of the world)
pgagain = 21  # 21 for 100A (2x), 42 for >100A (4x)

ugain = 42080  # 42080 - 9v AC transformer.
# 32428 - 12v AC Transformer

igainA = 25498  # 38695 - SCT-016 120A/40mA
igainC = 25498  # 25498 - SCT-013-000 100A/50mA
# 46539 - Magnalab 100A w/ built in burden resistor

energy_sensor = ATM90e32(linefreq, pgagain, ugain, igainA, 0, igainC)
sys0 = energy_sensor.sys_status0
print('Sys status:  S0:{:#04x}   S1:{:#04x}'.format(
    sys0, energy_sensor.sys_status1))
print('meter status E0: {:#04x} S1:{:#04x}'.format(
    energy_sensor.meter_status0, energy_sensor.meter_status1))
print('Last SPI read: {:#04x}'.format(energy_sensor.lastSpiData))
if (sys0 == 0xFFFF or sys0 == 0):
    print('ERROR: not receiving data from the energy meter')
    exit(0)
voltageA = energy_sensor.line_voltageA
voltageC = energy_sensor.line_voltageC
if (linefreq == 4485):  # split single phase
    totalVoltage = voltageA + voltageC
else:
    totalVoltage = voltageA  # 220-240v
print('Voltage 1: {}V'.format(voltageA))
print('Voltage 2: {}V'.format(voltageC))
print('Current 1: {}A'.format(energy_sensor.line_currentA))
print('Current 2: {}A'.format(energy_sensor.line_currentC))
print('Frequency: {}Hz'.format(energy_sensor.frequency))
print('Active Power: {}W'.format(energy_sensor.active_power))



