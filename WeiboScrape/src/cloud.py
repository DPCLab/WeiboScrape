from google.cloud import datastore
from datetime import datetime, timedelta

datastore_client = datastore.Client()

def get_posts_to_check_on():
    query = datastore_client.query(kind='WeiboPost')
    query.add_filter('visible', '=', True)
    query.add_filter('retrieved', '<=', datetime.now() - timedelta(hours=1))
    query.add_filter('retrieved', '>=', datetime.now() - timedelta(hours=24))
    query.order = ['retrieved']
    return list(query.fetch())

def get_urls_to_scrape():
    query = datastore_client.query(kind='WeiboUrl')
    query.order = ['updated']
    return list(query.fetch())

def add_url_to_scrape_list(url):
    url_object = {
        "url": url,
        "updated": None
    }
    key = datastore_client.key("WeiboUrl", url_object['url'])
    entity = datastore.Entity(key=key)
    entity.update(url_object)
    datastore_client.put(entity)

def mark_url_as_scraped(url_object):
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
    datastore_client = datastore.Client()
    post_entities = [_generate_datastore_entity(post) for post in posts]
    datastore_client.put_multi(post_entities)