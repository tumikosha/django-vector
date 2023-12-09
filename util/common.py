import hashlib
import json
import uuid
from urllib.parse import urlparse

import dateparser
from sentence_transformers import SentenceTransformer
from lxml import html as html_module

from tumi_tools.try_wrappers import TRIAL

encoder = SentenceTransformer("all-MiniLM-L6-v2")


def to_int_none(string_to_int: None | str) -> None | int:
    try:
        return int(float(string_to_int))
    except:
        return None


def to_date_none(s: str):
    with TRIAL:
        return dateparser.parse(s)
    return None


def string_2_uuid(val: str) -> uuid.UUID:
    """ generates uuid from random string """
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)


def clean_text(txt: str) -> str:
    if txt is None: return None
    return txt.replace("\n", "").replace("  ", " ").strip()


def html_2_text(html_content: object, length_limit: object = 15) -> object:
    if html_content is None: return None
    tree = html_module.fromstring(html_content)
    text_list = tree.xpath(
        '//text()[not(ancestor::script) and (not(ancestor::style)) and (not(ancestor::a))  and normalize-space()]')
    text_list = [text.strip() for text in text_list if len(text) > length_limit and text.find("cookies") == -1]
    return "\n".join(text for text in text_list if text != "")


def first_item_or_none(lst: list, default=None) -> None | object:
    exp = (lst or [None])[0]
    if exp is None: return default
    return exp

    #
    # if lst is None: return None
    # if len(lst) == 0: return None
    # return lst[0]


def html_2_txt_tit_fav(html_content: object, length_limit: object = 15) -> object:
    if html_content is None: return None
    tree = html_module.fromstring(html_content)
    description = tree.xpath('//meta[@name="description"]/@content')
    title = first_item_or_none(tree.xpath('//title/text()[1]'))
    favico = tree.xpath('//*[contains(@href,"favico")]/@href')
    h1 = tree.xpath('//h1/text()')
    h2 = tree.xpath('//h2/text()')

    text_list = tree.xpath(
        '//text()[not(ancestor::script) and (not(ancestor::style)) and (not(ancestor::a))  and normalize-space()]')
    text_list = [text.strip() for text in text_list if len(text) > length_limit and text.find("cookies") == -1]
    txt = "\n".join(text for text in text_list if text != "")
    return txt, clean_text(title), favico, description, h1, h2


def prepare_img_path(domain, logo):
    if logo is None: return None

    logo = str(logo).strip("'").strip('"')
    host = domain if urlparse(logo).hostname is None else urlparse(logo).hostname
    if urlparse(logo).path.startswith("/"):
        path = urlparse(logo).path
    else:
        path = "/" + urlparse(logo).path
    res = host + path
    return res.replace("//", "/")


def final(companies: list) -> list:
    """ processing companies  before pass to design """
    res = []
    for company in companies:
        # unpacking links..
        # print("company.calendly:", company.calendly)
        try:
            arr = json.loads(company.calendly.replace("'", '"'))
            company.links = arr
            company.link0 = arr[0]
        except:
            arr = []  # ????
            company.links = arr
            company.link0 = None

        res.append(company)
    return res


def clear_phones(phones: str):
    ph = str(phones).replace("ph:", "").replace("nan","").replace("None","")
    if ph=="": return None
    return ph

    # print(clear_phones("ph:+1-647-894-9580;+1-905-597-0405;+1-647-490-4555"))
    # print(clear_phones("ph:"))
    # print(clear_phones("nan"))

