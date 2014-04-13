import os
from flask import Flask
import sys

app = Flask(__name__)

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('app', 'templates'))
def templ8(name, vars):
	return env.get_template(name).render(vars)

def log(txt):
	print txt
	sys.stdout.flush()

app.debug = True
import hello
import ui
import sync
import stats
import restore
sync.start_sync_task()

