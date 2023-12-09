from typing import TypedDict, Tuple, Any

import time

from selenium.webdriver.common.by import By
from lxml import html as html_module

import tumi_tools.proxies
import tumi_tools.tumi_selenium as ts
from enum import Enum

from scanners.web_page import WebPage
from tumi_tools import proxies
from tumi_tools.name_util import Status, extract_name_from_intro
from tumi_tools.try_wrappers import TRIAL


class Response:
    status_code = None
    html = None
    text = None

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
        html_start = self.html[:20] if self.html is not None else None
        text_start = self.text[:20] if self.text is not None else None
        return f"{type(self).__name__}(status_code={self.status_code}, {html_len}::> html={html_start}..., {text_len}::>text={text_start}... {self.kwargs})"


def xpath(driver, path, attr):
    try:
        elem = driver.find_element(By.XPATH, path)
        if attr == 'text' or attr == "text()":
            return elem.text
        else:
            return elem.get_attribute[attr]
    except Exception as e:
        return None


browser = None
browser_use_count = 0


def scan(nickname: str, proxy_nest: proxies.Proxy | None, timeout=60, detach=False, headless=True,
         images=False, obligate=None, reuse: int = 1) -> Response:
    global browser, browser_use_count

    print(f"{nickname}...", end="")
    url = "https://calendly.com/" + nickname  # https://meetings.hubspot.com/oracle
    proxy = proxy_nest.next(prefix="") if proxy_nest is not None else None
    # browser = ts.new_auth_browser(proxy=proxy, detach=False, headless=True)
    if browser is None:
        browser = ts.new_auth_browser(proxy=proxy, detach=detach, headless=headless, images=images,
                                      extension=r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx'
                                      )
    elif browser_use_count > reuse:
        browser.quit()

        browser = ts.new_auth_browser(proxy=proxy, detach=detach, headless=headless, images=images,
                                      extension=r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx'
                                      )
        browser_use_count = 0
    browser_use_count += 1
    print("browser reused", browser_use_count)

    browser.set_page_load_timeout(timeout)
    try:
        browser.get(url)
        time.sleep(4)
    except Exception as e:
        print("--408-- # timeout :", url, proxy)
        return Response(408, str(e) + " ::>" + browser.page_source)

    if "Well, this is disappointing" in browser.page_source:
        print("--404-- # page does not exist:", url, proxy)
        return Response(404, browser.page_source)
    intro = None
    full_name = None
    with TRIAL:
        intro = browser.find_element(By.XPATH, "//h2")
        full_name = intro.text.replace("Request a meeting with", "").strip() if intro.text is not None else None
        full_name = full_name.replace("Meet with", "").strip() if intro.text is not None else None
        full_name = full_name.replace("Find a time to talk with", "").strip() if intro.text is not None else None
        full_name = full_name.replace("Find a time to meet with", "").strip() if intro.text is not None else None
        full_name = full_name.replace("Find a time to meet", "").strip() if intro.text is not None else None
        full_name = full_name.replace("Meeting with", "").strip() if intro.text is not None else None
        full_name = full_name.replace("Schedule a meeting with ", "").strip() if intro.text is not None else None
    durations = None
    with TRIAL:
        elems = browser.find_elements(By.XPATH, '//div[@id="duration-select"]//span')
        durations = [e.text for e in elems]

    if intro is None:  # strange situation when 200 and intro is None
        print("--404-- # intro does not exist:", url, proxy)
        with open(f"debug/hub_{nickname}.html", "w") as f:
            f.write(browser.page_source)

        return Response(404, browser.page_source)

    print("--200-- # success :", url, proxy)
    return Response(200, browser.page_source, intro=intro.text if intro is not None else None,
                    full_name=full_name, durations=durations)


class Hubspot(Enum):
    US = "https://meetings.hubspot.com/"
    EU = "https://meetings-eu1.hubspot.com/"


# def clear_text(txt:str)->str
#     return txt.replace("")


class BookUserInfo(TypedDict):
    first: str
    last: str
    email: str


def grab_block(browser, block_xpath, **items) -> Any:
    """ Usage:
        events = grab_block(browser, '//div[@data-id="event-type-header-title"]/../../..',
                             title=".//div[1]", description=".//div[2]", # extarct TEXT ATTRIBUTE by default
                             event_href=".//a", # extract HREF ATTRIBUTE
                             event_text=".//a", # extarct TEXT ATTRIBUTE
                             )
     """
    blocks = browser.find_elements(By.XPATH, block_xpath)
    result = []
    for block in blocks:
        block_items = {}
        for k, v in items.items():
            ks = k.split("_")
            if len(ks) == 1:
                block_items[k] = None
                with TRIAL:
                    block_items[k] = block.find_element(By.XPATH, v).text
            else:
                block_items[k] = None
                with TRIAL:
                    block_items[k] = block.find_element(By.XPATH, v).get_attribute(ks[1])

            print(k, v, block_items[k])
        result.append(block_items)
    print(result)
    return result


def calendly_book(nickname: str, proxy_nest: proxies.Proxy | None,
                  timeout=60, detach=False, headless=True, reuse: int = 1, images=False,
                  duration=None, time_slot=None, info: BookUserInfo = {}
                  ) -> Tuple[bool, str, dict]:
    global browser, browser_use_count
    print(f"{nickname}...", end="")
    url = f"https://calendly.com/{nickname}"  # https://calendly.com/tumikosha

    proxy = proxy_nest.next(prefix="") if proxy_nest is not None else None
    if browser is None:
        browser = ts.new_auth_browser(proxy=proxy, detach=detach, headless=headless, images=images,
                                      extension=r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx'
                                      )
    elif browser_use_count > reuse:
        browser.quit()
        browser = ts.new_auth_browser(proxy=proxy, detach=detach, headless=headless, images=images,
                                      extension=r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx')
    try:
        browser.get(url)
        time.sleep(4)
    except Exception as e:
        print("--408-- # timeout :", url, proxy)
        # return Response(408, str(e) + " ::>" + browser.page_source)
        return False, "408", {"error": str(e)}

    if "ERR_TIMED_OUT" in browser.page_source:
        return False, "408", {"error": "ERR_TIMED_OUT"}

    if "ERR_TUNNEL_CONNECTION_FAILED" in browser.page_source:
        return False, "408", {"error": "ERR_TUNNEL_CONNECTION_FAILED"}

    if "Page not found" in browser.page_source:  # or "404" in browser.page_source:
        return False, "404", {}

    try:
        full_name = xpath(browser, "//h1", "text()")
        intro = xpath(browser, '//div[@data-id="dossier"]/div[2]', "text()")
        # full_name = extract_name_from_intro(intro)
        # events = browser.find_elements(By.XPATH, '//div[@data-id="event-type-header-title"]/../..') #
        events = grab_block(browser, '//div[@data-id="event-type-header-title"]/../../..//a',
                            title=".//div[1]", description=".//div[2]", event_href=".")

        enriched_event=[]
        # scan events:
        for event in events:
            browser.get(event['event_href'])
            if "Web conferencing details" in browser.page_source:
                event['web conferencing']=True
            enriched_event.append(event)
            time.sleep(4)


        # getting list of durations
        durations = browser.find_elements(By.XPATH, '//div[@id="duration-select"]//button/span')
        durations_lst = [dur.text for dur in durations]
        print(durations_lst)
        durations[0].click()
        time.sleep(2)
        email = xpath(browser, "//span/a", "text")
        if email is not None:  # mail found
            return True, "email", {"intro": intro, "full_name": full_name,
                                   "durations": durations_lst, "dates": None, "email": email}

        # //*[contains(text(),"doesn't have")]
        dates = browser.find_elements(By.XPATH, '//td[@data-selenium-test-disabled="false"]//span')
        dates_lst = [dt.text for dt in dates]
        print(dates_lst)
        dates[0].click()
        time.sleep(2)
        month = browser.find_element(By.XPATH, '//h3')
        print(month.text)
        # time_slots
        time_slots = browser.find_elements(By.XPATH, '//div[@role="checkbox"]')
        time_slots_lst = [tm.text for tm in time_slots]
        print(time_slots_lst)
        time_slots[0].click()
        print(info)
        time.sleep(2)

        #
        first = browser.find_element(By.XPATH, '//input[@name="firstName"]')
        last = browser.find_element(By.XPATH, '//input[@name="lastName"]')
        email = browser.find_element(By.XPATH, '//input[@name="email"]')
        first.send_keys(info['first'])
        last.send_keys(info['last'])
        email.send_keys(info['email'])
        with TRIAL:  # click on  Agreement checkbox
            browser.find_element(By.XPATH, '//div[@type="checkbox"]//div').click()

        with TRIAL:  # fill company name
            browser.find_element(By.XPATH, '//input[@name="company"]').send_keys("---")

        time.sleep(8)
        book_dt = browser.find_element(By.XPATH, '//h5').text
        print(book_dt)
        browser.find_element(By.XPATH, '//button[@data-selenium-test="forward-button"]').click()
        time.sleep(25)
        # book_dt2 = browser.find_element(By.XPATH, '//h4').text
        book_dt2 = xpath(browser, '//h4', "text()")
        book_dt2 = book_dt2.replace("\n", "") if book_dt2 is not None else None

        if "confirmed" in browser.page_source:  # 'September 12, 2023\n6:00 PM'
            # p = xpath(browser, '//p', "text()")
            p = xpath(browser, '//div//p/i18n-string', "text()")
            full_name = None if p is None else p.replace("You're booked with", "").replace(
                "An invitation has been emailed to you.", "").replace(".", "").strip()
            return True, Status.Emailed.value, {"intro": intro, "full_name": full_name,
                                                "durations": durations_lst, "dates": dates_lst,
                                                "book_dt2": book_dt2}
        elif "Meeting time requested" in browser.page_source:
            return True, Status.Requested.value, {"intro": intro, "full_name": full_name,
                                                  "durations": durations_lst, "dates": dates_lst,
                                                  "book_dt2": book_dt2,
                                                  "reason": "Meeting time requested"
                                                  }
        else:  #
            # email = browser.find_element(By.XPATH, '//a"]')
            email = xpath(browser, '//a', "href")
            return True, Status.Complicated.value, {"intro": intro, "full_name": full_name, "durations": durations_lst,
                                                    "dates": dates_lst, "book_dt2": book_dt2,
                                                    "email": email, "reason": "complicated"
                                                    }
    except Exception as e:
        return False, Status.Loading_error.value, {"error": str(e)}



if __name__ == '__main__':
    # proxys = proxies.RotatingProxy("../proxy_dataimpulse.csv")  # this is data impulse
    proxys = proxies.RotatingProxy("/home/tumi/instant.proxy")  # instant proxy
    print(proxys.proxies)
    # scan("emra", proxy_nest=None, detach=True, headless=False)
    # url = "https://meetings-eu1.hubspot.com/veaceslav"

    # info: BookUserInfo = {"first": "Veaceslav", "last": "Kunitki", "email": "vkunitki@gmail.com"}
    info: BookUserInfo = {"first": "Angela", "last": "Buga", "email": "anjela.buga@gmail.com "}
    # GordonRussell8282@hotmail.com,Gordon Russell
    # confirmed, d = hubspot_book("veaceslav", host=Hubspot.EU,
    #                             proxy_nest=proxys, detach=True, headless=False, info=info)
    # confirmed, reason, d = calendly_book("Saray", proxy_nest=proxys, detach=True, headless=False, info=info)
    confirmed, reason, d = calendly_book("Jim", proxy_nest=proxys, detach=True, headless=False, info=info)
    print(confirmed, reason, d)
    # TrevorPullman361@hotmail.com
    # time.sleep(200)
    # resp = proxys.get(Hubspot.EU.value + "veaceslav")
    # resp = proxys.get(Hubspot.EU.value + "mujjjjjjjjjjdon")
    # if "disappointing" in resp.text:
    #     print("404 disappointing")
    # print(resp)
