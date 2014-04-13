import requests as r
import copy
import json

root = 'http://localhost:5000'

def postjson(endpoint, payload):
    print '\n'
    print endpoint, payload
    res = r.post(root+endpoint, data=json.dumps(payload), headers={"Content-Type": "application/json"}).json()
    print res
    return res

alice = postjson('/sign_up', {})
bob = postjson('/sign_up', {})

alice_chunks = {"c1": open('test_binary.png').read(), "c2": "Goodnight, moon"}

def withuser(user, params):
    np = copy.copy(params)
    np['user'] = user['user']
    np['secret'] = user['secret']
    return np

assert postjson('/update_chunks', withuser(alice, {"created": alice_chunks.keys(), "deleted": []}))['result']=='okay'

# try uploading:
def let_alice_upload():
    chunks = postjson('/chunks_to_upload', withuser(alice, {}))['chunks']
    if len(chunks)==0:
        return False
    status = r.post(root+'/upload_chunk/'+chunks[0]['key'], data=alice_chunks[chunks[0]['chunk_id']], headers={"Content-Type": "application/octet-stream"}).status_code
    assert status==200
    return True

assert let_alice_upload()
assert let_alice_upload()==False

assert postjson('/chunks_to_download', withuser(bob, {"friends": []}))['chunks']==[]

def let_bob_download():
    chunks = postjson('/chunks_to_download', withuser(bob, {"friends": [alice['user']]}))['chunks']
    if len(chunks)==0:
        return False
    assert chunks[0]['user']==alice['user']
    res = r.post(root+'/download_chunk/'+chunks[0]['key'], data=json.dumps(withuser(bob, {})), headers={"Content-Type": "application/json"}).content
    print type(res)
    print res, 'vs', alice_chunks[chunks[0]['chunk_id']]  
    assert res == alice_chunks[chunks[0]['chunk_id']]    
    return True

assert let_bob_download()
assert let_bob_download()==False
assert let_alice_upload()
assert let_bob_download()

del alice_chunks['c2']
assert postjson('/update_chunks', withuser(alice, {"created": [], "deleted": ["c2"]}))['result']=='okay'

assert postjson('/chunks_expired', withuser(alice, {}))['expired']==[]
assert postjson('/chunks_expired', withuser(bob, {}))['expired']==[{"user": alice['user'], "chunk_id": "c2"}]
assert postjson('/chunks_expired', withuser(bob, {}))['expired']==[] # the first call erases the data

assert postjson('/restore', withuser(alice, {}))['result']=='okay'
files_to_restore = postjson('/files_to_restore', withuser(bob, {"friends": [alice['user']]}))['chunks']
assert files_to_restore[0]['chunk_id']=='c1'
status = r.post(root+'/upload_chunk/'+files_to_restore[0]['key'], data=alice_chunks['c1'], headers={"Content-Type": "application/octet-stream"}).status_code
assert status==200

restorables = postjson('/get_restorable_chunks', withuser(alice, {}))['chunks']
assert restorables[0]['chunk_id']=='c1'
res = r.post(root+'/download_chunk/'+restorables[0]['key'], data=json.dumps(withuser(alice, {})), headers={"Content-Type": "application/json"}).content
assert res == alice_chunks['c1']
assert postjson('/files_to_restore', withuser(bob, {"friends": [alice['user']]}))['chunks']==[]
assert postjson('/get_restorable_chunks', withuser(alice, {}))['chunks']==[]


print "Done"
