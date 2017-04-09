import socketio
import eventlet
from flask import Flask, request

sio = socketio.Server()
app = Flask(__name__)


@app.route('/post', methods=['POST'])
def post():
    print(request.form['name'])
    print(request.form['email'])
    return 'ok'


@app.route('/file/<filename>')
def get(filename):
    def ack(file):
        print (file)
    sio.emit('download-file', filename, callback=ack)



@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)
    print('environ', environ)


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    # wrap Flask application with socketio's middleware
    app = socketio.Middleware(sio, app)
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)