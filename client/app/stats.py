from app import app, templ8
import data
import requests
import sync
import os

friend_name_cache = {}
def get_friend_name(id):
    if id not in friend_name_cache:
        friend_name_cache[id] = requests.get(sync.root+"/name_for_user/"+id).json()['name']
    return friend_name_cache[id]

def size_for_dir(folder):
    folder_size = 0
    for (path, dirs, files) in os.walk(folder):
      for file in files:
        filename = os.path.join(path, file)
        folder_size += os.path.getsize(filename)
    return folder_size

def capacity_for_friend(id):
    dir = os.path.join(data.data_dir, 'backups', id)
    if os.path.exists(dir):
        return size_for_dir(dir)
    else:
        return 0

@app.route('/stats')
def stats():
    conf = data.get_conf()
    if 'user' not in conf or 'dir' not in conf:
        return ""
    
    info = {}
    
    info['exportees'] = requests.post(sync.root+'/export_breakdown/'+conf['user']).json()['export_capacities']
    
    info['exporters'] = [{"name": get_friend_name(id), "capacity": capacity_for_friend(id)} for id in conf['friends'] if len(id)>0]
    
    progress = requests.get(sync.root+'/backup_progress/'+conf['user']).json()
    
    info['backup_progress'] = progress['backup_progress']
    
    data_size = size_for_dir(conf['dir'])
    remaining_to_restore = progress['capacity_left_to_restore']
    info['restore_progress'] = 1-remaining_to_restore*1.0/(data_size+remaining_to_restore) if (data_size+remaining_to_restore) else 0
    
    return templ8("stats.html", info)
