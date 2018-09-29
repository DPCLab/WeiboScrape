import cloud
import scrape
from multiprocessing import Pool
import sys
import logging
import traceback
import opts

POOL_SIZE = 16

logLevel = logging.INFO
if opts.is_debug():
    logLevel = logging.DEBUG
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logLevel)

def _pull_url(url):
    try:
        logging.info("Pulling from %s" % url['url'])
        posts = scrape.extract_posts(url['url'])
        return (posts, url)
    except Exception as e:
        logging.exception(e)
        traceback.print_exc()

def pull_new_posts():
    logging.info("Pulling new posts...")
    urls = cloud.get_urls_to_scrape()
    p = Pool(POOL_SIZE)
    post_groups = p.map(_pull_url, urls)
    for post_group in post_groups:
        cloud.upsert_posts(post_group[0])
        cloud.mark_url_as_scraped(post_group[1])
    logging.info("Pull complete! Found %s posts across %s urls." % (sum([len(post_group[0]) for post_group in post_groups]), len(urls)))

def check_for_censorship():
    logging.info("Checking for censorship...")
    posts = cloud.get_posts_to_check_on()
    p = Pool(POOL_SIZE)
    posts_updated = p.map(scrape.check_post_for_censorship, posts)
    now_invisible = [post for post in posts_updated if not post['visible']]
    # cloud.upsert_posts(now_invisible)
    logging.info("Found %s now-invisible posts and upserted them" % len(now_invisible))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Insufficient arguments!")
        sys.exit(0)
    if sys.argv[1] == "pull":
        pull_new_posts()
    if sys.argv[1] == "check":
        check_for_censorship()
    if sys.argv[1] == "test_connection":
        import requests
        logging.info("Connection test result: %s" % requests.get("http://captive.apple.com"))