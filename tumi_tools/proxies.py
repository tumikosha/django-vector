import json
from urllib import request

import datetime
import random
import time
import hashlib, uuid
from abc import ABC, abstractmethod
import requests
from fake_useragent import UserAgent
from tumi_tools.try_wrappers import TRIAL
import urllib
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import pandas as pd


class Proxy:
    @abstractmethod
    def next(self, prefix="https://") -> str:
        pass

    @abstractmethod
    def random(self, prefix="https://") -> str:
        pass

    def get(self, url, proxy=None):
        if proxy is None:
            self.last_proxy = self.next(prefix="http://")
        else:
            self.last_proxy = proxy
        proxy_servers_ = {'http': self.last_proxy}
        ua = UserAgent()
        print(url, proxy_servers_, ua.chrome)
        header = {'User-Agent': str(ua.chrome)}
        headers = header
        return requests.get(url, headers=header, proxies=proxy_servers_)


class RotatingProxy(Proxy):
    def __init__(self, file_name):
        self.counter = 0
        with open(file_name, "r") as f:
            self.proxies = [px.strip() for px in f.readlines()]
        # print("proxies loaded:", self.counter)

    def size(self):
        return len(self.proxies)

    def next(self, prefix="https://"):
        px = self.proxies[self.counter]
        self.counter = (self.counter + 1) if self.counter < len(self.proxies) - 1 else 0
        return px if px.find(prefix) > -1 else prefix + px

    def random(self, prefix="https://"):
        rnd = random.randrange(len(self.proxies) - 1)
        px = self.proxies[rnd]
        return px if px.find(prefix) > -1 else prefix + px

    def get(self, url, proxy=None, timeout=5):
        if proxy is None:
            self.last_proxy = self.next(prefix="http://")
        else:
            self.last_proxy = proxy
        proxy_servers_ = {'http': self.last_proxy}
        ua = UserAgent()
        print(url, proxy_servers_, ua.chrome)
        header = {'User-Agent': str(ua.chrome)}
        headers = header
        return requests.get(url, headers=header, proxies=proxy_servers_, timeout=timeout)

    def check_all(self):
        bad = []
        good = []
        for proxy in self.proxies:
            # resp = self.get("http://dirs.info")
            resp = self.get("https://www.wikipedia.org/", proxy=proxy)
            if resp.status_code == 200:
                good.append(proxy)
            else:
                bad.append(proxy)
            print(proxy, resp)
        print("GOOD:", len(good))
        print("BAD:", len(bad))
        return good, bad


class PandasRotating(RotatingProxy):

    def __init__(self, file_name):
        self.counter = 0
        df_emails = pd.read_csv(file_name)

        # self.proxies = df_emails.to_dict('list')
        self.proxies = df_emails.to_dict('record')
        # print("proxies loaded:", self.counter)

    def next(self, prefix=""):
        px = self.proxies[self.counter]
        self.counter = (self.counter + 1) if self.counter < len(self.proxies) - 1 else 0
        return prefix + str(px)


class RotatingProxyHTTP(Proxy):
    def __init__(self, file_name):
        self.counter = 0
        df_emails = pd.read_csv(file_name)

        # self.proxies = df_emails.to_dict('list')
        self.proxies = df_emails.to_dict('record')
        # print("proxies loaded:", self.counter)

    def next(self, prefix=""):
        return ask_new_proxy()

    def random(self, prefix="https://"):
        return ask_new_proxy()


class StormProxies(Proxy):
    def __init__(self, file_name):
        self.counter = 0
        with open(file_name, "r") as f:
            self.proxies = [px.strip() for px in f.readlines()]

    def size(self):
        return len(self.proxies)

    def next(self, prefix="https://"):
        px = self.proxies[self.counter]
        self.counter = (self.counter + 1) if self.counter < len(self.proxies) - 1 else 0
        return px if px.find(prefix) > -1 else prefix + px

    def random(self, prefix="https://"):
        rnd = random.randrange(len(self.proxies) - 1)
        px = self.proxies[rnd]
        return px if px.find(prefix) > -1 else prefix + px

    def get_with_proxy(self, proxy, url):
        proxy_servers_ = {'http': proxy}
        ua = UserAgent()
        print(url, proxy_servers_, ua.chrome)
        header = {'User-Agent': str(ua.chrome)}
        try:
            resp = requests.get(url, headers=header, proxies=proxy_servers_)
            return resp
        except Exception as e:
            import collections
            Response = collections.namedtuple('Response', ['status_code', 'text'])
            print(str(e))
            return Response(None, str(e))


class ZenProxies(Proxy):
    def __init__(self, api_key: str):
        self.counter = 0
        self.api_key = api_key

    def size(self):
        return 1

    def next(self, prefix="http://"):
        return prefix + self.api_key + ":@proxy.zenrows.com:8001"

    def get(self, url):
        self.last_proxy = self.next(prefix="http://")
        proxy_servers_ = {'http': self.last_proxy}
        ua = UserAgent()
        print(url, proxy_servers_, ua.chrome)
        header = {'User-Agent': str(ua.chrome)}
        headers = header
        return requests.get(url, headers=header, proxies=proxy_servers_)

    def get_with_css(self, url, css='[{"wait": 16000}]', safe=''):
        # coded = urllib.parse.quote(css)
        coded = urllib.parse.quote(css, safe=safe)
        # print("coded:", coded)
        proxy = "http://" + self.api_key + ":js_render=true&js_instructions=" + coded + "@proxy.zenrows.com:8001"
        proxies = {"http": proxy, "https": proxy}
        ua = UserAgent()
        # print(url, proxies, ua.chrome)
        header = {'User-Agent': str(ua.chrome)}
        headers = header
        requests.packages.urllib3.disable_warnings()
        return requests.get(url, headers=header, proxies=proxies, verify=False)

    def random_session(self):
        id = int(hashlib.sha1(str(uuid.uuid4()).encode('utf-8')).hexdigest(), 16) % (10 ** 4)
        return self.api_key + ":session_id=" + str(id)
        # +str(int(hashlib.sha1(str(uuid.uuid4()).encode('utf-8')).hexdigest(), 16) % (10 ** 8))

    def session(self):
        id = self.random_session()
        # id = int(hashlib.sha1(uuid.uuid4().int))
        return self.api_key + ":session_id=" + str(id) + "@proxy.zenrows.com:8001"
        # return "http://" + self.api_key + ":session_id=" + str(id) + "@proxy.zenrows.com:8001"
        # e9964545a109988eb897cde4684877d2c7f806ff@proxy.zenrows.com:8001


class EmpireProxies(StormProxies):

    def __init__(self, file_name):
        self.counter = 0
        with open(file_name, "r") as f:
            self.proxies = [px.strip() for px in f.readlines()]
    #
    #     def next(self, prefix="https://"):
    #         px = self.proxies[self.counter]
    #         self.counter = (self.counter + 1) if self.counter < len(self.proxies) - 1 else 0
    #         return px if px.find(prefix) > -1 else prefix + px


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the request URL to extract query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Set the response status code
        self.send_response(200)

        # Set headers (optional)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        response_message = f""
        if "proxy" in parsed_url.path:
            response_message += f"{proxy_nest.next(prefix='')}"
        if "email" in parsed_url.path:
            response_message += f"{email_nest.next(prefix='')}"

        self.wfile.write(response_message.encode('utf-8'))


def ask_new_proxy(ip="localhost:9999"):
    resp = requests.get("http://" + ip + "/proxy")
    if resp.status_code == 200:
        return resp.text
    return None


def ask_new_email(ip="localhost:9999"):
    resp = requests.get("http://" + ip + "/email")
    if resp.status_code == 200:
        jsn = json.loads(resp.text.replace("'", '"'))
        return jsn
    return None, None


if __name__ == '__main__':
    #  https://63.141.236.210:19015
    # proxies = StormProxies("proxy.txt")
    proxy_nest = RotatingProxy("/home/tumi/instant.proxy")
    email_nest = PandasRotating("data/emails.csv")
    good, bad = proxy_nest.check_all()

    # host = 'localhost'
    # port = 9999
    #
    # # Create and run the HTTP server with the custom request handler
    # try:
    #     server = HTTPServer((host, port), MyRequestHandler)
    #     print(f"Server started on http://{host}:{port}")
    #     server.serve_forever()
    # except KeyboardInterrupt:
    #     print("\nServer stopped")
    #     server.shutdown()
