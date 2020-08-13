# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
import threading
import random
import sys
from common import power
from profiles.bender import bender as profile

import signal

is_plugged_in = False
main_thread_is_running = True

SLEEP_TASK_ENABLED = True
IDLE_TIME = 60 # in minutes, 2 - minimum
sleep_enabled = True
is_sleeping = False
sleep_counter = 0
sleep_counter_lock = threading.Lock()

UPS_TASK_ENABLED = True
UPS_TASK_INTERVAL = 5
if UPS_TASK_ENABLED: from common import ups_lite

fsm_state = 1
fsm_transition = {
    'repeated keyphrase': 2,
    'exit': 3,
    'reboot': 4,
    'shutdown': 5
}

def signal_handler(sig, frame):
    global main_thread_is_running
    print('You pressed ctrl-c!')
    time.sleep(1)
    main_thread_is_running = False

def sleep_enable_set(val):
    global sleep_enabled
    sleep_enabled = val

def main():
    global main_thread_is_running
    global fsm_state
    global sleep_enabled

    signal.signal(signal.SIGINT, signal_handler)
    print("pRodriguezAssistant Starting Up...")
    print("set speaker volume...")
    profile.vol_ctrl.set_speaker_volume(profile.vol_ctrl.speaker_volume)

    print("kill pocketsphinx...")
    kill_pocketsphinx()
    print("stop music player...")
    #profile.m_player.send_command('stop')

    print("turn eyes off...")
    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('OFF')
    time.sleep(0.15)

    print("turn mouth off...")
    if profile.mouth_bl:
        profile.mouth_bl.exec_cmd('OFF')
    time.sleep(0.15)

    print("start UPS task...")
    if UPS_TASK_ENABLED:
        ups_thread = threading.Thread(target=ups_task)
        ups_thread.start()

    print("start sleep task...")
    if SLEEP_TASK_ENABLED:
        profile.sleep_enable_set = sleep_enable_set
        sleep_thread = threading.Thread(target=sleep_task)
        sleep_thread.daemon = True
        sleep_thread.start()

    print("start pocketsphinx...")
    #sphinx_proc = subprocess.Popen(["%s" % profile.speech_recognizer.cmd_line], shell=True, stdout=subprocess.PIPE)
    print(["%s" % profile.speech_recognizer.cmd_line])

    print("turn on eyes...")
    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('ON')

    wake_up()

    print("start speech processing loop...")
    while main_thread_is_running:
        if (fsm_state == 1):
            #if find_keyphrase(sphinx_proc):
            #    conversation_mode(sphinx_proc)
            #else:
            time.sleep(random.randint(5,15))
            profile.a_player.play_random()
        elif (fsm_state == 2):
            conversation_mode(sphinx_proc)
        elif (fsm_state == 3):
            break
        elif (fsm_state == 4):
            break
        elif (fsm_state == 5):
            break
        else:
            continue

    print("preparing to exit...")
    main_thread_is_running = False
    print("kill pocketsphinx...")
    kill_pocketsphinx()

    print("stop music player...")
    #profile.m_player.send_command('stop')

    print("turn eyes off...")
    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('OFF')
    time.sleep(3)

    if (fsm_state == 4):
        print("reboot!")
        power.reboot()

    if (fsm_state == 5):
        print("shutdown.")
        power.shutdown()

    sys.exit(0)

def ups_task():
    global is_plugged_in
    global main_thread_is_running
    prev_voltage = ups_lite.read_voltage()
    prev_capacity = ups_lite.read_capacity()
    while main_thread_is_running:
        time.sleep(UPS_TASK_INTERVAL)
        voltage = ups_lite.read_voltage()
        capacity = ups_lite.read_capacity()
        if voltage >= 4.20:
            if prev_voltage <= 4.15:
                profile.a_player.play_answer('electricity')
        else:
            if capacity < 20 and (prev_capacity > capacity):
                power.shutdown()
        prev_voltage = voltage
        prev_capacity = capacity
        if is_plugged_in != ups_lite.adapter_in():
            is_plugged_in = ups_lite.adapter_in()
            if is_plugged_in:
                profile.a_player.play_answer('electricity')
        if False:
            print("voltage %f" % voltage)
            print("capacity %d" % capacity)
            if ups_lite.adapter_in():
                print("power adapter plugged in")
            else:
                print("power adapter unplugged")

def sleep_task():
    global is_sleeping
    global sleep_enabled
    global sleep_counter

    while main_thread_is_running:
        time.sleep(60)
        if sleep_enabled:
            sleep_counter_inc()
            if sleep_counter >= IDLE_TIME:
                if not is_sleeping:
                    if not False: # profile.m_player.musicIsPlaying:
                        if profile.eyes_bl:
                            profile.eyes_bl.exec_cmd('OFF')
                        profile.a_player.play_answer('fall asleep')
                        is_sleeping = True

def sleep_counter_inc():
    global sleep_counter
    sleep_counter_lock.acquire()
    sleep_counter += 1
    sleep_counter_lock.release()

def sleep_counter_reset():
    global sleep_counter
    sleep_counter_lock.acquire()
    sleep_counter = 0
    sleep_counter_lock.release()

def wake_up():
    global is_sleeping
    if profile.eyes_bl:
        profile.eyes_bl.exec_cmd('ON')
    profile.a_player.play_answer('wake up')
    is_sleeping = False

def get_utterance(sphinx_proc):
    retcode = sphinx_proc.returncode
    utt = sphinx_proc.stdout.readline().decode('utf8').rstrip().lower()
    if len(utt):
        print('utterance = ' + utt)
    return utt

def find_keyphrase(sphinx_proc):
    global sleep_enabled
    global is_sleeping
    global aplayer
    global fsm_state

    keyphrase_found = False
    #print('Start mode:')

    utt = get_utterance(sphinx_proc)

    if profile.speech_recognizer.lang == 'ru':
        try:
            utt = profile.TranslatorRU.tr_start_ru_en[utt]
        except KeyError as e:
            utt = 'unrecognized'
            #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

    if (profile.name in utt):
        if sleep_enabled:
            sleep_counter_reset()
        if False: # profile.m_player.musicIsPlaying:
            if('pause' in utt or 'stop' in utt or profile.vol_ctrl.speaker_volume == 0):
                profile.m_player.send_command('pause')
                keyphrase_found = True
        else:
            if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)) and not is_sleeping:
                answer = 'hey ' + profile.name
                profile.a_player.play_answer(answer)
            if is_sleeping:
                wake_up()
            keyphrase_found = True

    return keyphrase_found

def conversation_mode(sphinx_proc):
    global sleep_enabled
    global is_sleeping
    global fsm_state

    print ('Conversation mode:')

    utt = get_utterance(sphinx_proc)

    if profile.speech_recognizer.lang == 'ru':
        try:
            utt = profile.TranslatorRU.tr_conversation_ru_en[utt]
        except KeyError as e:
            utt = 'unrecognized'
            #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

    if is_sleeping:
        wake_up()
    else:
        before_action = None
        after_action = None

        try:
            action = profile.actions[utt]
            answer = action[0]
            before_action = action[1]
            after_action = action[2]
        except KeyError as e:
            answer = 'unrecognized'

        print ("answer = " + answer)

        try:
            fsm_state = fsm_transition[answer]
        except:
            fsm_state = 1

        if before_action:
            before_action()

        if answer != 'no audio':
            profile.a_player.play_answer(answer)

        if after_action:
            after_action()

        if answer != 'shutdown' or answer != 'reboot':
            if False: # profile.m_player.musicIsPlaying:
                profile.m_player.send_command('resume')

    if sleep_enabled:
        sleep_counter_reset()

def stop_pocketsphinx():
    stop_exe = 'killall -s STOP pocketsphinx_co'
    p = subprocess.Popen(["%s" % stop_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def cont_pocketsphinx():
    cont_exe = 'killall -s CONT pocketsphinx_co'
    p = subprocess.Popen(["%s" % cont_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

main()
