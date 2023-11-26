from src.wsgi import app
from flask import Flask, request, escape


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/greet')
def greet():
    name = request.args['name']
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <h1>Hi {}</h1>
    </body>
    </html>'''.format(escape(name))