# -*- coding: utf-8 -*-
import time
from elasticsearch import Elasticsearch
from py4j.java_gateway import JavaGateway

from queryexp import QueryExpansion

es_url = 'localhost:9200'
index_name = 'wechat'
nickname_doc_type = 'nickname'

TOLERABLE_MISMATCHS = {u'省', u'市', u'县', u'局', u'厅', u'委', u'集团', u'公司', u'中国'}


def load_account_id_nickname(account_id_nickname_file, dst_dict):
    f = open(account_id_nickname_file)
    f.next()
    for line in f:
        vals = line.strip().split(',')
        acc_id = vals[0]
        acc_name = vals[1].decode('utf-8')
        dst_dict[acc_id] = acc_name
    f.close()


def __add_alias_to_dict(alias_dict, name, alias):
    aliases = alias_dict.get(name, None)
    if not aliases:
        aliases = list()
        alias_dict[name] = aliases
    aliases.append(alias)


def load_redirects(redirect_file):
    alias_dict = dict()
    f = open(redirect_file, 'r')
    for line in f:
        vals = line.strip().split('\t')
        __add_alias_to_dict(alias_dict, vals[0], vals[1])
        __add_alias_to_dict(alias_dict, vals[1], vals[0])
    f.close()

    return alias_dict


def load_expansion_dict(redirect_file):
    anchor_text_file = 'e:/data/res/wiki/anchor_text_list.txt'

    return load_redirects(redirect_file)


def __load_acronym_expansion_file(acronym_expansion_file):
    acr_exp_dict = dict()
    f = open(acronym_expansion_file, 'r')
    for line0 in f:
        line1 = f.next().strip()
        acr_exp_dict[line0.strip()] = line1.replace('\t', ' ')
    f.close()
    return acr_exp_dict


def load_acronym_to_name(acronym_name_file, exclude_strs):
    acr_name_dict = dict()
    f = open(acronym_name_file, 'r')
    for line in f:
        line = line.strip().decode('utf-8')
        acr, name, _ = line.split('\t')

        if exclude_strs and acr in exclude_strs:
            continue

        acr_name_dict[acr] = name
        # print acr, name_max

    f.close()

    return acr_name_dict


def load_name_to_acronym(acronym_name_file):
    name_acr_cnt_dict = dict()
    f = open(acronym_name_file, 'r')
    for line in f:
        line = line.strip().decode('utf-8')
        acr, name, cnt = line.split('\t')
        cnt = int(cnt)

        tup = name_acr_cnt_dict.get(name, None)
        if not tup or tup[1] < cnt:
            name_acr_cnt_dict[name] = (acr, cnt)
        # print acr, name_max
    f.close()

    name_acr_dict = dict()
    for name, (acr, cnt) in name_acr_cnt_dict.iteritems():
        name_acr_dict[name] = acr

    return name_acr_dict


def expand_word(word, acr_name_dict):
    name_exp = ''
    pl = 0
    while pl < len(word):
        pr = len(word)
        exps = ''
        while pr > pl:
            exps = acr_name_dict.get(word[pl:pr], None)
            if exps:
                break
            pr -= 1

        if pr > pl:
            name_exp += exps
            pl = pr
        else:
            name_exp += word[pl]
            pl = pr + 1

    return name_exp


def expand_name_by_words(name_words, acr_name_dict, exclude_strs):
    name_exp = ''
    lw = len(name_words)
    l = 0
    while l < lw:
        r = lw
        cur_str = ''
        while r > l:
            cur_str = ''.join(name_words[l:r])
            if cur_str in exclude_strs:
                break
            r -= 1

        if r > l:
            name_exp += cur_str
            l = r
        else:
            name_exp += expand_word(name_words[l], acr_name_dict)
            l += 1
    return name_exp


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


def get_diff_strs(s0, s1, num_max_diff_char):
    mis_match0 = __get_mismatch_positions(s0, s1)
    mis_match1 = __get_mismatch_positions(s1, s0)
    # print mis_match0, mis_match1

    if len(mis_match0) > num_max_diff_char or len(mis_match1) > num_max_diff_char:
        return

    diff_strs0 = __get_sub_strs_in_idxes(s0, mis_match0)
    diff_strs1 = __get_sub_strs_in_idxes(s1, mis_match1)
    # print diff_strs0, diff_strs1

    ds = list()
    if diff_strs0:
        ds += diff_strs0
    if diff_strs1:
        ds += diff_strs1

    # print '\n'.join(ds)
    return ds


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
                 abbrev_exclude_strs_file, account_id_nickname_dict, es_url):
        self.es = Elasticsearch([es_url])

        gateway = JavaGateway()
        self.cn_seg_app = gateway.entry_point
        self.account_id_nickname_dict = account_id_nickname_dict
        self.qe = QueryExpansion(acr_name_file, extra_acr_name_file, expansion_exclude_strs_file,
                                 abbrev_exclude_strs_file, self.cn_seg_app)

    def gen_candidates(self, name_str):
        max_num_candidates_ret = 20
        max_num_candidates_per_name = 7
        name_str_seg = self.cn_seg_app.segment(name_str)

        name_words = name_str_seg.split(' ')
        exp_names = self.qe.query_expansion_words(name_words)

        # print ' '.join(exp_names)
        # print name_str_seg

        candidates = list()
        candidates_tmp = self.__query_es_for_candidates(name_str_seg, max_num_candidates_ret)
        for c in candidates_tmp:
            # print c[1]
            name = self.account_id_nickname_dict.get(c[0], None)
            if not name:
                continue

            if all_tolerable_mismatches(name, name_str, 2):
                # print 'ex', name
                candidates.insert(0, (c[0], name, c[2]))
            else:
                candidates.append((c[0], name, c[2]))

        candidates = candidates[:min(len(candidates), max_num_candidates_per_name)]

        # print
        for exp_name in exp_names:
            if len(exp_name) == len(name_str) - name_str.count(' '):
                continue

            pre_len = len(candidates)
            if exp_name != name_str:
                name_exp_seg = self.cn_seg_app.segment(exp_name)
                candidates_tmp = self.__query_es_for_candidates(name_exp_seg, max_num_candidates_ret)
                for c in candidates_tmp:
                    cur_pos = WechatCandGen.__candidate_exist(c, candidates)

                    name = self.account_id_nickname_dict.get(c[0], None)
                    if not name:
                        continue

                    if all_tolerable_mismatches(name, exp_name, 2):
                        if cur_pos > -1:
                            candidates[cur_pos], candidates[0] = candidates[0], candidates[cur_pos]
                        else:
                            candidates.insert(0, (c[0], name, c[2]))
                        # print 'ex', name
                        continue

                    if cur_pos > -1:
                        continue

                    candidates.append((c[0], name, c[2]))

            candidates = candidates[:min(len(candidates), pre_len + max_num_candidates_per_name)]

        return candidates

    def __query_es_for_candidates(self, name_seg, max_res_size):
        candidates = list()
        hits_info = self.__match_name_es(name_seg, max_res_size)
        hits = hits_info['hits']
        for hit in hits:
            # print hit['_id'], hit['_score']
            # print hit['_source']['name']
            candidates.append((hit['_id'], hit['_source']['name'], hit['_score']))
        return candidates

    def __match_name_es(self, name_str, max_res_size=10):
        qbody = {
            # "query": {"match_all": {}}
            "query": {"match": {"name": name_str}}
        }

        res = self.es.search(index=index_name, doc_type=nickname_doc_type, body=qbody, size=max_res_size)
        return res['hits']

    @staticmethod
    def __candidate_exist(candidate, candidates):
        account_id = candidate[0]
        for i, c in enumerate(candidates):
            if account_id == c[0]:
                return i
        return -1


def __name_abbrev_test():
    acr_name_file = 'e:/data/res/wiki/acr_name_filter.txt'
    extra_acr_name_file = 'e:/data/res/wiki/acr_name_man.txt'
    expansion_exclude_strs_file = 'res/expansion_exclude_strs.txt'
    abbrev_exclude_strs_file = 'res/abbrev_exclude_strs.txt'
    account_nickname_file = 'e:/data/wechat/account_nickname.csv'
    name_str_file = 'e:/data/wechat/20w/name_strs_stat.txt'
    dst_file = 'e:/data/wechat/tmp/name_strs_acr.txt'

    account_id_nickname_dict = dict()
    load_account_id_nickname(account_nickname_file, account_id_nickname_dict)

    gateway = JavaGateway()
    cn_seg_app = gateway.entry_point

    # qe = QueryExpansion(acr_name_file, extra_acr_name_file, expansion_exclude_strs_file,
    #                     abbrev_exclude_strs_file, cn_seg_app)

    wcg = WechatCandGen(acr_name_file, extra_acr_name_file, expansion_exclude_strs_file,
                        abbrev_exclude_strs_file, account_id_nickname_dict, es_url)
    # print qe.abbrev_name(u'福建省高级人民法院')
    candidates = wcg.gen_candidates(u'四川省人社厅')
    for c in candidates:
        print c[1]

    # f = open(name_str_file)
    # fout = open(dst_file, 'wb')
    # for i, line in enumerate(f):
    #     vals = line.strip().split('\t')
    #     name_str = vals[0].decode('utf-8')
    #
    #     # name_abr = qe.abbrev_name(name_str)
    #     # if name_abr:
    #         # print name_str, name_exp
    #         # if name_abr.endswith(u'大学'):
    #         #     print name_str, name_abr
    #         # fout.write((u'%s\t%s\n' % (name_str, name_abr)).encode('utf-8'))
    #     exp_names = qe.query_expansion(name_str)
    #     if exp_names:
    #         fout.write(name_str.encode('utf-8'))
    #         for n in exp_names:
    #             fout.write((u'\t%s' % n).encode('utf-8'))
    #         fout.write('\n')
    #
    #     if i % 10000 == 0:
    #         print i
    #     # if i > 10000:
    #     #     break
    #
    # f.close()
    # fout.close()


if __name__ == '__main__':
    # __find_substr_test()
    # __name_expansion()
    __name_abbrev_test()
    # get_diff_strs(u'岩溪镇公安', u'岩溪公安局')
    pass
