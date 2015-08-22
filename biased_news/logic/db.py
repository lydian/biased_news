# -*- coding: utf-8 -*-
from pymongo import MongoClient


USER = 'test_user'
PASSWORD = 'a33kuoisdating'
MONGO_URL = 'mongodb://%s:%s@ds033113.mongolab.com:33113/heroku_0hfvrxm4' % (USER, PASSWORD)

client = MongoClient(MONGO_URL)
db = client.heroku_0hfvrxm4

NEWS_CLUSTERS = db.news_clusters
MEDIAS = db.medias
QUERY_KEYWORDS = db.query_keywords


def add_or_update_news_cluster(news_cluster):
    return NEWS_CLUSTERS.update(
        {'cluster_link': news_cluster['cluster_link']},
        news_cluster,
        upsert=True)


def add_news_article(news_cluster_link, articles):
    return NEWS_CLUSTERS.update_one(
        {'cluster_link': news_cluster_link},
        {'news_articles': {'$add': articles}}
    )

def get_news_cluster(query=None):
    return NEWS_CLUSTERS.find(query)


def add_media(media):
    return MEDIAS.insert_one(media)


def get_media(domain):
    row = MEDIAS.find_one({'domain': domain})
    if row:
        return row


def add_query_keywords(keyword):
    row = QUERY_KEYWORDS.find_one({'keyword': keyword})
    if row is None:
        QUERY_KEYWORDS.insert_one({'keyword': keyword, 'count': 1})
    else:
        QUERY_KEYWORDS.update_one({'keyword': keyword}, {'$inc': {'count': 1}})


def get_keywords():
    return QUERY_KEYWORDS.find()
