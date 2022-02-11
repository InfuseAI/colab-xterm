import asyncio
from typing import List
import tornado.ioloop
import tornado.web
import base64
from ptyprocess import PtyProcess
import os
from . import manager


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('client/dist/index.html')


class StdoutHandler(tornado.web.RequestHandler):
    def initialize(self, process):
        self.process = process

    async def get(self):
        loop = asyncio.get_event_loop()
        try:
            b = await loop.run_in_executor(None, lambda:  self.process.read(4*1024*1024))
            self.write(b)
            await self.flush()
        except EOFError as e:
            pass


class StdinHandler(tornado.web.RequestHandler):
    def initialize(self, process):
        self.process = process

    async def get(self, base64str):
        data = base64.b64decode(base64str)
        self.process.write(data)


class ResizeHandler(tornado.web.RequestHandler):
    def initialize(self, process):
        self.process = process

    async def get(self):
        rows = int(self.get_argument('rows'))
        cols = int(self.get_argument('cols'))
        self.process.setwinsize(rows, cols)


class XTerm:
    def __init__(self, argv: List, port=10000):
        self.argv = argv
        self.port = port

    def open(self):
        port = self.port
        argv = self.argv
        if not argv or len(argv) == 0:
            argv = [os.getenv("SHELL", '/bin/sh')]

        try:
            process = PtyProcess.spawn(argv)
            staticFolder = os.path.join(
                os.path.dirname(__file__), "client/dist")
        except Exception as e:
            manager.write_info_file(os.getpid(), False, str(e))

        try:
            app = tornado.web.Application([
                (r"/out", StdoutHandler, dict(process=process)),
                (r"/in/(.*)", StdinHandler, dict(process=process)),
                (r"/resize", ResizeHandler, dict(process=process)),
                (r"/(.*\.js)", tornado.web.StaticFileHandler,
                 {"path": staticFolder}),
                (r'/', MainHandler),
            ])
            app.listen(port, "127.0.0.1")
            print(f"🚀  Listen to {port}")
            manager.write_info_file(os.getpid(), True)
        except Exception as e:
            manager.write_info_file(os.getpid(), False, str(e))
            raise e

        tornado.ioloop.IOLoop.current().start()
