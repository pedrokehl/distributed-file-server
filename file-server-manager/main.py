import socketio
import eventlet
from flask import Flask
from flask import request

sio = socketio.Server()
app = Flask(__name__)


@app.route('/post', methods=['POST'])
def post():
    print(request.form['name'])
    print(request.form['email'])
    return 'ok'


@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    # wrap Flask application with socketio's middleware
    app = socketio.Middleware(sio, app)
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)