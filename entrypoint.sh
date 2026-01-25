#!/bin/bash

# Clean up any stale X sockets
rm -f /tmp/.X11-unix/X1 /tmp/.X1-lock 2>/dev/null

# Set up display
export DISPLAY=:1

# Start Xvfb (virtual framebuffer) with explicit options
Xvfb :1 -screen 0 1280x800x24 -ac -noreset &
XVFB_PID=$!
sleep 3

# Ensure DISPLAY is set for all child processes
export DISPLAY=:1

# Start D-Bus (required by XFCE4)
dbus-daemon --session --address=unix:tmpdir=/tmp --print-address &
sleep 1

# Start XFCE4 desktop environment
startxfce4 &
XFCE_PID=$!
sleep 3

# Wait for X11 to be ready
for i in {1..10}; do
  xdpyinfo -display :1 >/dev/null 2>&1 && break
  sleep 1
done

# Start x11vnc (VNC server) - allow connections from anywhere
x11vnc -display :1 -nopw -forever &
sleep 2

# Start Python Flask app
python /home/user/app/app.py &
APP_PID=$!
sleep 2

# Start websockify (VNC to WebSocket bridge) - bind to 0.0.0.0 for external access
websockify --web /usr/share/novnc/ 0.0.0.0:6080 localhost:5900 &
WEBSOCKIFY_PID=$!

# Keep the container running
wait $XVFB_PID

