from unittest import TestCase

from scanners.calendly_page import CalendlyPage


def clear_nick_list(nick_list):
    DENIED_NICKS = set(["integration", "favicon.svg", " icons", "favicon-32x32.png", ""])
    nick_list = [CalendlyPage.cal_nick_from_url(nick) for nick in nick_list]
    nick_list = set(nick_list)  # remove dublicated nicknames
    nick_list = nick_list - DENIED_NICKS
    return nick_list


class Test(TestCase):
    def test_get_events_by_nicks(self):
        nick_list = [
            "dnsmonitoring/constellix-demo",
            "tiggeedemo/60min?month=2021-12",
            "dnsmonitoring/constellix-demo?hide_event_type_details=1&hide_gdpr_bann…"
        ]

        lst = clear_nick_list(nick_list)
        print(lst)
        assert len(lst)==2
