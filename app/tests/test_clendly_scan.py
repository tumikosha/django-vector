from unittest import TestCase
from urllib.parse import urlparse

from scanners.calendly_page import CalendlyPage
from util.calendly_cached import get_events_by_nick


# from util.calendly_cached import get_cal_acc_info


class Test(TestCase):
    # def test_get_cal_acc_info(self):
    #     info = {"ver": 1, "links": ["betterstack/meeting?hide_gdpr_banner=1&amp", "betterstack/meeting"]}
    #     url_part = "betterstack/meeting?hide_gdpr_banner=1&amp"
    #     # proxy_nest=proxies.RotatingProxyHTTP("/home/tumi/instant.proxy"),
    #     page = CalendlyPage(proxy_nest=None, detach=True, headless=False)
    #     success, status, detail = page.scan("betterstack")
    #     page.browser.quit()
    #     print(success, status, detail)
    #     assert success

    def test_get_cal_acc_info_bad(self):
        is_good, status, res = get_events_by_nick("betterstack22222", headless=False, detach=False, pre_check=True)
        print("res", is_good, status, res)
        assert not is_good

    def test_get_cal_acc_info_good(self):
        links = ["botman-call/bt_team""botman-call/bt_team", "///botman-call/bt_team",
                 "https://calendly.com/botman-demo/bt-website",
                 "d/botman-call/bt_team""botman-call/bt_team",
                 ]

        for link in links:
           print(CalendlyPage.cal_nick_from_url(link))

        assert True

        # get_events_by_nick
