import requests as r
import os
import chunkify
import json
import threading
import time
import StringIO
import zipfile

root = 'http://localhost:5000'

import data

def start_sync_task():
    thread = threading.Thread(target=sync_task)
    thread.daemon = True
    thread.start()

def sync_task():
    while True:
        did_stuff = sync_now()
        if did_stuff:
            print "Did stuff"
            time.sleep(1)
        else:
            print "Did nothing"
            time.sleep(5)

def sync_now():
    conf = data.get_conf()
    if 'user' not in conf or 'dir' not in conf:
        return False
    
    chunk_dir = os.path.join(data.data_dir, "chunks")
    if not os.path.exists(chunk_dir): os.mkdir(chunk_dir)
    backup_dir = os.path.join(data.data_dir, "backups")
    if not os.path.exists(backup_dir): os.mkdir(backup_dir)
    
    return sync(conf['user'], conf['secret'], conf['friends'], conf['dir'], chunk_dir, backup_dir)

def postjson(endpoint, payload):
    res = r.post(root+endpoint, data=json.dumps(payload), headers={"Content-Type": "application/json"}).json()
    return res

def sync(user, secret, friends, user_dir, chunk_dir, backup_dir):
    did_anything = False
    
    encryption_key = 'shhh!'
    deleted_chunks, created_chunks = chunkify.chunkify([user_dir], encryption_key, chunk_dir)
    postjson('/update_chunks', {"user": user, "secret": secret, "created": created_chunks, "deleted": deleted_chunks})
    
    expired_chunks = postjson('/chunks_expired', {"user": user, "secret": secret})['expired']
    for chunk in expired_chunks:
        path = os.path.join(backup_dir, chunk['user'], chunk['chunk_id'])
        if os.path.exists(path):
            did_anything = True
            os.remove(path)
    
    # try restoring any pending files:
    restorables = postjson('/get_restorable_chunks', {"user": user, "secret": secret})['chunks']
    for chunk in restorables:
        did_anything = True
        data = r.post(root+'/download_chunk/'+chunk['key'], data=json.dumps({"user": user, "secret": secret}), headers={"Content-Type": "application/json"}).content
        path = os.path.join(user_dir, chunk['chunk_id'])
        #open(path, 'wb').write(data)
        archive = zipfile.ZipFile(StringIO.StringIO(data))
        archive.extractall(user_dir)
    
    # try uploading any files that need to be restored:
    files_to_restore = postjson('/files_to_restore', {"user": user, "secret": secret, "friends": friends})['chunks']
    for chunk in files_to_restore:
        path = os.path.join(backup_dir, chunk['user'], chunk['chunk_id'])
        if os.path.exists(path):
            did_anything = True
            r.post(root+'/upload_chunk/'+chunk['key'], data=open(path, 'rb').read(), headers={"Content-Type": "application/octet-stream"})
    
    while True:
        chunks = postjson('/chunks_to_upload', {"user": user, "secret": secret})['chunks']
        if len(chunks)==0:
            break
        did_anything = True
        chunk = chunks[0]
        data = open(os.path.join(chunk_dir, chunk['chunk_id']))
        print r.post(root+'/upload_chunk/'+chunk['key'], data=data, headers={"Content-Type": "application/octet-stream"})
        
    
    while True:
        chunks = postjson('/chunks_to_download', {"user": user, "secret": secret, "friends": friends})['chunks']
        if len(chunks)==0:
            break
        did_anything = True
        chunk = chunks[0]
        resp = r.post(root+'/download_chunk/'+chunk['key'], data=json.dumps({"user": user, "secret": secret}), headers={"Content-Type": "application/json"})
        #print resp
        data = resp.content
        if data and len(data)>0:
            user_dir = os.path.join(backup_dir, chunk['user'])
            if not os.path.exists(user_dir):
                os.mkdir(os.path.join(backup_dir, chunk['user']))
            open(os.path.join(user_dir, chunk['chunk_id']), 'wb').write(data)
    
    return did_anything
    

