from app import app
import flask
import data
import requests as r
from sync import postjson

@app.route('/restore/<user>/<secret>')
def restore(user, secret):
    conf = data.get_conf()
    conf['user'] = user
    conf['secret'] = secret
    conf['friends'] = []
    postjson('/restore', {"user": conf['user'], "secret": conf['secret']})
    data.save_conf(conf)
    return flask.redirect('/ui?msg=Now%20pick%20a%20folder%20and%20wait%20for%20your%20files:')
    
