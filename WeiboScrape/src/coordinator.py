import cloud
import scrape
from multiprocessing import Pool
import sys
import logging
import traceback
import opts

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
    p = Pool(8)
    post_groups = p.map(_pull_url, urls)
    for post_group in post_groups:
        cloud.upsert_posts(post_group[0])
        cloud.mark_url_as_scraped(post_group[1])
    logging.info("Pull complete! Found %s posts." % sum([len(post_group[0]) for post_group in post_groups]))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Insufficient arguments!")
        sys.exit(0)
    if sys.argv[1] == "pull":
        pull_new_posts()
    if sys.argv[1] == "test_connection":
        import requests
        logging.info("Connection test result: %s" % requests.get("http://captive.apple.com"))