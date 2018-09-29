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

POST_XPATH = '//div[@action-type="feed_list_item" and @mid]'


def _extract_post_from_element(element):
    try:
        html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(html, 'html.parser')
        mid = int(
            soup.find('div', {"action-type": "feed_list_item"}).attrs['mid'])
        linksearch = "".join(re.findall(
            r"(\/\/weibo.com\/)(\d*)(\/)([a-zA-Z0-9]*)", soup.prettify())[0])
        link = "https:" + linksearch
        uid = int(re.search(
            r"(\/\/weibo.com\/)(\d*)(\/)([a-zA-Z0-9]*)", soup.prettify()).group(2))
        text = soup.select_one(
            "[node-type=\"feed_list_content\"]").getText().strip()
        data = {
            "mid": mid,
            "uid": uid,
            "link": link,
            "text": text,
            "retrieved": datetime.utcnow(),
            "visible": True,
            "censored": False,
            "completed": False
        }
        return data
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        return None


def extract_posts(url):
    try:
        options = webdriver.ChromeOptions()
        if not opts.show_head():
            options.set_headless(headless=True)
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, POST_XPATH))
        )
        elements = driver.find_elements_by_xpath(POST_XPATH)
        posts = [_extract_post_from_element(element) for element in elements]
        return [post for post in posts if post is not None]
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        return []
