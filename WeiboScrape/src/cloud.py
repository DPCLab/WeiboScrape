from datetime import datetime, timedelta
import sys
import opts
import logging

def get_posts_to_check_on():
    logging.info("Loading posts to check on...")
    query = datastore_client.query(kind='WeiboPost')
    query.add_filter('visible', '=', True)
    query.add_filter('retrieved', '<=', datetime.now() - timedelta(hours=1))
    query.add_filter('retrieved', '>=', datetime.now() - timedelta(hours=24))
    query.order = ['retrieved']
    return list(query.fetch())

def get_urls_to_scrape():
    logging.info("Loading urls to scrape...")
    if opts.is_local():
        logging.info("Local mode enabled; returning test data.")
        return [{"url": "https://s.weibo.com/weibo/hi?topnav=1&wvr=6&b=1"}]
    query = datastore_client.query(kind='WeiboUrl')
    query.order = ['updated']
    return list(query.fetch())

def add_url_to_scrape_list(url):
    logging.info("Adding url to scrape list: %s" % str(url))
    if opts.is_local():
        logging.info("Aborted scrape list add because in local mode.")
        return
    url_object = {
        "url": url,
        "updated": None
    }
    key = datastore_client.key("WeiboUrl", url_object['url'])
    entity = datastore.Entity(key=key)
    entity.update(url_object)
    datastore_client.put(entity)

def mark_url_as_scraped(url_object):
    logging.info("Marking url as scraped: %s" % str(url_object))
    if opts.is_local():
        logging.info("Aborted because in local mode.")
        return
    key = datastore_client.key("WeiboUrl", url_object['url'])
    entity = datastore.Entity(key=key)
    url_object['updated'] = datetime.now()
    entity.update(url_object)
    datastore_client.put(entity)

def _generate_datastore_entity(post):
    key = datastore_client.key("WeiboPost", post['mid'])
    entity = datastore.Entity(key=key)
    entity.update(post) # puts all of the data into the entity
    return entity

def upsert_posts(posts):
    logging.info("Upserting %s posts..." % str(len(posts)))
    if opts.is_local():
        logging.info("Aborting upsert because in local mode.")
        return
    datastore_client = datastore.Client()
    post_entities = [_generate_datastore_entity(post) for post in posts]
    datastore_client.put_multi(post_entities)

if not opts.is_local():
    from google.cloud import datastore
    datastore_client = datastore.Client()