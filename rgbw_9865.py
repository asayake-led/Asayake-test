#!/usr/bin/env python3

import pigpio
import os, sys, time
import logging

# https://learn.adafruit.com/16-channel-pwm-servo-driver/python-circuitpython
import board
import busio
import adafruit_pca9685

#constants

RGBW_PWM_FREQ = 1000
RGBW_PWM_RANGE = 0xffff
RGBW_PWM_MAX   = 4095
RGBW_MAX_CH = 2
RGBW_GPIO = [
    [0, 2, 3, 1],
    [4, 6, 7, 5],
    ["R", "G", "B", "W"]
]

LED_MIN = 1.0/RGBW_PWM_MAX
LED_MAX = 1.0

LOOP_MAX_MAX = 1000
TIME_RESLUTION_SEC = 0.01
GPIO_TERMINATE_EVENT = 20

# logging
#useLogging = True
useLogging = False

logger = logging.getLogger('RGBW Logging')
logger.setLevel(10)
#fh = logging.FileHandler('test_rgbw.log')
#logger.addHandler(fh)
sh = logging.StreamHandler()
logger.addHandler(sh)
formatter = logging.Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
#fh.setFormatter(formatter)
sh.setFormatter(formatter)

pi = pigpio.pi()

i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)

def init_rgbw(freq):
    if freq <= 0:
        freq = pca.frequency
    pca.frequency = freq

def reset_rgbw(led_ch):
    ch = 0
    if 0 <= led_ch < RGBW_MAX_CH:
        for ch in RGBW_GPIO[led_ch]:
            pca.channels[ch].duty_cycle = 0

def set_rgbw_ratio(led_ch, rgbw):
    def pwm_dutycycle_ratio(fval):
        intval = int(fval*RGBW_PWM_RANGE)
        if RGBW_PWM_RANGE < intval:
            intval = RGBW_PWM_RANGE
        return intval

    if 0 <= led_ch < RGBW_MAX_CH:
        irgbw = [0,0,0,0]
        for i in range(4):
            ch = RGBW_GPIO[led_ch][i]
            irgbw[i] = pwm_dutycycle_ratio(rgbw[i])
            pca.channels[ch].duty_cycle = irgbw[i]
    if useLogging:
        logger.info('SET LED-CH[%d] %4x %4x %4x %4x', led_ch, irgbw[0], irgbw[1], irgbw[2], irgbw[3])

def get_rgbw_ratio(led_ch):
    rgbw = [0,0,0,0]
    irgbw = [0,0,0,0]
    if 0 <= led_ch < RGBW_MAX_CH:
        for i in range(4):
            ch = RGBW_GPIO[led_ch][i]
            irgbw[i] = pca.channels[ch].duty_cycle
            rgbw[i] = float(irgbw[i]) / RGBW_PWM_RANGE
        if useLogging:
            logger.info('GET LED-CH[%d] %4x %4x %4x %4x', led_ch, irgbw[0], irgbw[1], irgbw[2], irgbw[3])
    return rgbw

def main():
    global RGBW_PWM_FREQ, useLogging
    rgbw1 = [0,0,0,0]
    rgbw2 = [0,0,0,0]
    
    argv = sys.argv
    argc = len(argv)

    init_only = False

    if argc == 2:
        RGBW_PWM_FREQ = int(argv[1])
        init_only = True
    elif argc == 4:
        ch = int(argv[1])
        r = float(argv[2])
        decay = float(argv[3])
        rgbw1 = get_rgbw_ratio(ch)
        for i in range(4) :
            rgbw2[i] = r
    elif argc == 7:
        ch = int(argv[1])
        for i in range(4) :
            rgbw2[i] = float(argv[i+2])
        decay = float(argv[6])
        rgbw1 = get_rgbw_ratio(ch)
    elif argc == 11:
        ch = int(argv[1])
        for i in range(4) :
            rgbw1[i] = float(argv[i+2])
        for i in range(4) :
            rgbw2[i] = float(argv[i+6])
        decay = float(argv[10])
    else:
        init_only = True
        
    if init_only:
        init_rgbw(RGBW_PWM_FREQ)
        for i in range(RGBW_MAX_CH):
            reset_rgbw(i)
    else:
        #init_rgbw(0)
        init_rgbw(RGBW_PWM_FREQ)

        time_reslution_sec = TIME_RESLUTION_SEC
        loop_max = int(decay / time_reslution_sec)
        loop_active = loop_max
        if loop_max > LOOP_MAX_MAX:
            loop_max = LOOP_MAX_MAX
            time_reslution_sec = decay / loop_max
            loop_active = loop_max
        elif loop_max == 0:
            loop_max = 1
            loop_active = 0
            
        def terminate(event, tick):
            global loop_active
            loop_active = -1

        pi.event_trigger(GPIO_TERMINATE_EVENT)
        # Some delay needs before setting the callback.
        time.sleep(0.05)
        cb_terminate = pi.event_callback(GPIO_TERMINATE_EVENT, terminate)

        while loop_active >= 0:
            rgbw = [0,0,0,0]
            for i in range(4):
                rgbw[i] = (loop_active*rgbw1[i] + (loop_max-loop_active)*rgbw2[i]) / loop_max
            set_rgbw_ratio(ch, rgbw)
            time.sleep(time_reslution_sec)
            loop_active = loop_active - 1

main()
