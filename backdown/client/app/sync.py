import requests as r
import os
import chunkify
import json

root = 'http://localhost:5000'

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
        if data:
            user_dir = os.path.join(backup_dir, chunk['user'])
            if not os.path.exists(user_dir):
                os.mkdir(os.path.join(backup_dir, chunk['user']))
            open(os.path.join(user_dir, chunk['chunk_id']), 'wb').write(data)
    
    return did_anything
    

