# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess

modes = {
    'quiet': 80,
    'normal': 160,
    'loud': 255
}

speaker_volume = 20
VOLUME_STEP = 4
MAX_VOL = 255 # 40

def change_speaker_volume(value):
    global speaker_volume

    speaker_volume += value
    if speaker_volume < 0:
        speaker_volume = 0
    if speaker_volume > MAX_VOL:
        speaker_volume = MAX_VOL
    set_speaker_volume(speaker_volume)

def set_speaker_volume(value):
    amixer_exe = "amixer -q sset 'PCM' " + str(value)
    p = subprocess.Popen(["%s" % amixer_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()