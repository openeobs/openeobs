# Part of Open eObs. See LICENSE file for full copyright and licensing details.
__author__ = 'colin'
import gevent
import random
import threading
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
import logging
import openerp
_logger = logging.getLogger(__name__)


class PlotApplication(WebSocketApplication):
    def on_open(self):
        for i in xrange(10000):
            self.ws.send("0 %s %s\n" % (i, random.random()))
            gevent.sleep(0.1)

    def on_close(self, reason):
        print "Connection Closed!!!", reason




class NHWebSocketServer(object):

    port = 8000
    interface = '0.0.0.0'
    resource = None

    def gen_routes(self):
        return Resource({
            '/data': PlotApplication
        })


    def websocket_thread(self):
        def app(e, s):
            return self.app(e, s)
        self.httpd = WebSocketServer((self.interface, self.port), self.routes)
        self.httpd.serve_forever()

    def websocket_spawn(self):
        t = threading.Thread(target=self.websocket_thread, name="openerp.service.websocket")
        t.setDaemon(True)
        t.start()
        _logger.info('Websocket service (gevent) running on %s:%s', self.interface, self.port)

    def start(self):
        self.routes = self.gen_routes()
        self.websocket_spawn()


meh = NHWebSocketServer()
meh.start()