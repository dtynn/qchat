from gevent import monkey;
from modules.socketio import namespace, server

monkey.patch_all()

from bottle import Bottle, request
from modules.socketio import socketio_manage

app = Bottle()

class Hello(namespace.BaseNamespace):

    def on_hello(self, data):
        print "hello", data
        self.emit('greetings', {'from': 'sockets'})


@app.route('/socket.io/<arg:path>')
def socketio(*arg, **kw):
    socketio_manage(request.environ, {'': Hello}, request=request)
    return "out"


if __name__ == '__main__':
    server.SocketIOServer(
        ('localhost', 9090), app, policy_server=False).serve_forever()
