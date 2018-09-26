from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import traceback
import opts
import re
import time
from pyvirtualdisplay import Display

POST_XPATH = '//div[@action-type="feed_list_item" and @mid]'

display = Display(visible=0, size=(1280, 1024))
display.start()


def _extract_post_from_element(element):
    html = element.get_attribute("outerHTML")
    soup = BeautifulSoup(html, 'html.parser')
    mid = int(soup.find('div', {"action-type": "feed_list_item"}).attrs['mid'])
    uid = int(re.search(r"\/\/weibo.com\/(.*)(\?.*)",
                        soup.find('a', class_="name").attrs['href']).group(1))
    link = soup.find("p", class_="from").find('a').attrs['href']
    text = soup.find("p", class_="txt").getText()
    return {
        "mid": mid,
        "uid": uid,
        "link": link,
        "text": text,
        "retrieved": datetime.now(),
        "visible": True,
        "censored": False
    }


def extract_posts(url):
    try:
        options = webdriver.ChromeOptions()
        if not opts.show_head():
            options.set_headless(headless=True)
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        elements = driver.find_elements_by_xpath(POST_XPATH)
        posts = [_extract_post_from_element(element) for element in elements]
        return posts
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        return []
