import socketio
import eventlet
from constants import errors
from threading import Event
from flask import Flask, request, jsonify
from urllib.parse import parse_qs

sio = socketio.Server()
app = Flask(__name__)
eventlet.monkey_patch()
servers = {}


@app.before_request
def before_request():
    if not servers:
        return jsonify(errors['any-server'])


@app.route('/post', methods=['POST'])
def post():
    print(request.form['name'])
    print(request.form['email'])
    return 'ok'


@app.route('/file/<filename>')
def get(filename):
    ev = Event()
    result = None

    def ack(file):
        nonlocal result
        nonlocal ev
        result = file
        ev.set()  # unblock HTTP route

    sio.emit('download-file', filename, room=servers[0], callback=ack)
    ev.wait()  # blocks until ev.set() is called
    return jsonify(result)


@sio.on('connect')
def connect(sid, environ):
    query = parse_qs(environ.get('QUERY_STRING'))
    id = query['id'][0]
    servers[sid] = id


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

# wrap Flask application with socketio's middleware
app = socketio.Middleware(sio, app)
# deploy as an eventlet WSGI server
eventlet.wsgi.server(eventlet.listen(('', 8000)), app)