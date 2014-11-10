#!/bin/bash

all=0
prefix="grabbot"
if [ $# -eq 0 ]; then
    all=1
fi

if [ $all = 1 ] || [ $1 = 1 ]; then
    python -m builders.configuration_builder data_files/$prefix/$prefix.struct data_files/$prefix/$prefix.conf
fi

if [ $all = 1 ] || [ $1 = 2 ]
then
    mv data_files/$prefix/$prefix.conf ~/SMORES/gaits_and_configs/$prefix/;
    if [ $all = 0 ]
    then
        cd ~/SMORES/SimulationPlugins/SimulationController/pythonGUI/
        python ControlGUI.py
    fi
fi

if [ $all = 1 ] || [ $1 = 3 ]; then
    python make_gait.py data_files/$prefix/$prefix
fi

if [ $all = 1 ] || [ $1 = 4 ]; then
    mv data_files/$prefix/$prefix.gait ~/SMORES/gaits_and_configs/$prefix/
    cd ~/SMORES/SimulationPlugins/SimulationController/pythonGUI/
    python ControlGUI.py
fi
