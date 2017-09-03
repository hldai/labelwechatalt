from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
# from django.contrib.auth import views as auth_views
from django.apps import apps

import articledata


def index(request):
    # if not request.user.is_authenticated():
    #     return auth_views.login(request, template_name="login.html")
    #
    # context = dict()
    # context['username'] = username = request.user.username
    # num_articles = articledata.get_user_num_articles(username)
    # context['num_articles'] = num_articles
    # #     context['num_mentions'] = reviewdata.get_user_num_labeled_mentions(username)
    # context['label_article_idx'] = 1 if num_articles == 0 else num_articles
    # return render(request, 'wechat/userlabelstat.html', context)
    return HttpResponse('Hi')


def show_article(request, article_idx):
    wechat_config = apps.get_app_config('wechat')
    article_idx = int(article_idx)
    articles = wechat_config.articles

    if article_idx < 1 or article_idx > len(articles):
        return HttpResponse('Article not exist.')

    article = articles[article_idx - 1]
    mentions = wechat_config.article_mentions_dict.get(article['article_id'], None)
    label_results = None

    highlighted_article = articledata.highlight_mentions_para(article['contents'], mentions, label_results)

    context = dict()
    context['username'] = 'dhl'
    context['num_mentions'] = len(mentions)
    context['article_title'] = article['title']
    context['account'] = articledata.get_account_info(wechat_config, article['account_id'])
    context['highlighted_article'] = highlighted_article
    context['user_article_idx'] = article_idx
    context['prev_article_idx'] = article_idx - 1 if article_idx > 1 else 1
    context['next_article_idx'] = article_idx + 1
    context['mention_candidates'] = articledata.get_candidates_of_mentions(wechat_config, mentions)
    return render(request, 'wechat/article.html', context)


def logout(request):
    return HttpResponse('Hi')
    # return auth_views.logout(request, next_page=reverse('wechat:login'))


def label(request, article_idx):
    # tbeg = time()
    articledata.update_label_result(request.user.username, request.POST)
    # return HttpResponse('OK' + rev_idx)
    # print time() - tbeg
    return HttpResponseRedirect(reverse('wechat:article', args=(request.user.username, article_idx,)))


def delete_label(request, user_article_idx, mention_id):
    articledata.delete_label_result(mention_id, request.user.username)
    return HttpResponseRedirect(reverse('wechat:article', args=(request.user.username, user_article_idx,)))


def search_candidates(request):
    mention_id = request.POST['mention_id']
    qstr = request.POST['query_str']
    # reviewed_city = request.POST['reviewed_biz_city']
    wechat_config = apps.get_app_config('wechat')
    candidates = articledata.search_candidates(wechat_config, qstr)
    # print candidates
    context = {
        'mention_id': mention_id,
        'candidates': candidates,
        "candidate_type": "ser"
    }
    return render(request, 'wechat/candidates.html', context)
