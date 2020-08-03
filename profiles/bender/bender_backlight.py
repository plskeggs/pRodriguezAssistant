# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import board
import neopixel
import time
import math
from multiprocessing import Process

#parameters list: pin, count, brightness
#GPIO10, GPIO12, GPIO18 or GPIO21
eyes_pin = board.D10
mouth_pin = board.D12
eyes_leds = (eyes_pin, 1, 1) # two eyes in parallel
mouth_leds = (mouth_pin, 18, 0.5)

strips = {
    # 'EYES': eyes_leds,
    'MOUTH': mouth_leds
}

pin = None
pixels = None

ORDER = neopixel.GRB

default_color = (243, 253, 0)
no_color = (0, 0, 0)
orange = (255,165,0)
darkorange = (255,140,0)
blue = (0,0,255)
revert_row1 = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0}

is_talking = False

def fill_pixels(pixels, color):
    pixels.fill(color)
    pixels.show()

def blink(pixels, pin, mode):
    global eyes_pin
    if pin != eyes_pin:
        print('Teeth do not support talk command!')
        return

    if mode == 'plugged_in':
        phase_1_color = darkorange
        phase_2_color = blue
        period = 0.1
    else:
        back_color = no_color
        front_color = default_color
        period = 0.25

    t = 0
    while t < 30:  # maximum answer length to prevent infinite loop
        pixels.fill(phase_1_color)
        pixels.show()
        time.sleep(period)
        pixels.fill(phase_2_color)
        pixels.show()
        time.sleep(period)
    t += period * 4

def talk(pixels, pin, mode):
    global mouth_pin
    if pin != mouth_pin:
        print('Eyes do not support talk command!')
        return

    if mode == 'plugged_in':
        back_color = darkorange
        front_color = blue
        period = 0.1
    else:
        back_color = no_color
        front_color = default_color
        period = 0.25

    t = 0
    while t < 30: # maximum answer length to prevent infinite loop
        pixels.fill(back_color)
        for i in range(6, 12):
            pixels[i] = front_color
        pixels.show()
        time.sleep(period)

        sin_cos_graph(pixels, pin, math.cos, back_color, front_color)
        time.sleep(period)

        pixels.fill(back_color)
        for i in range(6, 12):
            pixels[i] = front_color
        pixels.show()
        time.sleep(period)

        sin_cos_graph(pixels, pin, math.sin, back_color, front_color)
        time.sleep(period)
        t += period * 4

def sin_cos_graph(pixels, pin, func, back_color, front_color):
    global mouth_pin
    if pin != mouth_pin:
        print('Eyes do not support talk command!')
        return
    if func != math.sin and func != math.cos:
        print('Only sin() and cos() are supported!')
        return
    pixels.fill(back_color)
    t = 0
    for x in range(0, 6):
        y = func(t)
        j = x
        if y >= -1 and y < -0.33:
            i = 0
        elif y >= -0.33 and y < 0.33:
            i = 1
            j = revert_row1[x]
        else:
            i = 2
        c = i * 6 + j
        pixels[c] = front_color
        t += 1.57
    pixels.show()

class BacklightControl:
    def __init__(self, strip):
        self.pixels = None
        if strip in strips:
            self.__init_pixels(strips[strip])
        else:
            print("Strip not found!")
        self.backlight_commands = {
            'ON': lambda: fill_pixels(self.pixels, default_color),
            'OFF': lambda: fill_pixels(self.pixels, no_color),
            'TALK': lambda: talk(self.pixels, self.pin, 'normal'),
            'PLUGGED_IN': lambda: talk(self.pixels, self.pin, 'plugged_in'),
            'BLINK_NORMAL': lambda: blink(self.pixels, self.pin, 'normal'),
            'BLINK_PLUGGED_IN': lambda: blink(self.pixels, self.pin, 'plugged_in')
        }

    def __del__(self):
        self.pixels.deinit()

    def exec_cmd(self, command):
        if command in self.backlight_commands:
            func = self.backlight_commands[command]
            p = Process(target=func, args=())
            p.start()
            return p

    def __init_pixels(self, leds):
        self.pin = leds[0]
        self.pixels = neopixel.NeoPixel(leds[0], leds[1], brightness=leds[2], auto_write=False,
                                   pixel_order=ORDER)
