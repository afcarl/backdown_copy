from app import app, templ8
import flask

@app.route('/')
def hello():
    return flask.redirect('/ui')
