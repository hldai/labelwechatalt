from __future__ import unicode_literals

import os
import json

from django.apps import AppConfig
from django.conf import settings

from wechatcandgen import WechatCandGen


class WechatConfig(AppConfig):
    name = 'wechat'

    def __init__(self, app_name, app_module):
        super(WechatConfig, self).__init__(app_name, app_module)
        self.articles = list()
        self.article_mentions_dict = dict()
        self.account_id_nickname_dict = dict()
        self.wcg = None

    def ready(self):
        self.__load_articles()
        self.__init_article_mentions_dict()
        self.__load_account_id_nickname()

        acr_name_file = settings.ACR_NAME_FILE
        extra_acr_name_file = settings.EXTRA_ACR_NAME_FILE
        expansion_exclude_strs_file = settings.EXPANSION_EXCLUDE_STRS_FILE
        abbrev_exclude_strs_file = settings.ABBREV_EXCLUDE_STRS_FILE
        es_url = settings.ES_URL
        self.wcg = WechatCandGen(acr_name_file, extra_acr_name_file, expansion_exclude_strs_file,
                                 abbrev_exclude_strs_file, self.account_id_nickname_dict, es_url)

    def __load_account_id_nickname(self):
        account_id_nickname_file = settings.ACCOUNT_INFO_FILE
        print 'loading %s ...' % account_id_nickname_file
        f = open(account_id_nickname_file)
        f.next()
        for line in f:
            # print line
            vals = line.decode('utf-8').strip().split(',')
            acc_id = vals[0]
            acc_name = vals[1]
            self.account_id_nickname_dict[acc_id] = acc_name
        f.close()

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

