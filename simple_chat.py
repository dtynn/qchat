#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, './modules')

from gevent import monkey
monkey.patch_all()

import logging

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)1.1s %(asctime)1.19s %(module)s:%(lineno)d] %(message)s')


class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    def on_nickname(self, nickname):
        self.request['nicknames'].append(nickname)
        self.socket.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', self.request['nicknames'])
        # Just have them join a default-named room
        self.join('main_room')
        return

    def recv_disconnect(self):
        # Remove nickname from the list.
        nickname = self.socket.session['nickname']
        self.request['nicknames'].remove(nickname)
        self.broadcast_event('announcement', '%s has disconnected' % nickname)
        self.broadcast_event('nicknames', self.request['nicknames'])

        self.disconnect(silent=True)
        return

    def on_user_message(self, msg):
        self.emit_to_room('main_room', 'msg_to_room',
                          self.socket.session['nickname'], msg)
        return

    def recv_message(self, message):
        print "PING!!!", message
        return message

    def on_upload(self, data):
        return ['token']


class Application(object):
    def __init__(self):
        self.buffer = []
        # Dummy request object to maintain state between Namespace
        # initialization.
        self.request = {
            'nicknames': [],
        }
        return

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')

        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>Welcome. '
                    'Try the <a href="/chat.html">chat</a> example.</h1>']

        if path.startswith('static/') or path == 'chat.html' or path =='simple_chat.html':
            try:
                data = open(path).read()
            except Exception as e:
                logging.error(e)
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'': ChatNamespace}, self.request)
        else:
            return not_found(start_response)


def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print 'Listening on port 8080 and on port 843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 18080), Application(),
                   resource="socket.io", policy_server=True,
                   policy_listener=('0.0.0.0', 843)).serve_forever()