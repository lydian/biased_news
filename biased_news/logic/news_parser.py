import urllib
from datetime import datetime
from urlparse import urlparse
from urlparse import parse_qs

import feedparser
from pyquery import PyQuery as pq
from lxml.html import HTMLParser, fromstring

from biased_news.logic.db import get_media
from biased_news.logic.db import add_or_update_news_cluster


BASE_QUERY_URL = 'https://news.google.com/'


def get_cluster_links(query):
    params = {
        'q': query,
        'ned': 'tw',
        'output': 'rss'
    }
    clusters = feedparser.parse(BASE_QUERY_URL + '?' + urllib.urlencode(params))
    links = filter(
        lambda link: 'ncl' in dict(parse_qs(urlparse(link).query)),
        [pq(link).attr('href') for link in pq(clusters['entries'][0]['summary'])('a')])

    return [pq(link).attr('href')
    for cluster in clusters['entries'] for link in pq(cluster['summary'])('a')
    if 'ncl' in parse_qs(urlparse(pq(link).attr('href')).query)
    ]


def get_news_link_in_cluster(cluster_link):
    return [
        url
        for entry in feedparser.parse(cluster_link + '&output=rss')['entries']
        for url in parse_qs(urlparse(entry['link']).query)['url']
    ]


def get_news_content(news_link):
    domain = urlparse(news_link).netloc
    media = get_media(domain)
    if media:
        content = pq(url=news_link)(media['selector'])
        content.remove('script')
        content.remove('iframe')
        content_text = content.text()
        if 'encoding' in media:
            content_text.decode('big5', 'strict').encode('utf8', 'strict')
        return content_text


class NewsCluster(object):

    @classmethod
    def create_many_by_query(cls, query_keyword):
        cluster_links = get_cluster_links(query_keyword)
        news_clusters = [
            NewsCluster.create_by_cluster_link(query_keyword, cluster_link)
            for cluster_link in cluster_links]
        return news_clusters

    @classmethod
    def create_by_cluster_link(cls, query_keyword, cluster_link):
        news_links = get_news_link_in_cluster(cluster_link)
        news_articles = []
        for news_link in news_links:
            content = get_news_content(news_link)
            news_articles.append({
                'link': news_link,
                'description': content,
                'dump_time': datetime.now()
            })
        return cls(cluster_link, query_keyword, news_articles)

    def __init__(self, cluster_link, query_keyword, news_articles):
        self.cluster_link = cluster_link
        self.query_keyword = query_keyword
        self.news_articles = news_articles

    def save(self):
        add_or_update_news_cluster({
            'cluster_link':  self.cluster_link,
            'query_keyword': self.query_keyword,
            'news_articles': self.news_articles
        })
