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
import re
import time
import os

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
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


def browser_visit_ipfs_site(url: str = None):
    if url is None:
        return
    driver = get_browser_driver_use()
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

    print(f"ipfs site: {link}")
    print("ipfs node information: \n"
          f"Onlie: {statues} \n"
          f"CORS: {cors}  \n"
          f"Hostname: {hostname} \n"
          f"Delay: {delay_time}")

    # visit ipfs url
    print(f"visit ipfs site: {link}")
    driver.get(link)
    Wait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'header')))

    # download zip file

    # crawl all nodes information

    # store information

    # get you want to update product from config File

    # if matched use pyautoGUI to operate all your ide product to update  and update
    # plugins

    time.sleep(120)

    driver.quit()


if __name__ == '__main__':
    source_url = "https://jetbra.in/s"
    browser_visit_ipfs_site(source_url)
