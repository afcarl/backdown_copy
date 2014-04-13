from app import app, templ8
import threading
import os
import json
import flask
import data
import requests
import sync
import platform
import copy

@app.route('/ui', methods=['GET', 'POST'])
def settings():
    conf = data.get_conf()
    if 'user' not in conf:
        info = requests.post(sync.root+"/sign_up", {"name": platform.node()}).json()
        conf['user'] = info['user']
        conf['secret'] = info['secret']
        conf['friends'] = conf.get('friends', [])
        data.save_conf(conf)
    if flask.request.method=='GET':
        args = copy.copy(conf)
        args['msg'] = flask.request.args.get('msg', None)
        return templ8("ui.html", args)
    elif flask.request.method=='POST':
        dir = flask.request.form.get('dir')
        conf['dir'] = dir
        data.save_conf(conf)
        return flask.redirect('/ui?msg=Saved')
        return "Saved!"

@app.route('/add/<id>')
def add(id):
    conf = data.get_conf()
    conf['friends'] = list(set(conf.get('friends', [])+[id]))
    data.save_conf(conf)
    return flask.redirect('/ui?msg=Added.')

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


