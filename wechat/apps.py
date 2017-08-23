from __future__ import unicode_literals

import os
import json

from django.apps import AppConfig
from django.conf import settings


class WechatConfig(AppConfig):
    name = 'wechat'

    def __init__(self, app_name, app_module):
        super(WechatConfig, self).__init__(app_name, app_module)
        self.articles = list()
        self.article_mentions_dict = dict()

    def ready(self):
        self.__load_articles()
        self.__init_article_mentions_dict()

    def __init_article_mentions_dict(self):
        mentions_file = settings.MENTIONS_FILE
        print 'loading %s ...' % mentions_file

        f = open(mentions_file)
        for line in f:
            m = json.loads(line)
            # TODO
            # if m['name_str'] in self.hide_name_strs:
            #     continue

            article_id = m['docid']

            cur_article_mentions = self.article_mentions_dict.get(article_id, list())
            if not cur_article_mentions:
                self.article_mentions_dict[article_id] = cur_article_mentions
            cur_article_mentions.append(m)
        f.close()

    def __load_articles(self):
        articles_file = settings.ARTICLES_FILE
        print 'loading %s ...' % articles_file
        f = open(articles_file)
        for line in f:
            article = json.loads(line)
            self.articles.append(article)
        f.close()

