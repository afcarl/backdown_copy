from app import app, templ8

@app.route('/')
def hello():
    return flask.redirect('/ui')
