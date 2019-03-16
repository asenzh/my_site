# -*- coding: utf-8 -*-

import urllib
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from utils.errorcode import ERRORCODE
from utils.dlibs.http.response import http_response
from utils.dlibs.tools.paginator import paginate
from utils.common import form_error
from article.models import Article, Links, Classification, CarouselImg, Music, Author, OwnerMessage
from .forms import SearchBlogForm, AddFriendLinkForm, AddAuthorForm


def login_view(request):
    """
    用户登录
    :param request:
    :return:
    """
    back_url = request.parameters.get('back_url')
    if not back_url:
        back_url = reverse('blog_list')
    user_info = request.session.get('user_info')
    if user_info:
        return HttpResponseRedirect(back_url)

    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        user = authenticate(username=user_name, password=password)
        if not user:
            messages.warning(request, u'登录失败，请检查用户名密码后重试.')
            return HttpResponseRedirect('%s?%s' % (reverse('login_view'), urllib.urlencode({'back_url': back_url})))
        login(request, user)
        request.session['is_login'] = True
        request.session['user_id'] = user.id
        request.session['user_name'] = user.username
        return HttpResponseRedirect(reverse('blog_list'))
    else:
        # 没有登录跳到登录页面进行登录
        return render(request, 'manager/login.html', {'back_url': back_url})


@login_required
def logout_view(request):
    """
    用户登出
    :param request:
    :return:
    """
    logout(request)
    del request.session['is_login']
    del request.session['user_id']
    del request.session['user_name']
    return HttpResponseRedirect('/manager')


@login_required
def blog_list_view(request):
    """
    博客列表
    :param request:
    :return:
    """
    form = SearchBlogForm(request.GET)
    form.is_valid()
    query = Q()
    title = form.cleaned_data.get("title")
    if title:
        query &= (Q(title__icontains=title) | Q(classification__name=title) | Q(tags__name=title))

    blogs = Article.objects.select_related().filter(query).order_by("-id")
    blog_list, total = paginate(
        blogs,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/blog_list.html', {
        "active_classes": ['.blog', '.blog_list'],
        "params": request.GET,
        "form": form,
        "data_list": blog_list,
        "total": total,
    })


def blog_create_view(request):
    return render(request, 'manager/operate_blog.html', {
        "active_classes": ['.blog', '.blog_list'],
        "params": request.GET,
    })


@login_required
def friend_link_list_view(request):
    """
    友情链接列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    links = Links.objects.filter(query).order_by("-id")
    link_list, total = paginate(
        links,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/link_list.html', {
        "active_classes": ['.blog', '.link_list'],
        "params": request.GET,
        "data_list": link_list,
        "total": total,
        "name": name
    })


@login_required
def add_friend_link_view(request):
    form = AddFriendLinkForm(request.POST)
    if not form.is_valid():
        messages.warning(request, "</br>".join(form_error(form)))
        return HttpResponseRedirect(reverse('friend_link_list'))

    try:
        Links.objects.create(
            name=form.cleaned_data.get('name'),
            link=form.cleaned_data.get('link'),
            avatar=form.cleaned_data.get('avatar'),
            desc=form.cleaned_data.get('desc'),
        )
        messages.success(request, u'添加成功')
        return HttpResponseRedirect(reverse('friend_link_list'))
    except Exception as e:
        messages.error(request, u'添加失败: %s' % e)
        return HttpResponseRedirect(reverse('friend_link_list'))


@login_required
def del_friend_link_view(request):
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg=u'参数错误')

    try:
        Links.objects.filter(id__in=item_ids).delete()
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg=u'删除失败: %s' % e)


@login_required
def author_list_view(request):
    """
    作者列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    authors = Author.objects.filter(query).order_by("-id")
    author_list, total = paginate(
        authors,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/author_list.html', {
        "active_classes": ['.blog', '.author_list'],
        "params": request.GET,
        "data_list": author_list,
        "total": total,
        "name": name
    })


@login_required
def add_author_view(request):
    form = AddAuthorForm(request.POST)
    if not form.is_valid():
        messages.warning(request, "</br>".join(form_error(form)))
        return HttpResponseRedirect(reverse('author_list'))

    try:
        Author.objects.create(
            name=form.cleaned_data.get('name'),
            email=form.cleaned_data.get('email'),
            website=form.cleaned_data.get('website'),
        )
        messages.success(request, u'添加成功')
        return HttpResponseRedirect(reverse('author_list'))
    except Exception as e:
        messages.error(request, u'添加失败: %s' % e)
        return HttpResponseRedirect(reverse('author_list'))


@login_required
def del_author_view(request):
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg=u'参数错误')

    try:
        Author.objects.filter(id__in=item_ids).delete()
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg=u'删除失败: %s' % e)
