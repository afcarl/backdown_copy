import os
import json
import sys
import threading

conf_lock = threading.Lock()

data_dir = "data_"+sys.argv[1]
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