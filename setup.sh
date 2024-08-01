#!/bin/bash

source ~/.zshrc
eval "$(conda shell.zsh hook)"

conda create --name voice_client python=3.8

conda activate voice_client
conda install numpy pyzmq
pip install sounddevice 

# conda env remove --name voice_client