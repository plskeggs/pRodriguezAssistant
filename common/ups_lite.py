import struct
import smbus
import RPi.GPIO as GPIO

bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
I2C_ADDRESS = 0x36
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.IN)

def power_on_reset():
    try:
        bus.write_word_data(I2C_ADDRESS, 0xfe, 0x0054)
    except OSError:
        print("no UPS!")
        pass

def quick_start():
    try:
        bus.write_word_data(I2C_ADDRESS, 0x06, 0x4000)
    except OSError:
        print("no UPS!")
        pass

def read_voltage():
    try:
        raw_value = bus.read_word_data(I2C_ADDRESS, 2)
        swapped = struct.unpack("<H", struct.pack(">H", raw_value))[0]
        voltage = swapped * 1.25 / 1000 / 16
    except OSError:
        voltage = 3.3
        pass
    return voltage

def read_capacity():
    try:
        raw_value = bus.read_word_data(I2C_ADDRESS, 4)
        swapped = struct.unpack("<H", struct.pack(">H", raw_value))[0]
        capacity = swapped / 256
    except OSError:
        capacity = 100
        pass
    return capacity

def adapter_in():
    try:
        return (GPIO.input(4) == GPIO.HIGH)
    except:
        return False
