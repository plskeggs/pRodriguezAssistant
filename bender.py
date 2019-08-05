# !/usr/bin/env python
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import string

audio_files = {}
audio_files['shutdown'] = 'with_bjah'
audio_files['start'] = 'lets_get_drunk'
audio_files['exit'] = 'lets_get_drunk'
audio_files['hey bender 0'] = 'bite'
audio_files['hey bender 1'] = 'hello'
audio_files['hey bender 2'] = 'hello_peasants'
audio_files['birthplace'] = 'born_in_tijuana'
audio_files['birthdate'] = 'birthdate'
audio_files['who are you 0'] = 'im_bender'
audio_files['who are you 1'] = 'bender_song'
audio_files['animal'] = 'turtle'
audio_files['sing'] = 'bender_song'
audio_files['magnet 0'] = 'roads_song'
audio_files['magnet 1'] = 'mountain_song'
audio_files['new sweater'] = 'new_sweater'
audio_files['kill all humans'] = 'kill_all_humans'
audio_files['wake up'] = 'most_wonderful_dream'
audio_files['enable'] = 'can_do'
audio_files['disable'] = 'can_do'
audio_files['set'] = 'can_do'
audio_files['how are you'] = 'right_now_i_feel_sorry_for_you'
audio_files['unrecognized'] = 'beat_children'
audio_files['no audio'] = 'silence'


def main():
    exe = '''pocketsphinx_continuous -adcdev plughw:1,0  -lm ./resources/bender.lm -dict ./resources/bender.dic''' + \
          ''' -jsgf ./resources/bender.gram -dictcase yes -inmic yes'''
    # '''./resources/bender.gram -dictcase yes -inmic yes -logfn /dev/null'''
    p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)

    while True:
        retcode = p.returncode
        line = p.stdout.readline()
        print("utterance = " + line)
        command = parse_utterance(string.lower(line))
        print("command = " + command)
        play_answer(command)
        time.sleep(0.15)
        if (retcode is not None):
            break


def parse_utterance(utt):
    current_milli_time = int(round(time.time() * 1000))
    if 'shutdown' in utt:
        command = 'shutdown'
    elif ('exit' in utt) or ('quit' in utt) :
        command = 'exit'
    elif ('sing' in utt) or ('song' in utt):
        command = 'sing'
    elif 'who are you' in utt:
        command = 'who are you ' + str(current_milli_time % 2)
    elif 'how are you' in utt:
        command = 'how are you'
    elif ('where are you from' in utt) or ('where were you born' in utt):
        command = 'birthplace'
    elif 'when were you born' in utt:
        command = 'birthdate'
    elif 'your favorite animal' in utt:
        command = 'animal'
    elif ('bender' in utt) and (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
        command = 'hey bender ' + str(current_milli_time % 3)
    elif 'magnet' in utt:
        command = 'magnet ' + str(current_milli_time % 2)
    elif 'new sweater' in utt:
        command = 'sweater'
    elif ('wake up' in utt) or ('awake' in utt):
        command = 'wake up'
    else:
        command = 'unrecognized'
    return command

def play_answer(command):
    answer = audio_files.get(command)
    if answer != None:
        exe = 'aplay ' + './audio/' + answer + '.wav'
        p = subprocess.Popen(["%s" % exe], shell=True, stdout=subprocess.PIPE)
    else:
        print('No answer to this question!')

main()


