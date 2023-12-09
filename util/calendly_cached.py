import datetime

import requests

from scanners.calendly_page import CalendlyPage
from scripts.constants import MONGO_URI
from tumi_tools.mongo_cache import mongo_cache


@mongo_cache(MONGO_URI, db_name="fixiegen", collection="cache_cal_nick_parsed",
             ttl=datetime.timedelta(days=30), verbose=True)
def get_events_by_nick(nick: str, detach=False, headless=True, proxy_nest=None, pre_check=False) -> object:
    """ parse calendly account page and save parsed results
            HTML is not cached
    """
    if pre_check:
        url = f"https://calendly.com/{nick}"
        response = requests.get(url)
        if response.status_code != 200:
            return False, response.status_code, {}

    print("headle", headless)
    page = CalendlyPage(proxy_nest=proxy_nest, detach=detach, headless=headless)
    # self.row['_id'] = nick
    # is_good, status, err = page.check_status()
    is_good, status, err = page.scan(nick)
    # print(page.row)
    page.browser.quit()
    return is_good, status, err


DENIED_NICKS = set(["integration", "favicon.svg", " icons", "favicon-32x32.png", "", "static", "hc"])


def clear_nick_list(nick_list):
    nick_list = [CalendlyPage.cal_nick_from_url(nick) for nick in nick_list]
    nick_list = set(nick_list)  # remove dublicated nicknames
    nick_list = nick_list - DENIED_NICKS
    return nick_list


def get_events_by_nicks(nick_list: list, headless=True, detach=False, proxy_nest=None, pre_check=False) -> object:
    """  USe IT universal method"""
    if nick_list is None: return None
    if isinstance(nick_list, str):
        nick_list = [nick_list]
    result = []
    for nick in clear_nick_list(nick_list) :
        is_good, status, res = get_events_by_nick(
            CalendlyPage.cal_nick_from_url(nick),
            detach=detach, headless=headless, proxy_nest=proxy_nest, pre_check=pre_check)

        if is_good:
            result.append(res)
    return result
