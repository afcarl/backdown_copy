from backend import app, db, templ8
import json
import random
import flask
import pymongo
from bson.objectid import ObjectId as to_id
from bson.binary import Binary
from collections import defaultdict

@app.route('/sign_up', methods=['POST'])
def sign_up():
    secret = str(random.random())
    id = str(db.users.save({"secret": secret, "name": flask.request.form.get('name'), "chunks_to_restore": []}))
    return json.dumps({"user": id, "secret": secret})

def get_user(user, secret):
    return db.users.find_one({"_id": user, "secret": secret})

@app.route('/update_chunks', methods=['POST'])
def update_chunks():
    data = flask.request.json
    if not get_user(to_id(data['user']), data['secret']):
        return json.dumps({"error": "bad_login"})
    for chunk_id in data['created']:
        db.chunks.save({"user": to_id(data['user']), "chunk_id": chunk_id, "mirrors": [], "alive": True, "data": None, "size": 0})
    if len(data['created'])>0:
        # clear the buffered files from this user to avoid the condition where there's a buffered file that every peer already has while there are new files awaiting buffering:
        db.chunks.update({"user": to_id(data['user']), "data": {"$ne": None}}, {"$set": {"data": None}})
    for chunk_id in data['deleted']:
        chunk = db.chunks.find_one({"user": to_id(data['user']), "chunk_id": chunk_id})
        if chunk:
            chunk['data'] = None
            chunk['alive'] = False
            db.chunks.save(chunk)
    return json.dumps({"result": "okay"})

@app.route('/chunks_to_upload', methods=['POST'])
def chunks_to_upload():
    data = flask.request.json
    if not get_user(to_id(data['user']), data['secret']):
        return json.dumps({"error": "bad_login"})
    live_chunks = list(db.chunks.find({"user": to_id(data['user']), "alive": True}))
    to_upload = []
    if len([chunk for chunk in live_chunks if chunk['data']])==0 and len(live_chunks):
        live_chunks.sort(key=lambda x: len(x['mirrors']))
        chunk = live_chunks[0]
        to_upload.append({"chunk_id": chunk['chunk_id'], "key": str(chunk['_id'])})
    return json.dumps({"chunks": to_upload})

@app.route('/upload_chunk/<id>', methods=['POST'])
def upload(id):
    chunk = db.chunks.find_one({"_id": to_id(id)})
    chunk['data'] = Binary(flask.request.data)
    chunk['size'] = len(chunk['data'])
    db.chunks.save(chunk)
    return json.dumps({"result": "okay"})

@app.route('/chunks_expired', methods=['POST'])
def chunks_expired():
    data = flask.request.json
    if not get_user(to_id(data['user']), data['secret']):
        return json.dumps({"error": "bad_login"})
    chunks = []
    for chunk in db.chunks.find({"mirrors": {"$in": [to_id(data['user'])]}, "alive": False}):
        user = db.users.find_one({"_id": chunk['user']})
        if chunk['chunk_id'] not in user['chunks_to_restore']:
            chunks.append(chunk)
    for chunk in chunks:
        db.chunks.update({"_id": chunk['_id']}, {"$pull": {"mirrors": to_id(data['user'])}})
    return json.dumps({"expired": [{"chunk_id": chunk['chunk_id'], "user": str(chunk['user'])} for chunk in chunks]})

@app.route('/chunks_to_download', methods=['POST'])
def chunks_to_download():
    data = flask.request.json
    friend_ids = map(to_id, data['friends'])
    chunks_with_data = db.chunks.find({"alive": True, "user": {"$in": friend_ids}, "data": {"$ne": None}, "mirrors": {"$nin": [to_id(data['user'])]}})
    return json.dumps({"chunks": [{"chunk_id": chunk['chunk_id'], "user": str(chunk['user']), "key": str(chunk['_id'])} for chunk in chunks_with_data]})

@app.route('/download_chunk/<id>', methods=['POST'])
def download_chunk(id):
    data = flask.request.json
    if not get_user(to_id(data['user']), data['secret']):
        return json.dumps({"error": "bad_login"})
    chunk = db.chunks.find_one({"_id": to_id(id)})
    chunk_data = chunk['data']
    if chunk_data:        
        chunk['data'] = None
        if chunk['user'] == to_id(data['user']):
            # the user is restoring their own chunk:
            user = get_user(to_id(data['user']), data['secret'])
            user['chunks_to_restore'].remove(chunk['chunk_id'])
            db.users.save(user)
        else:
            # another client just mirrored this file:    
            chunk['mirrors'].append(to_id(data['user']))
            db.chunks.save(chunk)
        return chunk_data
    else:
        return ''

@app.route('/restore', methods=['POST'])
def restore():
    data = flask.request.json
    user = get_user(to_id(data['user']), data['secret'])
    if not user:
        return json.dumps({"error": "bad_login"})
    user['chunks_to_restore'] = [chunk['chunk_id'] for chunk in db.chunks.find({"user": user['_id'], "alive": True})]
    db.users.save(user)
    return json.dumps({"result": "okay"})

@app.route('/files_to_restore', methods=['POST'])
def files_to_restore():
    data = flask.request.json
    friends = list(db.users.find({"_id": {"$in": map(to_id, data['friends'])}}))
    chunks = []
    for friend in friends:
        for chunk_id in friend['chunks_to_restore']:
            chunk = db.chunks.find_one({"chunk_id": chunk_id, "user": friend['_id']})
            if chunk['data']==None:
                chunk_key = str(chunk['_id'])
                chunks.append({"key": chunk_key, "chunk_id": chunk_id, "user": str(friend['_id'])})
                break # so we only upload one before the other end must pick it up
    return json.dumps({"chunks": chunks})

@app.route('/get_restorable_chunks', methods=['POST'])
def get_restorable_chunks():
    data = flask.request.json
    user = db.users.find_one({"_id": to_id(data['user'])})
    chunks = db.chunks.find({"user": to_id(data['user']), "chunk_id": {"$in": user['chunks_to_restore']}, "data": {"$ne": None}})
    chunks = [{"chunk_id": chunk['chunk_id'], "key": str(chunk['_id'])} for chunk in chunks]
    return json.dumps({"chunks": chunks})

@app.route('/name_for_user/<user_id>')
def name_for_user(user_id):
    return json.dumps({"name": db.users.find_one({"_id": to_id(user_id)})['name']})

@app.route('/export_breakdown/<user>', methods=["POST"])
def export_breakdown(user):
    chunks_exported = db.chunks.find({"user": to_id(user), "alive": True})
    export_capacities = defaultdict(int)
    for chunk in chunks_exported:
        export_capacities[chunk['user']] += chunk['size']
    export_capacities = [{"name": name_for_user(id), "capacity": capacity} for id, capacity in export_capacities.iteritems()]
    return json.dumps({"export_capacities": export_capacities})

@app.route('/backup_progress/<user>')
def backup_progress(user):
    chunks = list(db.chunks.find({"user": to_id(user), "alive": True}))
    backup_progress = len([chunk for chunk in chunks if len(chunk['mirrors'])>0])*1.0/len(chunks) if len(chunks) else 1
    
    chunks_to_restore = db.users.find_one({"_id": to_id(user)})['chunks_to_restore']
    capacity_to_restore = sum([chunk['size'] for chunk in db.chunks.find({"user": to_id(user), "chunk_id": {"$in": chunks_to_restore}})])
    
    return json.dumps({"backup_progress": backup_progress, "capacity_left_to_restore": capacity_to_restore})

