#!/usr/bin/python

import os, time, webbrowser

def is_service_running():
    import socket;
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',9999))
    return result==0

if not is_service_running():
    print "Not running"
    import subprocess
    subprocess.Popen("source venv/bin/activate && python run.py", shell=True)
    time.sleep(1)


webbrowser.open("http://localhost:9999/ui")
