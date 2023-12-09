import random

from pprint import pprint
from urllib.parse import urlparse

import time
from selenium.webdriver.common.by import By

from typing import Tuple

import tumi_tools.proxies
from scanners.web_page import WebPage, Response
from tumi_tools import proxies
from tumi_tools.name_util import Status
from tumi_tools.try_wrappers import TRIAL


class CalendlyPage(WebPage):
    row = {}
    nickname = None

    @staticmethod
    def cal_nick_from_url(url: str) -> str:
        """ extracts calendly account name from url"""
        try:
            arr = urlparse(url).path.strip("/").split("/")
            nick = arr[0]
            if arr[0] == "d" and len(arr) > 1:
                nick = arr[1]

            return nick
        except:
            return None

    @staticmethod
    def generate_usa_phone_number():
        lst = [1, 8, 0, 8] + [str(random.randrange(10)) for i in range(8)]
        return "+{}{}{}{}{}{}{}{}{}{}{}".format(*lst)

    @staticmethod
    def generate_mexican_phone_number():
        # +52 55 1234 5678
        lst = [5, 2, 5, 5] + [str(random.randrange(10)) for i in range(8)]
        return "+{}{} {}{} {}{}{}{} {}{}{}{}".format(*lst)

    @staticmethod
    def full_name_split(full_name) -> Tuple[str, str]:
        lst = full_name.strip().replace("  ", " ").split(" ")
        return lst[0], lst[1]

    def main_page(self, nickname: str) -> None:
        self.nickname = nickname
        self.navigate(url=f"https://calendly.com/{nickname}")
        time.sleep(4)
        self.accept_cookie()

    def check_status(self) -> Tuple[int, str, dict]:
        if "ERR_TIMED_OUT" in self.browser.page_source:
            return False, "408", {"error": "ERR_TIMED_OUT"}

        if "ERR_TUNNEL_CONNECTION_FAILED" in self.browser.page_source:
            return False, "408", {"error": "ERR_TUNNEL_CONNECTION_FAILED"}

        if "Page not found" in self.browser.page_source:  # or "404" in browser.page_source:
            return False, "404", {}

        return True, Status.OK.value, {}

    def scan_head(self):
        self.accept_cookie()
        self.row["full_name"] = self.xpath("//h1", "text()")
        self.row["intro"] = self.xpath('//div[@data-id="dossier"]/div[2]', "text()")

    def scan_events(self, nick=None):
        self.row["full_name"] = self.xpath("//h1", "text()")
        self.row["intro"] = self.xpath('//div[@data-id="dossier"]/div[2]', "text()")

        events = self.grab_block('//div[@data-id="event-type-header-title"]/../../..//a',
                                 title=".//div[1]", description=".//div[2]", event_href=".",
                                 # location='.//div[@data-component="event-type-location"]',
                                 # zoom='//*[contains(text(),"zoom")]',
                                 # teams='//*[contains(text(),"Microsoft Teams")]',
                                 # web_conferencing='//*[contains(text(),"Web conferencing ")]',
                                 )

        enriched_events = []
        self.row["web_conferencing"] = False
        # scan events:
        locations = []
        for event in events:
            self.browser.get(event['event_href'])
            time.sleep(6)
            location = self.xpath('//div[@data-component="event-type-location"]', "text()")

            web_conf = self.xpath('//*[contains(text(),"Web conf")]', "text()")
            zoom = self.xpath('//*[contains(text(),"zoom ")]', "text()")
            teams = self.xpath('//*[contains(text(),"Microsoft Teams")]', "text()")
            if web_conf is not None:
                event['web_conferencing'] = True
                self.row["web_conferencing"] = True
                self.row["web_conf"] = True
            if zoom is not None:
                event['web_conferencing'] = True
                self.row["web_conferencing"] = True
                self.row["zoom"] = True
            if teams is not None:
                event['web_conferencing'] = True
                self.row["web_conferencing"] = True
                self.row["teams"] = True

            # if "Web conferencing details" in self.browser.page_source:
            #     event['web_conferencing'] = True
            #     self.row["web_conferencing"] = True
            #     web_conferencing_flag = True
            # if "Zoom" in self.browser.page_source:
            #     event['web_conferencing'] = True
            #     self.row["web_conferencing"] = True
            #     web_conferencing_flag = True
            # if 'Microsoft Teams' in self.browser.page_source:
            #     event['web_conferencing'] = True
            #     self.row["web_conferencing"] = True
            #     web_conferencing_flag = True

            # //td[@aria-selected="false"]/button/span
            dates = self.xpath_lst('//td[@aria-selected="false"]/button/span', "text")
            event['dates_num'] = len(dates) if dates is not None else 0
            if "This calendar is currently unavailable" in self.browser.page_source \
                    or "indisponible" in self.browser.page_source \
                    or "no está disponible" in self.browser.page_source:
                pass
            else:
                enriched_events.append(event)

            event['location'] = self.xpath_lst('//div[@data-component="event-type-location"]', "text")
            locations.append(event['location'])

        self.row["events"] = enriched_events
        self.row["locations"] = locations

        # if self.row["web_conferencing"]:
        #     open("debug/" + str(nick), "w").write(self.browser.page_source)
        #
        # if nick == "Darcy":
        #     open("debug/" + str(nick), "w").write(self.browser.page_source)

        return self.row

    def accept_cookie(self):
        with TRIAL:  # close accept cookies dialog
            self.browser.find_element(By.XPATH, '//button[contains(text(),"Accept ")]').click()
            time.sleep(4)

    def book_random(self, email: str, full_name: str):
        try:
            first, last = self.full_name_split(full_name)
            events = self.row['events']
            events.sort(key=lambda event: event['dates_num'])
            if len(events) == 0:
                return "no available events"
            event = events[-1]
            self.browser.get(event['event_href'])
            if ("This calendar is currently unavailable" in self.browser.page_source
                    or "indisponible" in self.browser.page_source
                    or "no está disponible" in self.browser.page_source

            ):
                return "unavailable"
            time.sleep(4)  # //div[contains(text(),"View next month")]
            self.accept_cookie()
            # with TRIAL:  # close accept cookies dialog
            #     self.browser.find_element(By.XPATH, '//button[contains(text(),"Accept ")]').click()
            #     time.sleep(4)

            with TRIAL:
                self.browser.find_element(By.XPATH, '//div[contains(text(),"View next month")]').click()
                time.sleep(4)

            self.browser.find_element(By.XPATH, '//td[@aria-selected="false"][1]/button').click()
            time.sleep(4)
            self.browser.find_element(By.XPATH, '//button[@data-container="time-button"]').click()
            time.sleep(4)
            with TRIAL:
                self.browser.find_element(By.XPATH, '//button[contains(text(),"Next")]').click()
            with TRIAL:
                self.browser.find_element(By.XPATH, '//button[contains(text(),"Suivant")]').click()
            with TRIAL:
                self.browser.find_element(By.XPATH, '//button[contains(text(),"Volgende")]').click()
            with TRIAL:
                self.browser.find_element(By.XPATH, '//button[contains(text(),"Weiter")]').click()

            time.sleep(4)
            with TRIAL:
                self.browser.find_element(By.XPATH, '//input[@name="first_name"]').send_keys(first)
                time.sleep(2)
            with TRIAL:
                self.browser.find_element(By.XPATH, '//input[@name="last_name"]').send_keys(last)
                time.sleep(2)
            with TRIAL:
                self.browser.find_element(By.XPATH, '//input[@name="full_name"]').send_keys(full_name)
                time.sleep(2)

            self.browser.find_element(By.XPATH, '//input[@name="email"]').send_keys(email)
            time.sleep(2)
            with TRIAL:
                self.browser.find_element(By.XPATH, '//input[@name="question_0"]').send_keys("--")
                time.sleep(2)
            with TRIAL:
                self.browser.find_element(By.XPATH, '//textarea[@name="question_0"]').send_keys("-")
                time.sleep(2)
            with TRIAL:
                self.browser.find_element(By.XPATH, '//textarea[@name="question_1"]').send_keys("-")
                time.sleep(2)

            with TRIAL:
                self.browser.find_element(By.XPATH, '//input[@name="phone_number"]').send_keys(
                    self.generate_mexican_phone_number())
                time.sleep(2)
            with TRIAL:  #
                self.browser.find_element(By.XPATH, '//div[contains(text(), "Meet")]').click()
                time.sleep(2)

            with TRIAL:  # self.browser.find_element(By.XPATH, '//div[contains(text(), "Meet")]').click()
                self.browser.find_element(By.XPATH, '//div[contains(text(), "Schedule")]').click()
            with TRIAL:
                self.browser.find_element(By.XPATH, '//div[contains(text(), "Confirmer")]').click()
            with TRIAL:
                self.browser.find_element(By.XPATH, '//button[@type="submit"]').click()

            time.sleep(4)
            # https://calendly.com/tumikosha/30min/invitees/f5ccd2c4-0dbc-4ea2-b98c-8aa3ef5b44a9
            lst = str(self.browser.current_url).split("/")
            book_id = lst[-1]

            return book_id
        except Exception as e:
            print("FAIL")
            return "fail"

    def scan(self, nick: str) -> Tuple[bool, str, dict]:
        self.main_page(nick)
        is_good, status, err = self.check_status()
        if is_good:
            print(f" 🟢  {nick} {status} ")
            self.scan_head()
            self.scan_events()
            self.row['_id'] = nick
            return True, status, self.row
        else:
            print(f" 🔴  {nick} {status} ")
            return False, status, err


if __name__ == '__main__':
    page = CalendlyPage(proxy_nest=proxies.RotatingProxyHTTP("/home/tumi/instant.proxy"),
                        detach=True, headless=False
                        )

    # page.main_page("Jim")
    # page.main_page("matbock")
    page.main_page("abel")
    # print(page.check_status())
    page.scan_head()
    page.scan_events()

    # print("---------------")
    pprint(page.row)
    # print(page.book_random("acunamatata@gmail.com", "Acuna Matata"))
    time.sleep(60 * 5)

# fail
# fray
