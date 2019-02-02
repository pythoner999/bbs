from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from geetest import GeetestLib
from blog import forms, models
from django.db.models import Count
from django.db.models import F
from bs4 import BeautifulSoup
from bbs import settings
import logging
import json
import os
import re
from blog.utils import tools

# 生成一個logger實例，專門用來記錄日誌
logger = logging.getLogger(__name__)


# Create your views here.


# 使用極驗滑動驗證碼的登錄

def login(request):
    # if request.is_ajax():  # 如果是AJAX請求
    if request.method == "POST":
        # 初始化一個給AJAX返回的數據
        ret = {"status": 0, "msg": ""}
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 獲取極驗 滑動驗證碼相關的參數
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 驗證碼正確
            # 利用auth模塊做驗證碼和密碼的校驗
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用戶名和密碼正確
                # 給用戶做登錄
                auth.login(request, user)  # 將登錄用戶賦值給 request.user
                ret["msg"] = "/index/"
            else:
                # 用戶名或密碼錯誤
                ret["status"] = 1
                ret["msg"] = "用戶名或密碼錯誤！"
        else:
            ret["status"] = 1
            ret["msg"] = "驗證碼錯誤！"

        return JsonResponse(ret)
    return render(request, "login2.html")


# 註銷
def logout(request):
    auth.logout(request)
    return redirect("/index/")


def index(request):
    # 查詢所有的文章列表
    article_list = models.Article.objects.all()
    up_count_rank = list(models.Article.objects.order_by("-up_count")[:3].values("title", "nid", "user__username"))
    tools.choose_chinese_character(up_count_rank)
    comment_count_rank = list(models.Article.objects.order_by("-comment_count")[:3].values("title", "nid", "user__username"))
    tools.choose_chinese_character(comment_count_rank)
    view_count_rank = list(models.Article.objects.order_by("-view_count")[:3].values("title", "nid", "user__username"))
    tools.choose_chinese_character(view_count_rank)
    return render(request, "index.html", {"article_list": article_list, "up_count_rank": up_count_rank, "comment_count_rank": comment_count_rank, "view_count_rank": view_count_rank})


pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 處理極驗 獲取驗證碼的視圖
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 註冊
def register(request):
    if request.method == "POST":
        print(request.POST)
        print("=" * 120)
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        print(request.POST)
        # form組件校驗
        if form_obj.is_valid():

            # 校驗通過，去數據庫創建一個新用戶
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            blog_title = form_obj.cleaned_data.pop('blog_title')
            blog_obj = models.Blog.objects.create(title=blog_title, site=form_obj.cleaned_data.get('username'))
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img, blog=blog_obj)
            ret["msg"] = "/index/"
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            print(ret)
            print("=" * 120)
            return JsonResponse(ret)
    # 生成一個form對象
    form_obj = forms.RegForm()
    print(form_obj.fields)
    return render(request, "register.html", {"form_obj": form_obj})
    # return render(request, "form_test.html", {"form_obj": form_obj})


# 校驗用戶是否已被註冊
def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    print(username)
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        ret["status"] = 1
        ret["msg"] = "用戶名已被註冊！"
    return JsonResponse(ret)


# 個人博客主頁
def home(request, username, *args):
    logger.debug("home視圖獲取到用戶名:{}".format(username))
    # 去UserInfo表裡把用戶對象取出來
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        logger.warning("又有人訪問不存在的頁面了...")
        return HttpResponse("404")
    # 如果用戶存在，需要將他寫的所有文章找出来
    blog = user.blog
    if not args:
        logger.debug("沒有args參數，默認走的是用戶的個人博客頁面！")
        # 我的文章列表
        article_list = models.Article.objects.filter(user=user)
    else:
        logger.debug(args)
        logger.debug("------------------------------")
        # 表示按照文章的分類或tag或日期歸檔來查詢
        # args = ("category", "技術")
        # article_list = models.Article.objects.filter(user=user).filter(category__title="技術")
        if args[0] == "category":
            article_list = models.Article.objects.filter(user=user).filter(category__title=args[1])
        elif args[0] == "tag":
            article_list = models.Article.objects.filter(user=user).filter(tags__title=args[1])
        else:
            # 按照日期歸檔
            try:
                year, month = args[1].split("-")
                logger.debug("分割得到參數year:{}, month:{}".format(year, month))
                # logger_s10.info("得到年和月的參數啦！！！！")
                logger.debug("************************")
                article_list = models.Article.objects.filter(user=user).filter(
                    create_time__year=year, create_time__month=month
                )
            except Exception as e:
                logger.warning("請求訪問的日期歸檔格式不正確！！！")
                logger.warning((str(e)))
                return HttpResponse("404")
    return render(request, "home.html", {
        "username": username,
        "blog": blog,
        "article_list": article_list,
    })


# def get_left_menu(username):
#     user = models.UserInfo.objects.filter(username=username).first()
#     blog = user.blog
#     category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
#     tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
#     # 按日期歸檔
#     archive_list = models.Article.objects.filter(user=user).extra(
#         select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
#     ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")
#
#     return category_list, tag_list, archive_list


def article_detail(request, username, pk):
    """
    :param username: 被訪問的blog的用户名
    :param pk: 訪問的文章的主鍵id值
    :return:
    """
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    # 找到當前的文章
    article_obj = models.Article.objects.filter(pk=pk).first()
    # 所有評論列表
    comment_list = models.Comment.objects.filter(article_id=pk)

    # 建立觀看記錄
    try:
        models.ViewArticle.objects.create(user=user, article=article_obj)
    except:
        pass
    else:
        # 觀看次數加一
        article_obj.view_count += 1
        article_obj.save()

    return render(
        request,
        "article_detail.html",
        {
            "username": username,
            "article": article_obj,
            "blog": blog,
            "comment_list":comment_list
         }
    )


def up_down(request):
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))
    user = request.user
    response={"state": True}
    try:
        models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)
        if is_up:
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)
    except Exception as e:
        response["state"] = False
        response["first_action"] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up
    return JsonResponse(response)


def comment(request):
    pid = request.POST.get("pid")
    fid = request.POST.get("fid")
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    user_pk = request.user.pk
    response = {}
    # if not pid:  # 根評論
    #     comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content)
    # else:
    comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content, parent_comment_id=pid, friend_comment_id=fid)
    models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)
    response["create_time"] = comment_obj.create_time.strftime("%H:%M:%S")
    response["content"] = comment_obj.content
    response["username"] = comment_obj.user.username
    response["avatar"] = comment_obj.user.avatar.name
    response["pid"] = comment_obj.parent_comment_id
    response["fid"] = comment_obj.friend_comment_id
    return JsonResponse(response)


def comment_tree(request, article_id):
    username = request.user.username
    comment_list = list(models.Comment.objects.filter(article_id=article_id).extra(
        select={"c": "date_format(blog_comment.create_time,'%%Y-%%m-%%d %%H:%%i:%%s')"}
    ).values("pk", "content", "parent_comment_id", "friend_comment_id", "user__avatar","user__username","c", "parent_comment__user__username", "friend_comment__user__username"))

    ret = {"username": username, "comment_list": comment_list}
    return JsonResponse(ret)


def add_article(request):
    if request.method == "POST":
        title = request.POST.get('title')
        category = request.POST.get('category')
        tag_list = request.POST.getlist('all_selected')
        # print(tag_list)
        article_content = request.POST.get('article_content')
        user = request.user
        blog = user.blog
        bs = BeautifulSoup(article_content, "html.parser")
        desc = bs.text[0:150]+"..."
        # 過濾非法標籤，防xss攻擊
        for tag in bs.find_all():
            if tag.name in ["script", "link"]:
                tag.decompose()
        ret = {"status": 0, "msg": ""}
        # try:
        try:
            category_obj = models.Category.objects.create(title=category, blog=blog)
            article_obj = models.Article.objects.create(user=user, title=title, desc=desc, category=category_obj)
        except:
            category_obj = models.Category.objects.filter(title=category, blog=blog).first()
            article_obj = models.Article.objects.create(user=user, title=title, desc=desc, category=category_obj)
        models.ArticleDetail.objects.create(content=str(bs), article=article_obj)
        for tag in tag_list:
            tag = tag.strip()
            if tag:
                if '，' in tag:
                    tag_mini_list = tag.split('，')
                    for mini_tag in tag_mini_list:
                        if mini_tag:
                            try:
                                tag_obj = models.Tag.objects.create(title=mini_tag, blog=blog)
                                models.Article2Tag.objects.create(article=article_obj, tag=tag_obj)
                            except Exception as e:
                                tag_obj = models.Tag.objects.filter(title=mini_tag, blog=blog).first()
                                models.Article2Tag.objects.create(article=article_obj, tag=tag_obj)

                else:
                    try:
                        tag_obj = models.Tag.objects.create(title=tag, blog=blog)
                        models.Article2Tag.objects.create(article=article_obj, tag=tag_obj)
                    except Exception as e:
                        tag_obj = models.Tag.objects.filter(title=tag, blog=blog).first()
                        models.Article2Tag.objects.create(article=article_obj, tag=tag_obj)

        # except Exception as e:
        #     ret["status"] = 1
        #     ret["msg"] = "添加失敗！"
        #     return JsonResponse(ret)
        ret["msg"] = "/blog/"+request.user.blog.site
        return JsonResponse(ret)
    blog = request.user.blog
    category_list = blog.category_set.all()
    tag_list = blog.tag_set.all()
    return render(request, "add_article.html", {'category_list': category_list, 'tag_list':tag_list})


def upload(request):
    obj = request.FILES.get("upload_img")
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", obj.name)
    with open(path, "wb") as f:
        for line in obj:
            f.write(line)
    res = {
        "error": 0,
        "url": "/media/add_article_img/"+obj.name # KingEditor自動幫你在content加入<img ...
    }
    return HttpResponse(json.dumps(res))


def style(request):
    if request.method == 'POST':
        ret = {"status":0, "msg":""}
        header = request.POST.get("header-color")
        content = request.POST.get("content-color")
        title = request.POST.get("title-color")
        file = request.user.username+".css"
        path = os.path.join(settings.STATICFILES_DIRS[0], "theme", file)
        with open(path, "w") as f:
            f.write(".header {background-color: " + header + ";}"+
                    "body {background-color: " + content + ";}"+
                    "p.article-title {font-color: " + title + ";}"
                    )
        blog = request.user.blog
        blog.theme = file
        blog.save()
        ret["hint"] = "設定成功！"
        ret["msg"] = "/index/"
        return JsonResponse(ret)
    color_demo = {"header":'#5bc0de',"content":'#ffffff',"title":'#337ab7'}
    theme = request.user.blog.theme
    if theme:
        path = os.path.join(settings.STATICFILES_DIRS[0], "theme", theme)
        with open(path,'r')as f:
            text = f.read()

        rule = re.compile(r"\.header \{background-color: (?P<header>.+?);\}body \{background-color: (?P<content>.+?);\}p\.article-title \{font-color: (?P<title>.+?);\}")
        result = rule.search(text)
        color_demo['header'] = result.group('header')
        color_demo['content'] = result.group('content')
        color_demo['title'] = result.group('title')
    return render(request, "style.html", color_demo)





