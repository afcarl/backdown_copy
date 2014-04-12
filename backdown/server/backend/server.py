from backend import app, db, templ8
import json
import random
import flask
import pymongo
from bson.objectid import ObjectId as to_id
from bson.binary import Binary

@app.route('/sign_up', methods=['POST'])
def sign_up():
    secret = str(random.random())
    id = str(db.users.save({"secret": secret}))
    return json.dumps({"user": id, "secret": secret})

def get_user(user, secret):
    return db.users.find_one({"_id": user, "secret": secret})

@app.route('/update_chunks', methods=['POST'])
def update_chunks():
    data = flask.request.json
    if not get_user(to_id(data['user']), data['secret']):
        return json.dumps({"error": "bad_login"})
    for chunk_id in data['created']:
        db.chunks.save({"user": to_id(data['user']), "chunk_id": chunk_id, "mirrors": [], "alive": True, "data": None})
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
    db.chunks.save(chunk)
    return json.dumps({"result": "okay"})

@app.route('/chunks_expired', methods=['POST'])
def chunks_expired():
    data = flask.request.json
    if not get_user(to_id(data['user']), data['secret']):
        return json.dumps({"error": "bad_login"})
    chunks = list(db.chunks.find({"mirrors": {"$in": [to_id(data['user'])]}, "alive": False}))
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
    chunk['data'] = None
    chunk['mirrors'].append(to_id(data['user']))
    db.chunks.save(chunk)
    return chunk_data

