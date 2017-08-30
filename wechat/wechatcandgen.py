# -*- coding: utf-8 -*-
# from py4j.java_gateway import JavaGateway
import jieba
from queryexp import QueryExpansion
from namesearch import NameSearch
from utils import fix_jieba_words

TOLERABLE_MISMATCHS = {u'省', u'市', u'县', u'局', u'厅', u'委', u'集团', u'公司', u'中国'}


def __get_mismatch_positions(s0, s1):
    mis_match = list()
    for i, c in enumerate(s0):
        if c not in s1:
            mis_match.append(i)
    return mis_match


def __get_sub_strs_in_idxes(s, idxes):
    if not idxes:
        return []

    sub_str_ranges = list()
    lp = idxes[0]
    for i in xrange(1, len(idxes)):
        if i == idxes[i - 1] + 1:
            continue
        sub_str_ranges.append((lp, idxes[i - 1]))
        lp = idxes[i]
    sub_str_ranges.append((lp, idxes[-1]))

    strs = list()
    for r in sub_str_ranges:
        strs.append(s[r[0]:r[1] + 1])
    return strs


def all_tolerable_mismatches(s0, s1, num_max_diff_char):
    if s0 == s1:
        return True

    mis_match0 = __get_mismatch_positions(s0, s1)
    mis_match1 = __get_mismatch_positions(s1, s0)
    # print mis_match0, mis_match1

    if len(mis_match0) > num_max_diff_char or len(mis_match1) > num_max_diff_char:
        return False

    diff_strs0 = __get_sub_strs_in_idxes(s0, mis_match0)
    diff_strs1 = __get_sub_strs_in_idxes(s1, mis_match1)

    for s in diff_strs0:
        if s not in TOLERABLE_MISMATCHS:
            return False

    for s in diff_strs1:
        if s not in TOLERABLE_MISMATCHS:
            return False

    return True


class WechatCandGen:
    def __init__(self, acr_name_file, extra_acr_name_file, expansion_exclude_strs_file,
                 abbrev_exclude_strs_file, name_search):

        # gateway = JavaGateway()
        # self.cn_seg_app = gateway.entry_point
        # self.account_id_nickname_dict = account_id_nickname_dict
        self.qe = QueryExpansion(acr_name_file, extra_acr_name_file, expansion_exclude_strs_file,
                                 abbrev_exclude_strs_file)
        self.ns = name_search

    def gen_candidates(self, name_str):
        max_num_candidates_ret = 10
        max_num_candidates_per_name = 7

        # name_str_seg = self.cn_seg_app.segment(name_str)
        name_words = jieba.cut(name_str, HMM=False)
        # name_words = jieba.cut_for_search(name_str)
        name_words = fix_jieba_words(name_words)
        # print ' '.join(name_words)

        exp_names = self.qe.query_expansion_words(name_words)

        # print name_str_seg
        # print ' '.join(exp_names)
        # print name_words

        candidates = list()
        # candidates_tmp = self.__query_es_for_candidates(name_str_seg, max_num_candidates_ret)
        candidates_tmp = self.ns.search_accounts(name_words, max_num_candidates_ret)
        for c in candidates_tmp:
            account_id, account_name, score = c
            # print account_name
            if all_tolerable_mismatches(account_name, name_str, 2):
                # print 'ex', name
                candidates.insert(0, c)
            else:
                candidates.append(c)

        candidates = candidates[:min(len(candidates), max_num_candidates_per_name)]

        # print
        for exp_name in exp_names:
            if len(exp_name) == len(name_str) - name_str.count(' '):
                continue

            pre_len = len(candidates)
            if exp_name != name_str:
                # name_exp_seg = self.cn_seg_app.segment(exp_name)
                # name_words = name_exp_seg.split(' ')
                name_words = fix_jieba_words(jieba.cut(exp_name, HMM=False))
                candidates_tmp = self.ns.search_accounts(name_words, max_num_candidates_ret)
                for c in candidates_tmp:
                    cur_pos = WechatCandGen.__candidate_exist(c, candidates)
                    account_id, account_name, score = c
                    # print account_id, account_name

                    if all_tolerable_mismatches(account_name, exp_name, 2):
                        if cur_pos > -1:
                            candidates[cur_pos], candidates[0] = candidates[0], candidates[cur_pos]
                        else:
                            candidates.insert(0, c)
                        # print 'ex', name
                        continue

                    if cur_pos > -1:
                        continue

                    candidates.append(c)

            candidates = candidates[:min(len(candidates), pre_len + max_num_candidates_per_name)]

        return candidates

    @staticmethod
    def __candidate_exist(candidate, candidates):
        account_id = candidate[0]
        for i, c in enumerate(candidates):
            if account_id == c[0]:
                return i
        return -1


if __name__ == '__main__':
    acr_name_file = 'e:/data/res/wiki/acr_name_filter.txt'
    extra_acr_name_file = 'e:/data/res/wiki/acr_name_man.txt'
    expansion_exclude_strs_file = 'res/expansion_exclude_strs.txt'
    abbrev_exclude_strs_file = 'res/abbrev_exclude_strs.txt'
    account_nickname_file = 'e:/data/wechat/account_nickname.csv'
    account_name_words_file = 'e:/data/wechat/account_nicknames_seg.txt'
    word_name_file = 'e:/data/wechat/word_to_name.txt'
    word_idf_file = 'e:/data/wechat/word_idf.txt'

    jieba.set_dictionary('e:/data/res/seg/dict_fixed.txt')

    ns = NameSearch(account_nickname_file, account_name_words_file, word_name_file, word_idf_file)
    wcg = WechatCandGen(acr_name_file, extra_acr_name_file, expansion_exclude_strs_file,
                        abbrev_exclude_strs_file, ns)
    candidates = wcg.gen_candidates(u'黑龙江日报')
    for c in candidates:
        print c[0], c[1], c[2]

    # mention_names_file = 'e:/data/wechat/mentioned_org_names.txt'
    # f = open(mention_names_file)
    # for line in f:
    #     n, _ = line.strip().decode('utf-8').split('\t')
    #     print n
    #     candidates = wcg.gen_candidates(n)
    #     for c in candidates:
    #         print c[0], c[1], c[2]
    # f.close()
    pass
