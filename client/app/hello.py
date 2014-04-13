from app import app, templ8

@app.route('/')
def hello():
    return templ8("hello.html", {"name": "world"})
