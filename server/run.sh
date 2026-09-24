#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r libraryRequirements.txt
python3 main.py
