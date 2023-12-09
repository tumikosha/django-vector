class Point:
    def __new__(cls, *args, **kwargs):
        print("1. Create a new instance of Point.")
        return super().__new__(cls)

    def __init__(self, x, y):
        print("2. Initialize the new instance of Point.")
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"{type(self).__name__}(x={self.x}, y={self.y})"


point = Point(21, 42)
print(point)

from selenium.webdriver.common.by import By
from lxml import html as html_module
import proxies
import tumi_tools.tumi_selenium as ts
from enum import Enum


class Response:
    status_code = None
    html = None
    text = None
    kwargs = None

    def html_2_text(self, html_content, min_length=15):
        if html_content is None: return None
        tree = html_module.fromstring(html_content)
        text_list = tree.xpath(
            '//text()[not(ancestor::script) and (not(ancestor::style)) and (not(ancestor::a))  and normalize-space()]')
        text_list = [text.strip() for text in text_list if len(text) > min_length]
        return "\n".join(text for text in text_list if text != "")

    def __init__(self, code, src, **kwargs):
        self.status_code = code
        self.html = src
        self.kwargs = kwargs
        print(kwargs)
        try:
            self.text = self.html_2_text(src, min_length=1) if src is not None else None
        except:
            self.text = None

    def __repr__(self) -> str:
        html_len = len(self.html) if self.html is not None else None
        text_len = len(self.text) if self.text is not None else None
        html_start = self.html[:10] if self.html is not None else None
        text_start = self.text[:10] if self.text is not None else None
        return f"{type(self).__name__}(status_code={self.status_code}, {html_len}::> html={html_start}..., {text_len}::>text={text_start}... {self.kwargs})"


print(Response(404, "123", h2=""))
print(Response(404, ""))
print(Response(404, None))
print(Response(404, "<html<<"))
print(Response(404, "<P>Hello</p>"))
