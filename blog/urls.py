from django.conf.urls import url
from blog import views


urlpatterns = [


    url(r"backend/add_article/",views.add_article),

    url(r"up_down/",views.up_down),
    url(r"comment/",views.comment),
    url(r"comment_tree/(\d+)/",views.comment_tree),


    # /blog/xiaohei/tag/python
    # /blog/xiaohei/category/技術
    # /blog/xiaohei/archive/2018-05
    # url(r'(\w+)/tag/(\w+)', views.tag),
    # url(r'(\w+)/category/(\w+)', views.category),
    # url(r'(\w+)/archive/(.+)', views.archive),
    # 三和一 URL
    url(r'(\w+)/(tag|category|archive)/(.+)/', views.home),  # home(request, username, tag, 'python')

    url(r'(\w+)/article/(\d+)/', views.article_detail),  # 文章詳情  article_detail(request, xiaohei, 1)

    url(r'(\w+)/$', views.home),  # home(request, username) #最後的/$必須加上

]