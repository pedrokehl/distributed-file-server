import socketio
import eventlet
from threading import Event
from flask import Flask, request, jsonify
from urllib.parse import parse_qs
from pymongo import MongoClient
import utils
from constants import errors, config

sio = socketio.Server()
app = Flask(__name__)
eventlet.monkey_patch()

mongo_cli = MongoClient(config['mongo_server'], config['mongo_port'])
mongo_db = mongo_cli['file_server']
mongo_coll = mongo_db['files']

servers = []
current_balances = 0


@app.before_request
def before_request():
    if not servers:
        return jsonify(errors['any-server'])


@app.route('/file', methods=['POST'])
def post():
    filename = request.form['filename']
    file_doc = mongo_coll.find_one({'filename': filename})

    if file_doc:
        return jsonify(errors['file-exists'])

    server = utils.element_by_small_value(servers, 'files')

    fileObj = {
        'filename': filename,
        'path': filename,
        'server': server['id']
    }

    ev = Event()
    response = None

    def ack(err):
        nonlocal response
        nonlocal ev
        nonlocal server

        if err:
            response = errors['internal-error']
        else:
            response = {
                'codRetorno': 0,
                'descricaoRetorno': 'Arquivo Inserido'
            }
            mongo_coll.insert_one(fileObj)
            server['files'] += 1
        ev.set()

    sio.emit('upload-file', request.form, room=server['sid'], callback=ack)

    # blocks until ev.set() is called
    ev.wait()
    return jsonify(response)


@app.route('/file/<filename>', methods=['GET', 'DELETE'])
def get_delete(filename):
    file_doc = mongo_coll.find_one({'filename': filename})

    if not file_doc:
        return jsonify(errors['file-not-found'])

    server = utils.first_by_property(servers, 'id', file_doc['server'])

    if not server:
        return jsonify(errors['server-unavailable'])

    ev = Event()
    response = None

    # Callback to be executed after server-file responds
    def get(file64):
        nonlocal response
        nonlocal ev
        response = {
            'codRetorno': 0,
            'descricaoRetorno': file64
        }
        ev.set()

    def delete(err):
        nonlocal response
        nonlocal ev
        nonlocal server

        if err:
            response = errors['internal-error']
        else:
            response = {
                'codRetorno': 0,
                'descricaoRetorno': 'Arquivo deletado'
            }
            mongo_coll.delete_one(file_doc)
            server['files'] -= 1
        ev.set()

    if request.method == 'DELETE':
        sio.emit('delete-file', filename, room=server['sid'], callback=delete)
    else:
        sio.emit('download-file', filename, room=server['sid'], callback=get)

    # blocks until ev.set() is called
    ev.wait()
    return jsonify(response)


# Event dispatched when a file-server is connected, add the server to the list
@sio.on('connect')
def connect(sid, environ):
    query = parse_qs(environ.get('QUERY_STRING'))
    id = query['id'][0]

    # Validate if file-server id is already in use.
    if utils.first_by_property(servers, 'id', id):
        return False

    files = mongo_coll.count({'server': id})
    server = {
        'id': id,
        'files': files,
        'sid': sid
    }
    servers.append(server)
    servers_to_balance = utils.get_servers_to_balance(servers, current_balances)

    if servers_to_balance:
        # TODO: apply balance with mongo + socket.io
        print(servers_to_balance)


# Event dispatched when a file-server is disconnected, remove the server from the list
@sio.on('disconnect')
def disconnect(sid):
    server = utils.first_by_property(servers, 'sid', sid)
    servers.remove(server)

# wrap Flask application with socketio's middleware
app = socketio.Middleware(sio, app)
# deploy as an eventlet WSGI server
eventlet.wsgi.server(eventlet.listen(('', config['port'])), app)