from django.conf.urls import url
# from django.contrib.auth import views as auth_views

from . import views

app_name = "wechat"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^label/(?P<article_idx>[0-9]+)/$', views.label, name='label'),
    url(r'^article/(?P<article_idx>[0-9]+)/$', views.show_article, name='article'),
    url(r'^search/$', views.search_candidates, name='search'),
]
