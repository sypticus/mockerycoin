import socketio

sio = socketio.Client()

sio.connect('http://localhost:8001')
sio.emit("aaa")
sio.wait()