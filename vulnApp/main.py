#!/bin/python3
import random
from io import StringIO

import sys
import tornado.ioloop
import tornado.web

INJECTION_PATH = '/injection'
PORT = 8080


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(
            f'''<h1 align="center">Hello world!</h1>
<p align="center">Please enter <a href="{INJECTION_PATH}">{INJECTION_PATH}</a> for testing</p>''')


class InjectionHandler(tornado.web.RequestHandler):
    def get(self):
        stdout = sys.stdout
        sys.stdout = t_io = StringIO()
        p1 = self.get_argument('p1', '110')
        p2 = self.get_argument('p2', '120')
        eval_p2 = ''
        eval_p1 = ''
        eval_visited = ''
        try:
            p1 = eval(p1)
            if p1:
                eval_p1 = p1
        except Exception:
            pass
        try:
            p2 = eval(p2)
            if p2:
                eval_p2 = p2
        except Exception:
            pass
        try:
            visited = eval(self.get_cookie('visited', '1'))
            if visited:
                eval_visited = visited + 1
        except Exception:
            pass

        msg = t_io.getvalue()
        sys.stdout = stdout
        self.set_cookie('Visited', str(eval_visited))
        self.write('''<h1 align="center">Welcome to test!</h1>
<p align="center">P1 handle: {}</p>
<p align="center">P2 handle: {}</p>
<p align="center">Message handle: {}</p>'''.format(eval_p1, eval_p2, msg))

    def post(self):
        stdout = sys.stdout
        sys.stdout = t_io = StringIO()
        p1 = self.get_argument('p1', '0')
        p2 = self.get_argument('p2', '1')
        eval_p2 = ''
        eval_p1 = ''
        eval_rand = ''
        try:
            p1 = eval(p1)
            if p1:
                eval_p1 = p1
        except Exception:
            pass
        try:
            p2 = eval(p2)
            if p2:
                eval_p2 = p2
        except Exception:
            pass
        try:
            rand = eval(self.get_cookie('random', str(random.randint(100000, 999999))))
            if rand:
                eval_rand = rand
        except Exception:
            pass

        msg = t_io.getvalue()
        sys.stdout = stdout
        self.set_cookie('random', str(eval_rand))
        self.write('''<h1 align="center">Welcome to test!</h1>
<p align="center">P1 handle: {}</p>
<p align="center">P2 handle: {}</p>
<p align="center">Message handle: {}</p>'''.format(eval_p1, eval_p2, msg))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/injection", InjectionHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(PORT)
    print('Web server startup, Access to http://127.0.0.1:{}'.format(PORT))
    tornado.ioloop.IOLoop.current().start()

