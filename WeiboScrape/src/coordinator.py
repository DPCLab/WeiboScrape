import scrape
from multiprocessing import Pool
import sys
import logging
import traceback
import opts
import cloud

POOL_SIZE = 16

logLevel = logging.INFO
if opts.is_debug():
    logLevel = logging.DEBUG
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logLevel)


def _pull_url(url):
    try:
        logging.info("Pulling from %s" % url['url'])
        posts = scrape.extract_posts(url['url'])
        cloud.upsert_posts(posts)
        cloud.mark_url_as_scraped(url)
        return (posts, url)
    except Exception as e:
        logging.exception(e)
        traceback.print_exc()


def pull_new_posts():
    logging.info("Pulling new posts...")
    urls = cloud.get_urls_to_scrape()
    p = Pool(POOL_SIZE)
    post_groups = p.map(_pull_url, urls)
    logging.info("Pull complete! Found %s posts across %s urls." % (
        sum([len(post_group[0]) for post_group in post_groups]), len(urls)))

def _check_for_censorship_wrapper(post):
    checked_post = scrape.check_post_for_censorship(post)
    if checked_post['visible'] == False:
        cloud.upsert_posts([checked_post])
    return checked_post

def check_for_censorship():
    logging.info("Checking for censorship...")
    posts = cloud.get_posts_to_check_on()
    p = Pool(POOL_SIZE)
    posts_updated = p.map(_check_for_censorship_wrapper, posts)
    now_invisible = [post for post in posts_updated if not post['visible']]
    logging.info("Found %s now-invisible posts and upserted them" %
                 len(now_invisible))


def monitor_url():
    url = sys.argv[2]
    logging.info("Adding %s to monitored urls..." % url)
    cloud.add_url_to_scrape_list(url)
    logging.info("Added %s to monitored urls!" % url)

def mark_invisible_posts_as_visible():
    logging.info("Marking invisible posts as visible...")
    posts = cloud.get_invisible_posts()
    for post in posts:
        post['visible'] = True
    cloud.upsert_posts(posts)

def add_potentially_censored_key_to_invisible_posts():
    logging.info("Marking potentially censored posts as such...")
    posts = cloud.get_invisible_posts()
    for post in posts:
        post['potentially_censored'] = True
    cloud.upsert_posts(posts)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Insufficient arguments!")
        sys.exit(0)
    if sys.argv[1] == "pull":
        pull_new_posts()
    if sys.argv[1] == "check":
        check_for_censorship()
    if sys.argv[1] == "monitor":
        monitor_url()
    if sys.argv[1] == "revisible":
        mark_invisible_posts_as_visible()
    if sys.argv[1] == "markpotentiallycensored":
        add_potentially_censored_key_to_invisible_posts()
    if sys.argv[1] == "test_connection":
        import requests
        logging.info("Connection test result: %s" %
                     requests.get("http://captive.apple.com"))
