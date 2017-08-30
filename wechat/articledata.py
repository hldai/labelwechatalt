# -*- coding: utf-8 -*-

import json
import socket

from django.shortcuts import get_object_or_404

# from models import LabelResultWe


def get_label_results(mentions, username):
    label_result_dict = dict()
    # for m in mentions:
    #     try:
    #         mention_id = m['mention_id']
    #         lr = LabelResultWe.objects.get(mention_id=mention_id, username=username)
    #         label_result_dict[mention_id] = lr
    #     except LabelResultWe.DoesNotExist:
    #         continue
    return label_result_dict


def __get_candidates_info(candidates, wechat_config):
    candidate_dicts = list()
    for c in candidates:
        account_name = wechat_config.account_id_nickname_dict.get(c[0], 'NULL')
        # print c, account_name
        cdict = {'account_id': c[0], 'name': account_name}
        candidate_dicts.append(cdict)
    return candidate_dicts


def get_candidates_of_mentions(wechat_config, mentions):
    if not mentions:
        return None

    mention_candidates = list()
    for m in mentions:
        # mention_id = m['mention_id']
        candidates = wechat_config.wcg.gen_candidates(m['name_str'])
        candidate_dicts = __get_candidates_info(candidates, wechat_config)
        first_candidate_id = candidate_dicts[0]['account_id'] if candidate_dicts else 'NULL'
        tup = (m, False, candidate_dicts, first_candidate_id)
        mention_candidates.append(tup)
    return mention_candidates


def get_account_info(wechat_config, account_id):
    name = wechat_config.account_id_nickname_dict.get(account_id, 'NULL')
    return {'name': name}


def highlight_mentions(rev_text, mentions, label_results):
    new_text = u''
    last_pos = 0
    for i, m in enumerate(mentions):
        span_class = 'span-mention'
        if m.mention_id in label_results:
            span_class += ' span-mention-labeled'
        span_attrs = 'id="mention-span-%d" class="%s" onclick="mentionClicked(%d, \'%s\')' % (
            i, span_class, i, m.mention_id)
        new_text += u'%s<span %s">%s</span>' % (rev_text[last_pos:m.begpos], span_attrs,
                                                rev_text[m.begpos:m.endpos + 1])
        last_pos = m.endpos + 1

    new_text += rev_text[last_pos:]
    return new_text.replace('\n', '<br/>')


def __paragraph_mention_dict(mentions):
    pidx_mention_dict = dict()
    if not mentions:
        return pidx_mention_dict
    for m in mentions:
        para_idx = m['para_idx']
        cur_para_mentions = pidx_mention_dict.get(para_idx, list())
        if not cur_para_mentions:
            pidx_mention_dict[para_idx] = cur_para_mentions
        cur_para_mentions.append(m)
    return pidx_mention_dict


def __highlight_mentions_in_text(mentions, text, label_results, start_mention_idx):
    new_text = u''
    last_pos = 0
    for i, m in enumerate(mentions):
        mention_idx = i + start_mention_idx
        span_class = 'span-mention'
        mention_id = m['mention_id']
        if label_results and mention_id in label_results:
            span_class += ' span-mention-labeled'
        if start_mention_idx == 0 and i == 0:
            span_class += ' span-mention-first'
        span_attrs = 'id="mention-span-%s" class="%s" onclick="mentionClicked(%d, \'%s\')' % (
            mention_id, span_class, mention_idx, mention_id)
        left_pos, right_pos = m['span']
        new_text += u'%s<span %s">%s</span>' % (text[last_pos:left_pos], span_attrs,
                                                text[left_pos:right_pos + 1])
        last_pos = right_pos + 1

    new_text += text[last_pos:]
    return new_text.replace('\n', '<br/>')


def highlight_mentions_para(contents, mentions, label_results):
    disp_text = u''
    pidx_mention_dict = __paragraph_mention_dict(mentions)
    start_mention_idx = 0
    for i, content in enumerate(contents):
        if disp_text:
            disp_text += '<br>'

        mentions = pidx_mention_dict.get(i, None)
        if not mentions:
            disp_text += content
            continue

        highlighted_text = __highlight_mentions_in_text(mentions, content,
                                                        label_results, start_mention_idx)
        start_mention_idx += len(mentions)
        disp_text += highlighted_text
    return disp_text


def search_candidates(wechat_config, qstr):
    candidates = wechat_config.wcg.gen_candidates(qstr)
    candidate_dicts = __get_candidates_info(candidates, wechat_config)
    # data = json.dumps({'query': 'candidates', 'name_str': qstr})
    # res = __query_wechat_dispatcher(data)
    return candidate_dicts


def update_label_result(username, post_data):
    # LabelResultWe.update_label_result(username, post_data)
    pass


def delete_label_result(mention_id, username):
    # lr = LabelResult.objects.get(mention_id=mention_id, username=username)
    # lr = get_object_or_404(LabelResultWe, mention_id=mention_id, username=username)
    # lr.delete()
    # user_num_mentions[username] -= 1
    pass
