from unittest import TestCase

import requests

from util import common
from tumi_tools.tumi_selenium import get_page_via_selenium
from util.common import html_2_txt_tit_fav


class Test(TestCase):
    def test_html_2_text(self):
        sites=[
        "rvvup.com",
        "proctoredu.ru",
        "42southtravel.com",
        "nofraud.com",
        "configcat.com",
        "kinescope.io",
        "onaudience.com",
        "openshot.org",
        "upnoya.de",
        "42startup.com",
        "talon-sec.com",
        "thirdiron.com",
        "ticketspice.com",
        "timecamp.com",
        "feedify.org",
        "flixlog.com",
        "sonnenbatterie.de",
        "smarttab.com",
        "societe.com",
        "sonnen.de",
        "gambol.in",
        "leadsrx.com",
        "survio.com",
        "debugbear.com",
        "desktime.com",
        "legalmatch.com",
        "botdistrikt.com"]
        for site in sites:

            response = get_page_via_selenium(f"https://{site}", sleep=2, proxy=None)
            print(response.status_code)
            if response.text is not None:
                txt, tit, fav, desc, h1, h2 = html_2_txt_tit_fav(response.text)
                print(f"{site}, {len(txt)}, {fav},\n {tit} \n {desc} \n h1: {h1}\n h2: {h2}")
            else:
                print("---NONE---")

        assert True

#