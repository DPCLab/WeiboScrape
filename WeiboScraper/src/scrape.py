from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import re

POST_XPATH = '//div[@action-type="feed_list_item" and @mid]'

def _extract_post_from_element(element):
    html = element.get_attribute("outerHTML")
    soup = BeautifulSoup(html, 'html.parser')
    mid = int(soup.find('div', {"action-type": "feed_list_item"}).attrs['mid'])
    uid = int(re.search(r"\/\/weibo.com\/(.*)(\?.*)", soup.find('a', class_="name").attrs['href']).group(1))
    link = soup.find("p", class_="from").find('a').attrs['href']
    text = soup.find("p", class_="txt").getText()
    return {
        "mid": mid,
        "uid": uid,
        "link": link,
        "text": text
    }

def extract_posts(url):
    driver = webdriver.Firefox()
    driver.get(url)
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, POST_XPATH))
    )
    elements = driver.find_elements_by_xpath(POST_XPATH)
    posts = [_extract_post_from_element(element) for element in elements]
    return posts