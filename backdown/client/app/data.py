import os
import json
import sys
data_dir = "data_"+sys.argv[1]
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
conf_path = os.path.join(data_dir, 'conf.json')
if not os.path.exists(conf_path):
    open(conf_path, 'w').write("{}")

def get_conf():
    return json.loads(open(conf_path).read())

def save_conf(data):
    open(conf_path, 'w').write(json.dumps(data))
