#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Description: update_for_me  入口程序
@Author  : fireinrain
@Site    : https://github.com/fireinrain
@File    : main.py
@Software: PyCharm
@Time    : 2022/7/13 1:36 AM
"""
import collections
import re
import time
import os
import platform

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.expected_conditions import staleness_of
# from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait

from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# init store dir
DATA_STORE_NAME = "data_store"
store_dir = os.path.join(os.path.dirname(__file__), DATA_STORE_NAME)
if not os.path.exists(store_dir):
    os.makedirs(store_dir)
abs_store_dir = os.path.abspath(store_dir)
platform_str = platform.system()


# 获取不同的浏览器驱动
def get_browser_driver_use(browser_name: str = None) -> webdriver:
    """
    根据传入的浏览器名 获取driver实例
    :param browser_name:
    :type str:
    :return:
    :rtype:
    """
    if browser_name == "firefox":
        option = webdriver.FirefoxOptions()
        # option = webdriver.ChromeOptions()
        option.set_preference("permissions.default.desktop-notification", 0)
        option.set_preference("dom.webnotifications.enabled", 0)
        option.set_preference("media.volume_scale", "0.0")
        option.set_preference("general.useragent.override", UserAgent(verify_ssl=False).random)
        option.add_argument("--disable-blink-features")
        # option.add_argument("--headless")
        # 下载设置

        option.set_preference('browser.download.dir', abs_store_dir)
        option.set_preference('browser.download.folderList', 2)
        option.set_preference('browser.download.manager.showWhenStarting', False)
        option.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')

        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=option)

        return driver
    # use chrome as default
    else:
        option = webdriver.ChromeOptions()
        # option = webdriver.ChromeOptions()
        option.add_argument('--disable-notifications')
        option.add_argument("--mute-audio")
        option.add_argument("--disable-blink-features")
        # option.add_argument("--headless")
        # option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        option.add_argument(
            f"user-agent={UserAgent(verify_ssl=False).random}")
        # 下载设置
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': abs_store_dir}
        option.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return driver


def browser_visit_ipfs_site(url: str = None, browser_name: str = None, destroys_driver: bool = False) -> {}:
    """
    浏览器访问ipfs网站 获取 driver 和 cookie，request headers
    :param destroys_driver:
    :type destroys_driver:
    :param url:
    :type url:
    :param browser_name:
    :type browser_name:
    :return:
    :rtype:
    """
    if url is None:
        return
    # {"driver": "","cookie": "","header":""}
    results = {}
    driver = get_browser_driver_use(browser_name)
    driver.get(url)
    print(f"{driver.current_url} is: waiting for be loaded ......")
    try:
        Wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="checker.results"]/div[2]/div[1]')),
                               message="can't find a valid ipfs node onlie ......")
    except TimeoutException as e:

        driver.quit()
    print(f"{driver.current_url} is: loaded ......")
    # find version node
    version_node = driver.find_element(by=By.XPATH, value='//*[@id="origin-warning"]/ul/li')
    version_text = version_node.text
    pattern = re.compile(r'[(](.*?)[)]', re.S)
    version_str = re.findall(pattern, version_text)[0]

    print(f"tools version is: {version_str} ......")
    time.sleep(2)

    # find a valid ipfs site url
    first_ipfs_node = driver.find_element(by=By.XPATH, value='//*[@id="checker.results"]/div[2]')
    statues = first_ipfs_node.find_element(by=By.XPATH, value='./div[1]').text
    cors = first_ipfs_node.find_element(by=By.XPATH, value='./div[2]').text
    hostname = first_ipfs_node.find_element(by=By.XPATH, value='./div[3]').text
    delay_time = first_ipfs_node.find_element(by=By.XPATH, value='./div[4]').text

    link = driver.find_element(by=By.XPATH, value='//*[@id="checker.results"]/div[2]/div[3]/a').get_attribute('href')

    ipfs_node_info = collections.OrderedDict()
    print(f"1.ipfs site: {link}")
    print("ipfs node information: \n"
          f"2.Onlie: {statues} \n"
          f"3.CORS: {cors}  \n"
          f"4.Hostname: {hostname} \n"
          f"5.Delay: {delay_time}")
    ipfs_node_info['1.ipfs site'] = link
    ipfs_node_info['2.Onlie'] = statues
    ipfs_node_info['3.CORS'] = cors
    ipfs_node_info['4.Hostname'] = hostname
    ipfs_node_info['5.Delay'] = delay_time

    results["ipfs_node_info"] = ipfs_node_info
    results["site_link"] = link

    # visit ipfs url
    print(f"visit ipfs site: {link}")
    driver.get(link)
    Wait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'header')))

    # dont need cookies or sepecific header or cookie
    # cookies = driver.get_cookies()
    # results['cookies'] = cookies
    # results['headers'] = None

    # time.sleep(120)
    if destroys_driver:
        driver.delete_all_cookies()
        driver.quit()
        results["driver"] = None
    else:
        results["driver"] = driver

    return results


# # store information
#
# # get you want to update product from config File
#
# # if matched use pyautoGUI to operate all your ide product to update  and update
# # plugins

def crawl_info_by_browser(driver: WebDriver) -> []:
    download_link = driver.find_element(by=By.XPATH, value='/html/body/header/p/a')
    file_path_in_server = download_link.get_attribute("href")
    file_name = file_path_in_server.split("/")[-1]
    file_path_in_local = os.path.join(abs_store_dir, file_name)

    # check if this file is already exists
    # download zip file
    if not os.path.exists(file_path_in_local):
        download_link.click()
        while not os.path.exists(file_path_in_local):
            time.sleep(0.1)
        print(f"{file_path_in_local}: 文件下载完成......")

    # crawl all nodes information
    product_nodes = driver.find_elements(by=By.XPATH, value='/html/body/main/article')
    if product_nodes is None or len(product_nodes) < 1:
        # no content to crawl
        driver.delete_all_cookies()
        driver.quit()
        return None
    # 因为在selenium中无法从selenium api中获取剪贴板内容
    # 所以这里设计为 使用selenium 执行js脚本在 dom中创建input node
    # 然后使用 selenium 获取 node 的value
    # create an input dom node for getting value
    driver.execute_script('''
        var input_node = document.createElement('input');
        input_node.id = "inputSeleniumForCopy";
        var body = document.getElementsByTagName('body')[0];
        body.appendChild(input_node);
        ''')
    time.sleep(0.01)
    results = {"active_zip": file_path_in_local}
    keys_info = []
    input_node = driver.find_element(by=By.ID, value='inputSeleniumForCopy')
    if platform_str == "Darwin":
        copy_key = Keys.COMMAND
    else:
        copy_key = Keys.CONTROL
    for product_node in product_nodes:
        version_support = product_node.find_element(by=By.XPATH, value='./header/div/button').get_attribute(
            "data-version")
        product_name = product_node.find_element(by=By.XPATH, value='./div[1]/h1').text
        active_key = product_node.find_element(by=By.XPATH, value='./div[1]/p')
        active_key.click()
        # 这里需要判断平台
        input_node.send_keys(copy_key, 'v')
        key_str = input_node.get_attribute("value")
        print(f"product name: {product_name},version_support: {version_support}, key_str: {key_str}")
        keys_info.append((product_name.strip(), version_support.strip(), key_str.strip()))
        input_node.clear()
    results["keys_info"] = keys_info
    return results


def fetch_product_info_all_by_browser(url, browser_name):
    info_dict = browser_visit_ipfs_site(url, browser_name, destroys_driver=False)
    print(info_dict)
    driver = info_dict["driver"]
    product_infos = crawl_info_by_browser(driver)
    print(product_infos)
    driver.delete_all_cookies()
    driver.quit()


def fetch_product_info_all_by_requests(url, browser_name):
    info_dict = browser_visit_ipfs_site(url, browser_name, destroys_driver=True)

    pass


if __name__ == '__main__':
    source_url = "https://jetbra.in/s"
    fetch_product_info_all_by_browser(source_url)
