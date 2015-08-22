import unicodedata

from biased_news.logic.news_parser import NewsCluster
from biased_news.logic.db import get_keywords

class NewsParserBatch(object):


    def run(self):
        keywords = get_keywords()

        for keyword_row in keywords:
            keyword = unicodedata.normalize(
                'NFKD', keyword_row['keyword']).encode('utf-8')
            clusters = NewsCluster.create_many_by_query(keyword)
            for cluster in clusters:
                cluster.save()


if __name__ == '__main__':
    NewsParserBatch().run()
