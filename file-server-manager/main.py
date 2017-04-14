import socketio
import eventlet
import utils
from constants import errors
from threading import Event
from flask import Flask, request, jsonify
from urllib.parse import parse_qs
from pymongo import MongoClient

sio = socketio.Server()
app = Flask(__name__)
eventlet.monkey_patch()
mongo_cli = MongoClient('localhost', 27017)
mongo_db = mongo_cli['file_server']
mongo_coll = mongo_db['files']

servers = []


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
    file_doc = mongo_coll.find_one({'filename': filename})

    if not file_doc:
        return jsonify(errors['file-not-found'])

    server = utils.first_by_property(servers, 'id', file_doc['server'])

    if not server:
        return jsonify(errors['server-unavailable'])

    ev = Event()
    response = None

    def ack(file64):
        nonlocal response
        nonlocal ev
        response = {
            'codRetorno': 0,
            'descricaoRetorno': file64
        }
        ev.set()  # unblock HTTP route

    sio.emit('download-file', filename, room=server['sid'], callback=ack)
    ev.wait()  # blocks until ev.set() is called
    return jsonify(response)


# Event dispatched when a file-server is connected, add the server to the list
@sio.on('connect')
def connect(sid, environ):
    query = parse_qs(environ.get('QUERY_STRING'))
    id = query['id'][0]
    files = mongo_coll.count({'server': id})
    server = {
        'id': id,
        'files': files,
        'sid': sid
    }
    servers.append(server)


@sio.on('disconnect')
def disconnect(sid):
    server = utils.first_by_property(servers, 'sid', sid)
    servers.remove(server)

# wrap Flask application with socketio's middleware
app = socketio.Middleware(sio, app)
# deploy as an eventlet WSGI server
eventlet.wsgi.server(eventlet.listen(('', 8000)), app)