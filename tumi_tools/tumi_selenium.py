from collections import namedtuple

import time

from selenium import webdriver
from seleniumwire import webdriver as wire_driver  # for Proxy with AUTHORIZING
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from tumi_tools.proxies import ZenProxies, StormProxies


# edge = webdriver.Edge(EdgeChromiumDriverManager().install())
# chrome = webdriver.Chrome(ChromeDriverManager().install())


def new_browser(detach=True, proxy="63.141.23.210:19015", headless=True):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option("detach", detach)
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--headless')
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-dev-shm-usage");
    chrome_options.add_extension(r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx')
    # Turn-off useAutomationExtension
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if proxy is not None:
        chrome_options.add_argument(f'--proxy-server=' + proxy)
    print("new browser proxy ", proxy)
    # driver = webdriver.Chrome(r"bin/chromedriver", options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    # Rotating the user-agent through execute_cdp_cmd() command as follows:
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def new_undetectable_browser(headless=False, use_subprocess=False, proxy="63.141.236.210:19015"):
    # chrome_options = uc.ChromeOptions()
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-ssl-errors=yes') # ?
    chrome_options.add_argument('--ignore-certificate-errors') # ?
    chrome_options.add_extension(r'/home/tumi/prj/fixiegen/bin/xpath_helper.crx')
    print("SELENIUM SET PROXY  ", proxy)
    chrome_options.add_argument(f'--proxy-server=' + proxy)
    driver = uc.Chrome(options=chrome_options, headless=headless, use_subprocess=use_subprocess)
    return driver


def zen_browser(api_key="<...>", detach=True):
    from seleniumwire import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option("detach", detach)
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    zen_proxy = ZenProxies(api_key=api_key)
    key_with_session = zen_proxy.random_session()
    print(key_with_session)
    selenium_wire_options = {
        'proxy': {
            # 'http': f'http://{api_key}:@proxy.zenrows.com:8001',
            'http': f'http://{key_with_session}@proxy.zenrows.com:8001',
            # 'https': f'https://{key_with_session}@proxy.zenrows.com:8001',
            'verify_ssl': False,
        },
    }
    return webdriver.Chrome(options=chrome_options, seleniumwire_options=selenium_wire_options)


# browser = new_browser()
# browser = new_undetectable_browser()
# browser.get("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
# browser.get("http://51.195.118.108:9999")
# time.sleep(120)


def new_auth_browser(detach=True, proxy="Bt36tT29DapPVbgr:wifi;;;;@rotating.proxyempire.io:9000",
                     headless=True,  images=False, extension=None):
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
        chrome_options.add_argument('--blink-settings=imagesEnabled=false') # images
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


def get_page_via_selenium(url: str, sleep=2, detach=False, proxy="63.141.23.210:19015", headless=True,
                          timeout=40):
    # browser = new_undetectable_browser()
    Response = namedtuple('Response', ['status_code', 'text'])
    # browser = new_browser(detach=detach, headless=headless, proxy=proxy)
    browser = new_auth_browser(detach=detach, headless=headless, proxy=proxy)
    # browser = new_browser(detach=detach, headless=False, proxy=proxy)
    browser.set_page_load_timeout(timeout)
    try:
        browser.get(url)
        time.sleep(sleep)
        if browser.page_source.find("404 Not Found")>-1:
            return Response(404, None)

        if browser.page_source.find("Privacy error")>-1:
            return Response(404, None)

        response = Response(200, browser.page_source)
        # result = {"status_code": 200, "text": browser.page_source}
        browser.close()

        return response

    except Exception as e:
        print(str(e))
        # r = requests.get(url)
        browser.close()
        return Response(None, None)
        # return {"status_code": None, "text": None}


if __name__ == '__main__':
    # edge = webdriver.Edge(EdgeChromiumDriverManager().install())
    # chrome = webdriver.Chrome(ChromeDriverManager().install())
    # res = get_page_via_selenium("https://www.zignsec.com/", sleep=2, proxy=None)
    # print(res)
    # url = "http://dirs.info/ccc"
    res = get_page_via_selenium(url := "http://dirs.info/ccc", sleep=2, proxy=None)
    print(res)
    # res = get_page_via_selenium("https://www.zignsessssc.com/", sleep=2, proxy=None)
    # print(res)
