from app import app, templ8
import threading
import os
import json
import flask
import data
import requests
import sync
    
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    conf = data.get_conf()
    if 'user' not in conf:
        info = requests.post(sync.root+"/sign_up").json()
        conf['user'] = info['user']
        conf['secret'] = info['secret']
        data.save_conf(conf)
    if flask.request.method=='GET':
        return templ8("settings.html", conf)
    elif flask.request.method=='POST':
        friends = flask.request.form.get('friends').split('\n')
        friends = [f for f in friends if len(f)>0]
        conf['friends'] = friends
        dir = flask.request.form.get('dir')
        conf['dir'] = dir
        data.save_conf(conf)
        return "Saved!"

@app.route('/sync_now', methods=["GET"])
def sync_now():
    conf = data.get_conf()
    if 'user' not in conf or 'dir' not in conf:
        return "Conf. incomplete"
    # def sync(user, secret, friends, user_dir, chunk_dir, backup_dir):
    
    chunk_dir = os.path.join(data.data_dir, "chunks")
    if not os.path.exists(chunk_dir): os.mkdir(chunk_dir)
    backup_dir = os.path.join(data.data_dir, "backups")
    if not os.path.exists(backup_dir): os.mkdir(backup_dir)
    
    sync.sync(conf['user'], conf['secret'], conf['friends'], conf['dir'], chunk_dir, backup_dir)
    return "Okay!"


