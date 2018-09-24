import cloud
import scrape
from multiprocessing import Pool

def _pull_url(url):
    posts = scrape.extract_posts(url['url'])
    cloud.upsert_posts(posts)
    cloud.mark_url_as_scraped(url)

def pull_new_posts():
    urls = cloud.get_urls_to_scrape()
    p = Pool(8)
    p.map(_pull_url, urls)