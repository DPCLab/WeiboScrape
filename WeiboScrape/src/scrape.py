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

# FROM https://stackoverflow.com/questions/1119722/base-62-conversion


def weibo_encode_mid(mid):
    mid = str(mid)
    hash = ''
    end = len(mid)
    while end > 0:
        start = end - 7
        if start < 0:
            start = 0
        num = mid[start:end]
        h = _b62_encode(int(num))
        padding = 4 - len(h)
        if padding > 0 and start > 0:
            for i in range(padding):
                h = '0' + h
        hash = h + hash
        end -= 7
    return hash
    # mid_str = str(mid)
    # return "".join([_b62_encode(int(i)) for i in [mid_str[:2], mid_str[2:9], mid_str[9:16]]])


def _b62_encode(num):
    """Encode a positive number in Base 62 with a custom alphabet

    Arguments:
    - `num`: The number to encode
    - `alphabet`: The alphabet to use for encoding
    """
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def _extract_post_from_element(element):
    try:
        html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(html, 'html.parser')
        mid = int(
            soup.find('div', {"action-type": "feed_list_item"}).attrs['mid'])
        linksearch = "".join(re.findall(
            r"(\/\/weibo.com\/)(\d*)(\/)([a-zA-Z0-9]*)", soup.prettify())[0])
        uid = int(re.search(
            r"(\/\/weibo.com\/)(\d*)(\/)([a-zA-Z0-9]*)", soup.prettify()).group(2))
        try:
            text = soup.select_one(
                "[node-type=\"feed_list_content\"]").getText().strip()
        except Exception as e:
            text = None
        data = {
            "mid": mid,
            "uid": uid,
            "text": text,
            "link": "https://www.weibo.com/%s/%s" % (uid, weibo_encode_mid(mid)),
            "retrieved": datetime.utcnow(),
            "visible": True,
            "censored": False,
            "completed": False
        }
        return data
    except Exception as e:
        logging.error(e)
        logging.info(soup.prettify())
        traceback.print_exc()
        return None


def check_post_for_censorship(post):
    try:
        logging.info("Checking %s for censorship..." % post['mid'])
        if 'link' not in post:
            post['link'] = "https://weibo.com/%s/%s" % (post['uid'],
                                                weibo_encode_mid(post['mid']))
        posts_visible = extract_posts(post['link'])
        if int(post['mid']) not in [int(post['mid']) for post in posts_visible]:
            post['visible'] = False
            logging.info("Message %s was censored! Not in %s. See %s" % (
                post['mid'], [post['mid'] for post in posts_visible], post['link']))
    except Exception as e:
        logging.exception(e)
        traceback.print_exc()
    return post


def extract_posts(url):
    options = webdriver.ChromeOptions()
    if not opts.show_head():
        options.set_headless(headless=True)
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    tries = 0
    while tries < 3:
        if tries > 0:
            logging.info(
                "Failed to extract posts from %s; trying again (%s/3)" % (url, tries))
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, POST_XPATH))
            )
            elements = driver.find_elements_by_xpath(POST_XPATH)
            posts = [_extract_post_from_element(
                element) for element in elements]
            driver.quit()
            return [post for post in posts if post is not None]
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
        tries += 1
        time.sleep(60)

    logging.info("Aborting; failed to extract posts from %s" % url)
    driver.quit()
    return []
