#!/bin/bash

CMD=/home/rho/bin/rgbw_9865.py
Z=0.00024
T1=1200
T2=800
T3=600
T4=600
Ttimer=0

CH1=0
CH2=1

if [ $# -ge 2 ]; then
    Ttimer=$2
fi

if [ $# -ge 1 ]; then
    x=$1
    if [ $x -ge 0 ]; then
	T1=`expr $T1 / $x`
	T2=`expr $T2 / $x`
	T3=`expr $T3 / $x`
	T4=`expr $T4 / $x`
    fi
fi
   
if [ -f $CMD ]; then
    sleep $Ttimer
    $CMD $CH1   $Z 0 0 0            0.01 0 0 0  $T1
    $CMD $CH1   0.01 $Z 0 0         0.02 0.001 0 0 $T2
    $CMD $CH1   0.02 0.001 $Z 0     0.04 0.01 0.005 0 $T3
    $CMD $CH1   0.04 0.01 0.005 $Z  1 0.64 0.1 0.32 $T4
fi
