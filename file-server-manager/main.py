import socketio
import eventlet
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

    file_obj = {
        'filename': filename,
        'server': server['id']
    }

    ev = eventlet.event.Event()

    def ack(err):
        if err:
            res = errors['internal-error']
        else:
            res = {
                'codRetorno': 0,
                'descricaoRetorno': 'Arquivo Inserido'
            }
            mongo_coll.insert_one(file_obj)
            server['files'] += 1

        ev.send(res)

    sio.emit('upload-file', request.form, room=server['sid'], callback=ack)

    # blocks until ev.set() is called
    response = ev.wait()
    return jsonify(response)


@app.route('/file/<filename>', methods=['GET', 'DELETE'])
def get_delete(filename):
    file_doc = mongo_coll.find_one({'filename': filename})

    if not file_doc:
        return jsonify(errors['file-not-found'])

    server = utils.first_by_property(servers, 'id', file_doc['server'])

    if not server:
        return jsonify(errors['server-unavailable'])

    ev = eventlet.event.Event()

    # Callback to be executed after server-file responds
    def get(file64):
        res = {
            'codRetorno': 0,
            'descricaoRetorno': file64
        }
        ev.send(res)

    def delete(err):
        if err:
            res = errors['internal-error']
        else:
            res = {
                'codRetorno': 0,
                'descricaoRetorno': 'Arquivo deletado'
            }
            mongo_coll.delete_one(file_doc)
            server['files'] -= 1
        ev.send(res)

    if request.method == 'DELETE':
        sio.emit('delete-file', filename, room=server['sid'], callback=delete)
    else:
        sio.emit('download-file', filename, room=server['sid'], callback=get)

    # blocks until ev.set() is called
    response = ev.wait()
    return jsonify(response)


# Event dispatched when a file-server is connected, add the server to the list and balance
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
    servers_to_balance = utils.get_servers_to_balance(servers)

    if servers_to_balance:
        balance_servers(servers_to_balance)


def balance_servers(servers_to_balance):

    def transfer(res):
        sio.emit('upload-file', res, room=res['server_to_add'])

    # iterate over servers that has more files than expected
    for server_to_remove in servers_to_balance['servers_high']:
        # get the number of files that need to be moved
        files_to_move = server_to_remove['files'] - servers_to_balance['average']
        for i in range(0, files_to_move):
            # get the file to be moved
            file_doc = mongo_coll.find_one({'server': server_to_remove['id']})
            # get the server to receive the file
            server_to_add = servers_to_balance['servers_low'][0]
            # set variable to be emitted
            req_content = {
                'server_to_add': server_to_add['sid'],
                'filename': file_doc['filename']
            }
            # emit transfer-file
            sio.emit('transfer-file', req_content, room=server_to_remove['sid'], callback=transfer)

            # update references
            server_to_remove['files'] -= 1
            server_to_add['files'] += 1
            # update mongo
            mongo_coll.update_one(
                {'_id': file_doc['_id']},
                {'$set': {'server': server_to_add['id']}},
                upsert=False)
            # remove from array, then in the next iteration, will take next servers_low element
            if server_to_add['files'] == servers_to_balance['average']:
                del servers_to_balance['servers_low'][0]


# Event dispatched when a file-server is disconnected, remove the server from the list
@sio.on('disconnect')
def disconnect(sid):
    server = utils.first_by_property(servers, 'sid', sid)
    servers.remove(server)

# wrap Flask application with socketio's middleware
app = socketio.Middleware(sio, app)
# deploy as an eventlet WSGI server
eventlet.wsgi.server(eventlet.listen(('', config['port'])), app)