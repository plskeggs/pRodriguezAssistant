# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import board
import neopixel
import time
import math
from multiprocessing import Process

#parameters list: pin, count, brightness
#GPIO10, GPIO12, GPIO18 or GPIO21
mouth_pin = board.D12
eyes_pin = board.D10
mouth_section = 0
eyes_section = 1
full_section = 2
mouth_leds = (mouth_pin, 18, 0.5, mouth_section)
eyes_leds = (mouth_pin, 2, 1, eyes_section) # two eyes in series
all_leds = (mouth_pin, 20, 1, full_section) # combining both sets

strips = {
    'EYES': eyes_leds,
    'MOUTH': mouth_leds
}

pin = None
pixels = None
ORDER = neopixel.GRB
initialized = False

#default_color = (243, 253, 0)
default_color = (243, 253, 128)
no_color = (32, 32, 32)
orange = (255,165,0)
darkorange = (255,140,0)
blue = (0,0,255)
revert_row1 = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0}

is_talking = False

def fill_pixels(section, color):
    global pixels
    global eyes_section
    global initialized
    if initialized == False:
        print("NOT INITIALIZED!")
        return
    if section == eyes_section:
        color = tuple(int(i * eyes_leds[2]) for i in color)
        pixels[mouth_leds[1]] = color
        pixels[mouth_leds[1] + 1] = color
    else:
        color = tuple(int(i * mouth_leds[2]) for i in color)
        for i in range(0, mouth_leds[1]):
            pixels[i] = color
    print("pixels = ")
    print(pixels)
    print("section = ")
    print(section)
    print("color = ")
    print(color)
    pixels.show()

def blink(section, mode):
    global pixels
    global eyes_section
    global initialized
    if initialized == False:
        print("NOT INITIALIZED!")
        return
    if section != eyes_section:
        print('Teeth do not support blink command!')
        return

    if mode == 'plugged_in':
        phase_1_color = darkorange
        phase_2_color = blue
        period = 0.1
    else:
        phase_1_color = no_color
        phase_2_color = default_color
        period = 0.25

    print("section = ")
    print(section)
    print("phase_1_color = ")
    print(phase_1_color)
    print("phase_2_color = ")
    print(phase_2_color)
    t = 0
    while t < 30:  # maximum answer length to prevent infinite loop
        fill_pixels(section, phase_1_color)
        time.sleep(period)
        fill_pixels(section, phase_2_color)
        time.sleep(period)
    t += period * 4

def talk(section, mode):
    global pixels
    global mouth_section
    global initialized
    if initialized == False:
        print("NOT INITIALIZED!")
        return
    if section != mouth_section:
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

    print("section = ")
    print(section)
    print("front_color = ")
    print(front_color)
    print("back_color = ")
    print(back_color)
    t = 0
    while t < 30: # maximum answer length to prevent infinite loop
        fill_pixels(section, back_color)
        for i in range(6, 12):
            pixels[i] = front_color
        pixels.show()
        time.sleep(period)

        sin_cos_graph(section, math.cos, back_color, front_color)
        time.sleep(period)

        fill_pixels(section, back_color)
        for i in range(6, 12):
            pixels[i] = front_color
        pixels.show()
        time.sleep(period)

        sin_cos_graph(section, math.sin, back_color, front_color)
        time.sleep(period)
        t += period * 4

def sin_cos_graph(section, func, back_color, front_color):
    global pixels
    global mouth_section
    if section != mouth_section:
        print('Eyes do not support talk command!')
        return
    if func != math.sin and func != math.cos:
        print('Only sin() and cos() are supported!')
        return
    fill_pixels(section, back_color)
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
        if strip in strips:
            self.__init_pixels(strips[strip])
        else:
            print("Strip not found!")
        print("Initialized strip = ")
        print(strip)
        self.backlight_commands = {
            'ON': lambda: fill_pixels(self.section, default_color),
            'OFF': lambda: fill_pixels(self.section, no_color),
            'TALK': lambda: talk(self.section, 'normal'),
            'PLUGGED_IN': lambda: talk(self.section, 'plugged_in'),
            'BLINK_NORMAL': lambda: blink(self.section, 'normal'),
            'BLINK_PLUGGED_IN': lambda: blink(self.section, 'plugged_in')
        }

    def __del__(self):
        global pixels
        global initialized
        if initialized:
            print("deinitializing NeoPixels!")
            pixels.deinit()
            initialized = False

    def exec_cmd(self, command):
        if command in self.backlight_commands:
            func = self.backlight_commands[command]
            p = Process(target=func, args=())
            p.start()
            return p

    def __init_pixels(self, leds):
        global pixels
        global initialized
        self.section = leds[3]
        print("leds = ")
        print(leds)
        print("initialized section = %d" % self.section)
        if initialized == False:
            print("initializing NeoPixels!")
            pixels = neopixel.NeoPixel(all_leds[0], all_leds[1], brightness=all_leds[2], auto_write=False, pixel_order=ORDER)
            initialized = True

