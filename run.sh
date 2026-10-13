#!/bin/bash

google-chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/.x-scraper-profile" &

sleep 2

python3 ./main.py < input.txt
