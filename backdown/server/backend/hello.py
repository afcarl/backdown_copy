from backend import app, db, templ8

@app.route('/')
def hello():
    return templ8("hello.html", {"name": "world"})
