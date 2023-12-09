import time

from selenium.webdriver.common.by import By

import tumi_tools.proxies
from tumi_tools import proxies
from tumi_tools.try_wrappers import TRIAL
from selenium import webdriver
from seleniumwire import webdriver as wire_driver  # for Proxy with AUTHORIZING
from lxml import html as html_module


class Response:
    status_code = None
    html = None
    text = None

    @staticmethod
    def html_2_text(html_content, min_length=15):
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
        except Exception as e:
            self.text = str(e)

    def __repr__(self) -> str:
        html_len = len(self.html) if self.html is not None else None
        text_len = len(self.text) if self.text is not None else None
        html_start = self.html[:20] if self.html is not None else None
        text_start = self.text[:20] if self.text is not None else None
        return f"{type(self).__name__}(status_code={self.status_code}, {html_len}::> html={html_start}..., {text_len}::>text={text_start}... {self.kwargs})"


def new_auth_browser(detach=True, proxy="Bt36tT29DapPVbgr:wifi;;;;@rotating.proxyempire.io:9000",
                     headless=True, images=False, extension=None):
    """
        This method creates driver via seleniumwire_options
        and used to connect via PROXY with AUTHORIZATION
    :param detach: True to detach
    :param proxy: "login:password@addr:port"  ; None for direct connection
    :param headless: True to hide window
    :return:
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option("detach", detach)
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    if not images:
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # images
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--headless')
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-dev-shm-usage");
    if extension is not None:
        # chrome_options.add_extension(r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx')
        chrome_options.add_extension(extension)
    # Turn-off useAutomationExtension
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if proxy is not None:
        proxy_options = {
            'proxy': {
                # 'http': 'http://USERNAME:PASSWORD@proxy-server:8080',
                'http': 'http://' + proxy,
                'https': 'http://' + proxy,
                # 'https': 'http://USERNAME:PASSWORD@proxy-server:8080',
                # 'no_proxy': 'localhost:127.0.0.1'
            },
            'request_storage_base_dir': '/media/tumi/evo850-512Gb/selenium',
            'request_storage': 'memory',
            'request_storage_max_size': 1000  # Store no more than 100 requests in memory
        }
        # print("new browser proxy ", proxy)
        # driver = webdriver.Chrome(r"bin/chromedriver", options=chrome_options)
        # driver = webdriver.Chrome(options=chrome_options)
        driver = wire_driver.Chrome(options=chrome_options, seleniumwire_options=proxy_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    # Rotating the user-agent through execute_cdp_cmd() command as follows:
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


class WebPage:
    last_url, browser = None, None

    # browser_use_count = 0
    pages_opened, pages_opened_200, pages_tried = 0, 0, 0

    def __init__(self, browser=None, proxy_nest: proxies.Proxy | None = None, reuse: int = 1, detach=False,
                 headless=True, images=False, timeout=60, url=None):
        self.proxy_nest = proxy_nest
        self.browser_use_count = 0
        # self.proxy = proxy_nest.next(prefix="") if proxy_nest is not None else None
        self.proxy = proxy_nest.random(prefix="") if proxy_nest is not None else None
        print("choosed proxy:", self.proxy)

        self.make_new_browser(reuse=reuse, detach=detach, headless=headless, images=images, timeout=timeout)

    def make_new_browser(self, reuse: int = 1, detach=False, headless=True, images=False, timeout=60,
                         extension=r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx'):

        proxy = self.proxy_nest.next(prefix="") if self.proxy_nest is not None else None
        print("PROXY:", proxy)
        if self.browser is None:
            self.browser = new_auth_browser(proxy=proxy, detach=detach, headless=headless, images=images,
                                            # extension=r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx'
                                            )
        elif self.browser_use_count > reuse:
            self.browser.quit()
            self.browser = new_auth_browser(proxy=proxy, detach=detach, headless=headless, images=images,
                                            # extension=r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx'
                                            )
            browser_use_count = 0
        self.browser_use_count += 1
        print("browser reused", self.browser_use_count)
        self.browser.set_page_load_timeout(timeout)

    def delete_cache(self):
        # driver = self.browser
        # driver.execute_script("window.open('')")  # Create a separate tab than the main one
        # driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
        # driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
        # self.perform_actions(driver, Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 5 + Keys.ENTER)  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
        # driver.close()  # Close that window
        # driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.
        self.browser.execute_cdp_cmd('Storage.clearDataForOrigin', {
            "origin": '*',
            "storageTypes": 'all',
        })
        print("* cache cleared")

    def navigate(self, url, timeout_after=4):
        self.last_url = url
        self.pages_tried += 1
        self.browser.get(url)
        try:
            self.browser.get(url)
            time.sleep(timeout_after)
        except Exception as e:
            print("--408-- # timeout :", url, self.proxy)
            return Response(408, str(e) + " ::>" + self.browser.page_source)
        self.pages_opened += 1
        if "Well, this is disappointing" in self.browser.page_source:
            print("--404-- # page does not exist:", url, self.proxy)
        self.pages_opened_200 += 1
        return Response(200, self.browser.page_source)

    def xpath(self, path, attr):
        try:
            elem = self.browser.find_element(By.XPATH, path)
            if attr == 'text' or attr == "text()":
                return elem.text
            else:
                return elem.get_attribute(attr)
        except Exception as e:
            return None

    def xpath_lst(self, path, attr):
        try:
            elems = self.browser.find_elements(By.XPATH, path)
            lst = []
            for elem in elems:
                if attr == 'text' or attr == "text()":
                    lst.append(elem.text)
                else:
                    lst.append(elem.get_attribute(attr))
            return lst
        except Exception as e:
            return None

    def grab_block(self, block_xpath, **items) -> list:
        """ Usage:
            events = grab_block(browser, '//div[@data-id="event-type-header-title"]/../../..',
                                 title=".//div[1]", description=".//div[2]", # extarct TEXT ATTRIBUTE by default
                                 event_href=".//a", # extract HREF ATTRIBUTE
                                 event_text=".//a", # extarct TEXT ATTRIBUTE
                                 )
         """

        blocks = self.browser.find_elements(By.XPATH, block_xpath)
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

                # print(k, v, block_items[k])
            result.append(block_items)
        # print(result)
        return result


if __name__ == '__main__':
    proxys = proxies.RotatingProxy("/home/tumi/instant.proxy")  # instant proxy
    page = WebPage(proxy_nest=proxys, detach=True, headless=False)
    response = page.navigate("http://dirs.info")
    print(response)

    response = page.navigate("http://dirs.info")
    print(response)
    response = page.navigate("http://dirs.info")
    print(response)
