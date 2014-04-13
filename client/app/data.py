import os
import json
import sys
import threading
import shutil

conf_lock = threading.Lock()

port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1][0]!='-') else 9999
data_dir = "data_"+str(port)
if '--clear' in sys.argv:
    shutil.rmtree(data_dir)
default_dir = os.path.expanduser("~/Desktop/Backdown")
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
conf_path = os.path.join(data_dir, 'conf.json')
if not os.path.exists(conf_path):
    open(conf_path, 'w').write("{}")

def get_conf():
    conf_lock.acquire()
    conf = json.loads(open(conf_path).read())
    conf_lock.release()
    return conf

def save_conf(data):
    conf_lock.acquire()
    open(conf_path, 'w').write(json.dumps(data))
    conf_lock.release()
