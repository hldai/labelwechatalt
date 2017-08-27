# -*- coding: utf-8 -*-

import time
import math

DEF_IDF = 13.0
FREQ_WORD_LIM = 5000


class NameSearch:
    def __init__(self, account_name_file, account_name_words_file, word_name_file, word_idf_file):
        self.word_names = dict()
        self.account_names = list()
        self.account_name_words = list()
        self.account_ids = list()
        self.word_idf = dict()

        self.__load_word_name_file(word_name_file)
        self.__load_account_names(account_name_file)
        self.__load_account_name_words(account_name_words_file)
        self.__load_word_idf_values(word_idf_file)

    def search_accounts(self, words, max_num_accounts):
        words = set(words)
        accounts = self.__search(words, max_num_accounts, True)
        if len(accounts) < max_num_accounts:
            accounts = self.__search(words, max_num_accounts, True)
        return accounts

    def __search(self, words, max_num_accounts, ignore_freq_words):
        accounts = list()
        for w in words:
            tmp_idxs = self.word_names.get(w, None)
            if not tmp_idxs:
                continue

            if ignore_freq_words and len(tmp_idxs) > FREQ_WORD_LIM:
                continue

            for idx in tmp_idxs:
                cur_score = self.__get_score(words, self.account_name_words[idx])
                cur_account = (self.account_ids[idx], self.account_names[idx], cur_score)
                NameSearch.__insert_account(accounts, cur_account, max_num_accounts)
        return accounts

    @staticmethod
    def __insert_account(cur_accounts, new_account, max_num_accounts):
        if len(cur_accounts) == max_num_accounts and cur_accounts[-1][2] > new_account[2]:
            return

        if not cur_accounts or cur_accounts[-1][2] > new_account[2]:
            cur_accounts.append(new_account)
            return

        if cur_accounts[-1][0] == new_account[0]:
            return

        p = len(cur_accounts) - 2
        while p > -1:
            if cur_accounts[p][0] == new_account[0]:
                return

            if cur_accounts[p][2] > new_account[2]:
                break
            p -= 1
        cur_accounts.insert(p + 1, new_account)

        if len(cur_accounts) > max_num_accounts:
            cur_accounts.pop()

    def __get_score(self, qwords, name_words):
        v = 0
        s1, s2 = 0, 0
        for w in qwords:
            widf = self.word_idf.get(w, DEF_IDF)
            s1 += widf * widf
            if w in name_words:
                v += widf * widf

        for w in name_words:
            widf = self.word_idf.get(w, DEF_IDF)
            s2 += widf * widf

        return v / math.sqrt(s1) / math.sqrt(s2)

    def __load_account_name_words(self, account_name_words_file):
        print 'loading %s ...' % account_name_words_file
        f = open(account_name_words_file)
        for line in f:
            _, name_seg = line.strip().decode('utf-8').split('\t')
            self.account_name_words.append(set(name_seg.split(' ')))
        f.close()

    def __load_word_name_file(self, word_name_file):
        print 'loading %s ...' % word_name_file
        f = open(word_name_file)
        for line in f:
            w = line.strip().decode('utf-8')
            line = f.next()
            vals = line.strip().split(' ')
            idxs = [int(v) for v in vals]
            self.word_names[w] = idxs
        f.close()

    def __load_account_names(self, account_name_file):
        print 'loading %s ...' % account_name_file
        f = open(account_name_file)
        f.next()
        for line in f:
            vals = line.strip().decode('utf-8').split(',')
            self.account_ids.append(vals[0])
            self.account_names.append(vals[1])
        f.close()

    def __load_word_idf_values(self, word_idf_file):
        print 'loading %s ...' % word_idf_file
        f = open(word_idf_file)
        for line in f:
            vals = line.strip().decode('utf-8').split('\t')
            w, idf = vals
            idf = float(idf)
            self.word_idf[w] = idf
        f.close()


if __name__ == '__main__':
    account_name_file = 'e:/data/wechat/account_nickname.csv'
    account_name_words_file = 'e:/data/wechat/account_nicknames_seg.txt'
    word_name_file = 'e:/data/wechat/word_to_name.txt'
    word_idf_file = 'e:/data/wechat/word_idf.txt'
    ns = NameSearch(account_name_file, account_name_words_file, word_name_file, word_idf_file)
    words = [u'黑龙江日报']
    accounts = ns.search_accounts(words, 10)
    print len(accounts)
    for acc in accounts:
        print acc[1], acc[2]
    time.sleep(10)
