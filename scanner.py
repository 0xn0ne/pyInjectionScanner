import argparse
import os
import re
from typing import List

import injection


def how_about_it(requests: List[injection.Request]):
    for request in requests:
        exists = False
        querys = []
        querys.extend(re.findall(r'([^?=&#/\\]+)=', request.uri))
        if request._raw_data and isinstance(request.data, str):
            querys.extend(re.findall(r'([^?=&#/\\]+)=', request.data))
        if request._raw_headers and 'Cookie' in request._raw_headers:
            querys.extend(re.findall(r'([^?=&#/\\;\s]+)=', request._raw_headers['Cookie']))
        for q in querys:
            res = injection.how_about_it(request, querys=[q])
            if isinstance(res, str):
                print('[+] Find in', request._raw_uri)
                print('[+] Method: {}; About: {}'.format(request.method, q))
                exists = True
        if not exists:
            print('[-] Method: {}, Url: {} python code injection not detected'.format(request.method, request._raw_uri))


def main(paths: List[str]):
    l_request: List[injection.Request] = []
    for path in paths:
        l_file = []
        if os.path.isdir(path):
            for f in os.listdir(path):
                l_file.append(os.path.join(path, f))
        else:
            l_file.append(path)
        for f in l_file:
            r = injection.Request.from_file(f)
            if not r:
                with open(f) as _f:
                    for uri in _f.read().split():
                        uri = uri.strip()
                        if uri.startswith('http://') or uri.startswith('https://'):
                            l_request.append(injection.Request(uri))
            else:
                l_request.append(r)

    how_about_it(l_request)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--paths', nargs='+', help='Files or folders path')

    args = parser.parse_args()
    main(args.paths)
