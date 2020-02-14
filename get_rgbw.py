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
RGBW_MAX_CH = 2
RGBW_GPIO = [
    [0, 2, 3, 1],
    [4, 6, 7, 5],
    ["R", "G", "B", "W"]
]

i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)

def init_rgbw(freq):
    if freq <= 0:
        freq = pca.frequency
    pca.frequency = freq

def get_rgbw_ratio(led_ch):
    rgbw = [0,0,0,0]
    irgbw = [0,0,0,0]
    if 0 <= led_ch < RGBW_MAX_CH:
        for i in range(4):
            ch = RGBW_GPIO[led_ch][i]
            irgbw[i] = pca.channels[ch].duty_cycle
            rgbw[i] = float(irgbw[i]) / RGBW_PWM_RANGE
    return rgbw

def main():
    global RGBW_PWM_FREQ

    argv = sys.argv
    argc = len(argv)

    if argc == 2:
        ch = int(argv[1])
        init_rgbw(0)
        rgbw1 = get_rgbw_ratio(ch)
        print('%.4f %.4f %.4f %.4f' % (rgbw1[0], rgbw1[1], rgbw1[2], rgbw1[3]))
        
main()
