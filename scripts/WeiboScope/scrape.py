'''
WeiboScope/scrape.py
Read the latest censored posts from Weiboscope and store them in a Google Database
'''

import requests
import re

def readLatestPosts():
    r = requests.get("http://weiboscope.jmsc.hku.hk/latest.py")

    # Clean up the html
    html = r.text.replace("<body style='background-color:#FFFFFF;'><h3>Latest permission denied posts (max 200, order by publication date):</h3><ol>\n", "")
    html = re.sub("<(br|/ol|/body|li)>", "", html)
    html = re.sub("( {2,}|\n|\u200b)", " ", html)

    posts = []
    for post in html.split("</li>")[:-1]:
        post = post.strip()

        text = post[post.index(" | ") + 3:]
        timestamp = post[post.index(">") + 1:post.index("</a>")]
        url = post[post.index("http"):post.index(">") - 1]

        posts.append({"text": text, "timestamp": timestamp, "url": url})

    return posts

readLatestPosts()
