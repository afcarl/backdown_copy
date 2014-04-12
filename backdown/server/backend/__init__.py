import os
from flask import Flask
import pymongo

app = Flask(__name__)

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('backend', 'templates'))
def templ8(name, vars):
	return env.get_template(name).render(vars)

if 'MONGOHQ_URL' in os.environ:
	db = pymongo.MongoClient(os.environ['MONGOHQ_URL']).app22686072
else:
	db = pymongo.MongoClient().backdown

if 0:
    db.users.remove({})
    db.chunks.remove({})

app.debug = True
import hello
import server
