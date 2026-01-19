#!/bin/bash
export DISPLAY=:1
Xvfb :1 -screen 0 1280x800x24 &
sleep 2
startxfce4 &
sleep 2
x11vnc -display :1 -nopw -forever &
sleep 5
python /home/user/app/app.py &
websockify --web /usr/share/novnc/ 6080 localhost:5900
