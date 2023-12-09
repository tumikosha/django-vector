import time
from unittest import TestCase

from selenium.webdriver.common.by import By

import config as cfg
from calendly_scenarios import CalendlyWeb
from proxies import ZenProxies, StormProxies
import tumi_tools.tumi_selenium as ts


class Test(TestCase):

    def test_zen_browser(self):
        driver = ts.zen_browser(api_key=cfg.ZEN_API_KEY)
        driver.get('http://httpbin.org/ip')
        print(driver.find_element(By.TAG_NAME, "body").text)
        driver.get('https://calendly.com/Modesto')
        time.sleep(600)
        self.assertTrue(True)

    def test_nedetectible_browser(self):
        # driver = ts.new_browser("")
        import os
        file = os.getcwd() + "/../../proxy.txt"
        print(file)
        proxy = StormProxies(file).next(prefix="")
        # print(proxy)

        driver = ts.new_undetectable_browser(proxy=proxy)
        driver.get('http://httpbin.org/ip')
        # print(driver.find_element(By.TAG_NAME, "body").text)
        driver.get('https://calendly.com/anjela-buga')
        # link = driver.find_element_by_xpath('//div[@data-id="event-type-header-title"][1]')
        link = driver.find_element(By.XPATH('//div[@data-id="event-type-header-title"][1]'))
        link.click()
        time.sleep(600)
        self.assertTrue(True)

    def test_new_browser(self):
        # driver = ts.new_browser("")
        import os
        file = os.getcwd() + "/../../proxy.txt"
        print(file)
        proxy = StormProxies(file).next(prefix="")
        # proxy = StormProxies(file).next(prefix="")
        # print(proxy)
        driver = ts.new_browser(proxy=proxy)
        # driver.get('http://httpbin.org/ip')
        # print(driver.find_element(By.TAG_NAME, "body").text)
        driver.get('https://calendly.com/anjela-buga')
        # links = driver.find_element(By.XPATH, '//div[@data-id="event-type-header-title"]')
        link = driver.find_element(By.XPATH, '(//div[@data-id="event-type-header-title"])[1]')
        link.click()
        time.sleep(10)
        driver.find_element(By.XPATH, '(//td/button[not(@disabled)])[1]').click() # date
        # time_buttons = driver.find_element(By.XPATH, '//button[@data-container="time-button"]')
        driver.find_element(By.XPATH, '(//button[@data-container="time-button"])[1]').click() # time
        time.sleep(5)
        driver.find_element(By.XPATH, '//button[contains(text(), "Next")]').click() # Next
        # //input[@name="full_name"]
        driver.find_element(By.XPATH, '//input[@name="full_name"]').send_keys("Nadejda Matiuhina")
        time.sleep(2)
        driver.find_element(By.XPATH, '//input[@name="email"]').send_keys("nadejda.matiuhina@gmail.com")
        time.sleep(2)
        driver.find_element(By.XPATH, '//textarea[@name="question_0"]').send_keys("lets talk")
        time.sleep(6)
        driver.find_element(By.XPATH, '//div[contains(text(), "Schedule")]').click()
        time.sleep(600)
        self.assertTrue(True)


