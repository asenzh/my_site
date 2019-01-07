# -*- coding: utf-8 -*-

import random
from django.db.models import F, Q
from django.contrib.syndication.views import Feed  # 订阅RSS
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from utils.paginate import paginate
from utils.response import render_json
from utils.mine_qiniu import upload_data
from .models import Article, Classification, Messages, OwnerMessage, Tag, Links, CarouselImg
from .constants import BlogStatus
from .backends import get_tags_and_musics


@csrf_exempt
@require_POST
def upload_file(request):
    filestream = request.FILES.get('file')
    key, img_path = upload_data(filestream, 'blog')
    return render_json({"error": False, "key": key, "url": img_path, "path": img_path})


def home(request):
    """
    博客首页
    """
    is_home = True
    articles = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by("-publish_time")
    page_num = request.GET.get("page") or 1
    page_size = request.GET.get("page_size") or 5
    articles, total = paginate(articles, page_num=page_num, page_size=page_size)

    new_post = Article.objects.order_by('-count')[:10]  # 最近发布的十篇文章
    # links = Links.objects.order_by("-weights", "id")  # 友情链接
    classification = Classification.class_list.get_classify_list()  # 分类,以及对应的数目
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()  # 按月归档,以及对应的文章数目
    carouse_imgs = CarouselImg.objects.order_by("-weights", "id")  # 轮播图

    return render(request, 'blog/index.html', locals())


def detail(request, year, month, day, id):
    """
    博客详情
    """
    try:
        article = Article.objects.get(id=id)
        Article.objects.filter(id=id).update(count=F('count') + 1)
    except Article.DoesNotExist:
        raise Http404

    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    # links = Links.objects.order_by("-weights", "id")
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()

    return render(request, 'blog/content.html', locals())


def archive_month(request, year, month):
    is_arch_month = True

    articles = Article.objects.filter(publish_time__year=year, publish_time__month=month, status=BlogStatus.PUBLISHED)  # 当前日期下的文章列表
    page_num = request.GET.get("page") or 1
    page_size = request.GET.get("page_size") or 5
    articles, total = paginate(articles, page_num=page_num, page_size=page_size)

    # links = Links.objects.order_by("-weights", "id")
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()

    return render(request, 'blog/index.html', locals())


def classfiDetail(request, classfi):
    is_classfi = True
    temp = Classification.objects.get(name=classfi)  # 获取全部的Article对象

    articles = temp.article_set.filter(status=BlogStatus.PUBLISHED)
    page_num = request.GET.get("page") or 1
    page_size = request.GET.get("page_size") or 5
    articles, total = paginate(articles, page_num=page_num, page_size=page_size)

    # links = Links.objects.order_by("-weights", "id")
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()

    return render(request, 'blog/index.html', locals())


def tagDetail(request, tag):
    is_tag = True
    temp = Tag.objects.get(name=tag)  # 获取全部的Article对象
    # articles = Article.objects.filter(tags=tag)
    articles = temp.article_set.filter(status=BlogStatus.PUBLISHED)
    page_num = request.GET.get("page") or 1
    page_size = request.GET.get("page_size") or 5
    articles, total = paginate(articles, page_num=page_num, page_size=page_size)

    # links = Links.objects.order_by("-weights", "id")
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()

    return render(request, 'blog/index.html', locals())


def about(request):
    """
    关于我
    """
    links = Links.objects.all().order_by("-weights", "id")
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()

    return render(request, 'blog/about.html', locals())


def archive(request):
    """
    文章归档
    """
    # links = Links.objects.order_by("-weights", "id")  # 友情链接
    archive = Article.date_list.get_article_by_archive()
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()

    return render(request, 'blog/archive.html', locals())


class RSSFeed(Feed):
    title = "RSS feed - Daniel的小站"
    link = "feeds/posts/"
    description = "RSS feed - blog posts"

    @classmethod
    def items(cls):
        return Article.objects.order_by('-publish_time')

    def item_title(self, item):
        return item.title

    @classmethod
    def item_pubdate(cls, item):
        return item.publish_time

    @classmethod
    def item_description(cls, item):
        return item.content


def blog_search(request):  # 实现对文章标题的搜索
    is_search = True
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    # links = Links.objects.order_by("-weights", "id")
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()
    error = False

    query = Q()
    s = request.GET.get('s') or ""
    if s:
        query &= Q(title__icontains=s)

    articles = Article.objects.filter(query)
    page_num = request.GET.get("page") or 1
    page_size = request.GET.get("page_size") or 5
    articles, total = paginate(articles, page_num=page_num, page_size=page_size)
    if total == 0:
        error = True

    return render(request, 'blog/index.html', locals())


def message(request):
    """
    主人寄语
    """
    own_messages = OwnerMessage.objects.all()
    own_message = random.sample(own_messages, 1)[0]  # 随机返回一个主人寄语
    date_list = Article.date_list.get_article_by_date()
    classification = Classification.class_list.get_classify_list()
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    # links = Links.objects.order_by("-weights", "id")
    return render(request, 'blog/message.html', locals())


def love(request):
    name = request.POST.get('name')
    pw = request.POST.get('pw')
    if name == 'maomao' and pw == 'nn':
        return render(request, 'blog/love.html')
    else:
        return render(request, 'blog/404.htm')


@csrf_exempt
@require_POST
def create_messages(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    messages = request.POST.get('messages')
    Messages.create_message(
        name=name,
        email=email,
        content=messages
    )
    return render_json({'success': True, 'message': '留言成功！'})


@require_GET
def my_resume(request):
    return render(request, 'resume/my_resume.html')


def links(request):
    """
    友情链接
    """
    links = list(Links.objects.all())
    random.shuffle(links)  # 友情链接随机排序
    new_post = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-count')[:10]
    classification = Classification.class_list.get_classify_list()
    tag_list, music_list = get_tags_and_musics()  # 获取所有标签，并随机赋予颜色
    date_list = Article.date_list.get_article_by_date()
    return render(request, 'blog/links.html', locals())
