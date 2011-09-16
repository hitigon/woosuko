#coding=utf-8
'''
Created on 11-9-13

@author: qiaoshun8888
'''
import os
import random
import re
import datetime
import Image
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
import time
import sys
import math

import config
from iv2ex import SYSTEM_VERSION
from iv2ex.models import Counter, Section, Member, Minisite, Node, Page, Topic, Reply, Notification
import settings
from v2ex.babel.da import GetSite, GetKindByName, GetKindByNum
from v2ex.babel.l10n import GetMessages, GetLanguageSelect, GetSupportedLanguages
from v2ex.babel.security import CheckAuth
from v2ex.babel.ua import detect
from django.core.cache import cache as memcache

def BackstageHomeHandler(request):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values = {}
        template_values['l10n'] = l10n
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        template_values['system_version'] = SYSTEM_VERSION
        template_values['member'] = member
        template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8')
        member_total = memcache.get('member_total')
        if member_total is None:
            q3 = Counter.objects.filter(name='member.total')
            if (len(q3) > 0):
                member_total = q3[0].value
            else:
                member_total = 0
            memcache.set('member_total', member_total, 600)
        template_values['member_total'] = member_total
        topic_total = memcache.get('topic_total')
        if topic_total is None:
            q4 = Counter.objects.filter(name='topic.total')
            if (len(q4) > 0):
                topic_total = q4[0].value
            else:
                topic_total = 0
            memcache.set('topic_total', topic_total, 600)
        template_values['topic_total'] = topic_total
        reply_total = memcache.get('reply_total')
        if reply_total is None:
            q5 = Counter.objects.filter(name='reply.total')
            if (len(q5) > 0):
                reply_total = q5[0].value
            else:
                reply_total = 0
            memcache.set('reply_total', reply_total, 600)
        template_values['reply_total'] = reply_total
        if (member):
            if (member.level == 0):
                q = Section.objects.filter().order_by('-nodes')
                template_values['sections'] = q
                q2 = Member.objects.filter().order_by('-created')[:5]
                template_values['latest_members'] = q2
                q3 = Minisite.objects.filter().order_by('-created')
                template_values['minisites'] = q3
                q4 = Node.objects.filter().order_by('-last_modified')[:8]
                template_values['latest_nodes'] = q4
                if browser['ios']:
                    path = os.path.join('mobile', 'backstage_home.html')
                else:
                    path = os.path.join('desktop', 'backstage_home.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageNewMinisiteHandler(request):
    if request.method == 'GET':
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 添加新站点'
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                path = os.path.join('desktop', 'backstage_new_minisite.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 添加新站点'
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                errors = 0
                # Verification: name
                minisite_name_error = 0
                minisite_name_error_messages = ['',
                    u'请输入站点名',
                    u'站点名长度不能超过 32 个字符',
                    u'站点名只能由 a-Z 0-9 及 - 和 _ 组成',
                    u'抱歉这个站点名已经存在了']
                minisite_name = request.POST['name'].strip().lower()
                if (len(minisite_name) == 0):
                    errors = errors + 1
                    minisite_name_error = 1
                else:
                    if (len(minisite_name) > 32):
                        errors = errors + 1
                        minisite_name_error = 2
                    else:
                        if (re.search('^[a-zA-Z0-9\-\_]+$', minisite_name)):
                            q = Minisite.objects.filter(name=minisite_name.lower())
                            if (len(q) > 0):
                                errors = errors + 1
                                minisite_name_error = 4
                        else:
                            errors = errors + 1
                            minisite_name_error = 3
                template_values['minisite_name'] = minisite_name
                template_values['minisite_name_error'] = minisite_name_error
                template_values['minisite_name_error_message'] = minisite_name_error_messages[minisite_name_error]
                # Verification: title
                minisite_title_error = 0
                minisite_title_error_messages = ['',
                    u'请输入站点标题',
                    u'站点标题长度不能超过 32 个字符'
                ]
                minisite_title = request.POST['title'].strip()
                if (len(minisite_title) == 0):
                    errors = errors + 1
                    minisite_title_error = 1
                else:
                    if (len(minisite_title) > 32):
                        errors = errors + 1
                        minisite_title_error = 2
                template_values['minisite_title'] = minisite_title
                template_values['minisite_title_error'] = minisite_title_error
                template_values['minisite_title_error_message'] = minisite_title_error_messages[minisite_title_error]
                # Verification: description
                minisite_description_error = 0
                minisite_description_error_messages = ['',
                    u'请输入站点描述',
                    u'站点描述长度不能超过 2000 个字符'
                ]
                minisite_description = request.POST['description'].strip()
                if (len(minisite_description) == 0):
                    errors = errors + 1
                    minisite_description_error = 1
                else:
                    if (len(minisite_description) > 2000):
                        errors = errors + 1
                        minisite_description_error = 2
                template_values['minisite_description'] = minisite_description
                template_values['minisite_description_error'] = minisite_description_error
                template_values['minisite_description_error_message'] = minisite_description_error_messages[minisite_description_error]
                template_values['errors'] = errors
                if (errors == 0):
                    minisite = Minisite()
                    q = Counter.objects.filter(name='minisite.max')
                    if (len(q) == 1):
                        counter = q[0]
                        counter.value = counter.value + 1
                    else:
                        counter = Counter()
                        counter.name = 'minisite.max'
                        counter.value = 1
                    minisite.num = counter.value
                    minisite.name = minisite_name
                    minisite.title = minisite_title
                    minisite.description = minisite_description
                    minisite.save()
                    counter.save()
                    return HttpResponseRedirect('/backstage')
                else:
                    path = os.path.join('desktop', 'backstage_new_minisite.html')
                    return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageMinisiteHandler(request, minisite_name):
    if request.method == 'GET':
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › Minisite'
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                minisite = GetKindByName('Minisite', minisite_name)
                if minisite is not False:
                    template_values['minisite'] = minisite
                    template_values['page_title'] = site.title + u' › ' + minisite.title
                    q = Page.objects.filter(minisite=minisite).order_by('weight')
                    template_values['pages'] = q
                    path = os.path.join('desktop', 'backstage_minisite.html')
                    return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/backstage')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageNewPageHandler(request, minisite_name):
    if request.method == 'GET':
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                minisite = GetKindByName('Minisite', minisite_name)
                if minisite is not False:
                    template_values['minisite'] = minisite
                    template_values['page_title'] = site.title + u' › ' + minisite.title + u' › 添加新页面'
                    template_values['page_content_type'] = 'text/html;charset=utf-8'
                    template_values['page_weight'] = 0
                    template_values['page_mode'] = 0
                    path = os.path.join('desktop', 'backstage_new_page.html')
                    return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/backstage')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                minisite = GetKindByName('Minisite', minisite_name)
                if minisite is False:
                    return HttpResponseRedirect('/backstage')
                else:
                    template_values['minisite'] = minisite
                    template_values['page_title'] = site.title + u' › ' + minisite.title + u' › 添加新页面'
                    errors = 0
                    # Verification: name
                    page_name_error = 0
                    page_name_error_messages = ['',
                        u'请输入页面名',
                        u'页面名长度不能超过 64 个字符',
                        u'页面名只能由 a-Z 0-9 及 . - _ 组成',
                        u'抱歉这个页面名已经存在了']
                    page_name = request.POST['name'].strip().lower()
                    if (len(page_name) == 0):
                        errors = errors + 1
                        page_name_error = 1
                    else:
                        if (len(page_name) > 64):
                            errors = errors + 1
                            page_name_error = 2
                        else:
                            if (re.search('^[a-zA-Z0-9\-\_\.]+$', page_name)):
                                q = Page.objects.filter(name=page_name.lower())
                                if (len(q) > 0):
                                    if q[0].minisite.name == minisite.name:
                                        errors = errors + 1
                                        page_name_error = 4
                            else:
                                errors = errors + 1
                                page_name_error = 3
                    template_values['page_name'] = page_name
                    template_values['page_name_error'] = page_name_error
                    template_values['page_name_error_message'] = page_name_error_messages[page_name_error]
                    # Verification: title
                    page_t_error = 0
                    page_t_error_messages = ['',
                        u'请输入页面标题',
                        u'页面标题长度不能超过 100 个字符'
                    ]
                    page_t = request.POST['t'].strip()
                    if (len(page_t) == 0):
                        errors = errors + 1
                        page_t_error = 1
                    else:
                        if (len(page_t) > 100):
                            errors = errors + 1
                            page_t_error = 2
                    template_values['page_t'] = page_t
                    template_values['page_t_error'] = page_t_error
                    template_values['page_t_error_message'] = page_t_error_messages[page_t_error]
                    # Verification: content
                    page_content_error = 0
                    page_content_error_messages = ['',
                        u'请输入页面内容',
                        u'页面内容长度不能超过 200000 个字符'
                    ]
                    page_content = request.POST['content'].strip()
                    if (len(page_content) == 0):
                        errors = errors + 1
                        page_content_error = 1
                    else:
                        if (len(page_content) > 200000):
                            errors = errors + 1
                            page_content_error = 2
                    template_values['page_content'] = page_content
                    template_values['page_content_error'] = page_content_error
                    template_values['page_content_error_message'] = page_content_error_messages[page_content_error]
                    # Verification: mode
                    page_mode = 0
                    page_mode = request.POST['mode'].strip()
                    if page_mode == '1':
                        page_mode = 1
                    else:
                        page_mode = 0
                    # Verification: content_type
                    page_content_type = request.POST['content_type'].strip()
                    if (len(page_content_type) == 0):
                        page_content_type = 'text/html;charset=utf-8'
                    else:
                        if (len(page_content_type) > 40):
                            page_content_type = 'text/html;charset=utf-8'
                    template_values['page_content_type'] = page_content_type
                    # Verification: weight
                    page_weight = request.POST['weight'].strip()
                    if (len(page_content_type) == 0):
                        page_content_type = 0
                    else:
                        if (len(page_weight) > 9):
                            page_weight = 0
                        else:
                            try:
                                page_weight = int(page_weight)
                            except:
                                page_weight = 0
                    template_values['page_weight'] = page_weight
                    template_values['errors'] = errors
                    if (errors == 0):
                        page = Page()
                        page.minisite = minisite
                        q = Counter.objects.filter(name='page.max')
                        if (len(q) == 1):
                            counter = q[0]
                            counter.value = counter.value + 1
                        else:
                            counter = Counter()
                            counter.name = 'page.max'
                            counter.value = 1
                        q2 = Counter.objects.filter(name='page.total')
                        if (len(q2) == 1):
                            counter2 = q[0]
                            counter2.value = counter.value + 1
                        else:
                            counter2 = Counter()
                            counter2.name = 'page.total'
                            counter2.value = 1
                        page.num = counter.value
                        page.name = page_name
                        page.title = page_t
                        page.content = page_content
                        if page_mode == 1:
                            from django.template import Context, Template
                            t = Template(page_content)
                            c = Context({"site" : site, "minisite" : page.minisite, "page" : page})
                            output = t.render(c)
                            page.content_rendered = output
                        else:
                            page.content_rendered = page_content
                        page.content_type = page_content_type
                        page.weight = page_weight
                        page.mode = page_mode
                        page.minisite = minisite
                        page.save()
                        counter.save()
                        counter2.save()
                        minisite.pages = minisite.pages + 1
                        minisite.save()
                        memcache.delete('Minisite_' + str(minisite.num))
                        memcache.delete('Minisite::' + str(minisite.name))
                        return HttpResponseRedirect('/backstage-minisite/' + minisite.name)
                    else:
                        path = os.path.join('desktop', 'backstage_new_page.html')
                        return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageRemoveMinisiteHandler(request, minisite_key):
    if request.method == 'GET':
        member = CheckAuth(request)
        if member:
            if member.level == 0:
                minisite = db.get(db.Key(minisite_key))
                if minisite:
                    # Delete all contents
                    pages = db.GqlQuery("SELECT * FROM Page WHERE minisite = :1", minisite)
                    for page in pages:
                        memcache.delete('Page_' + str(page.num))
                        memcache.delete('Page::' + str(page.name))
                        memcache.delete(minisite.name + '/' + page.name)
                        page.delete()
                    minisite.pages = 0
                    minisite.put()
                    # Delete the minisite
                    memcache.delete('Minisite_' + str(minisite.num))
                    memcache.delete('Minisite::' + str(minisite.name))
                    minisite.delete()
                    self.redirect('/backstage')
                else:
                    self.redirect('/backstage')
            else:
                self.redirect('/')
        else:
            self.redirect('/signin')

def BackstagePageHandler(request, page_key):
    if request.method == 'GET':
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                page = Page.objects.get(id=int(page_key))
                #page = db.get(db.Key(page_key))
                if page:
                    minisite = page.minisite
                    template_values['page'] = page
                    template_values['minisite'] = minisite
                    template_values['page_title'] = site.title + u' › ' + minisite.title + u' › ' + page.title + u' › 编辑'
                    template_values['page_name'] = page.name
                    template_values['page_t'] = page.title
                    template_values['page_content'] = page.content
                    template_values['page_content_type'] = page.content_type
                    template_values['page_mode'] = page.mode
                    template_values['page_weight'] = page.weight
                    path = os.path.join('desktop', 'backstage_page.html')
                    return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/backstage')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                page = Page.objects.get(id=int(page_key))
                #page = db.get(db.Key(page_key))
                if page:
                    minisite = page.minisite
                    template_values['page'] = page
                    template_values['minisite'] = minisite
                    template_values['page_title'] = site.title + u' › ' + minisite.title + u' › 添加新页面'
                    errors = 0
                    # Verification: name
                    page_name_error = 0
                    page_name_error_messages = ['',
                        u'请输入页面名',
                        u'页面名长度不能超过 64 个字符',
                        u'页面名只能由 a-Z 0-9 及 . - _ 组成',
                        u'抱歉这个页面名已经存在了']
                    page_name = request.POST['name'].strip().lower()
                    if (len(page_name) == 0):
                        errors = errors + 1
                        page_name_error = 1
                    else:
                        if (len(page_name) > 64):
                            errors = errors + 1
                            page_name_error = 2
                        else:
                            if (re.search('^[a-zA-Z0-9\-\_\.]+$', page_name)):
                                q = Page.objects.filter(name=page_name.lower(), minisite=page.minisite)
                                if (len(q) > 0):
                                    if q[0].num != page.num:
                                        errors = errors + 1
                                        page_name_error = 4
                            else:
                                errors = errors + 1
                                page_name_error = 3
                    template_values['page_name'] = page_name
                    template_values['page_name_error'] = page_name_error
                    template_values['page_name_error_message'] = page_name_error_messages[page_name_error]
                    # Verification: title
                    page_t_error = 0
                    page_t_error_messages = ['',
                        u'请输入页面标题',
                        u'页面标题长度不能超过 100 个字符'
                    ]
                    page_t = request.POST['t'].strip()
                    if (len(page_t) == 0):
                        errors = errors + 1
                        page_t_error = 1
                    else:
                        if (len(page_t) > 100):
                            errors = errors + 1
                            page_t_error = 2
                    template_values['page_t'] = page_t
                    template_values['page_t_error'] = page_t_error
                    template_values['page_t_error_message'] = page_t_error_messages[page_t_error]
                    # Verification: content
                    page_content_error = 0
                    page_content_error_messages = ['',
                        u'请输入页面内容',
                        u'页面内容长度不能超过 200000 个字符'
                    ]
                    page_content = request.POST['content'].strip()
                    if (len(page_content) == 0):
                        errors = errors + 1
                        page_content_error = 1
                    else:
                        if (len(page_content) > 200000):
                            errors = errors + 1
                            page_content_error = 2
                    template_values['page_content'] = page_content
                    template_values['page_content_error'] = page_content_error
                    template_values['page_content_error_message'] = page_content_error_messages[page_content_error]
                    # Verification: mode
                    page_mode = 0
                    page_mode = request.POST['mode'].strip()
                    if page_mode == '1':
                        page_mode = 1
                    else:
                        page_mode = 0
                    # Verification: content_type
                    page_content_type = request.POST['content_type'].strip()
                    if (len(page_content_type) == 0):
                        page_content_type = 'text/html;charset=utf-8'
                    else:
                        if (len(page_content_type) > 40):
                            page_content_type = 'text/html;charset=utf-8'
                    template_values['page_content_type'] = page_content_type
                    # Verification: weight
                    page_weight = request.POST['weight'].strip()
                    if (len(page_content_type) == 0):
                        page_content_type = 0
                    else:
                        if (len(page_weight) > 9):
                            page_weight = 0
                        else:
                            try:
                                page_weight = int(page_weight)
                            except:
                                page_weight = 0
                    template_values['page_weight'] = page_weight
                    template_values['errors'] = errors
                    if (errors == 0):
                        page.name = page_name
                        page.title = page_t
                        page.content = page_content
                        if page.mode == 1:
                            from django.template import Context, Template
                            t = Template(page_content)
                            c = Context({"site" : site, "minisite" : page.minisite, "page" : page})
                            output = t.render(c)
                            page.content_rendered = output
                        else:
                            page.content_rendered = page_content
                        page.content_type = page_content_type
                        page.mode = page_mode
                        page.weight = page_weight
                        page.save()
                        memcache.delete('Page_' + str(page.num))
                        memcache.delete('Page::' + str(page.name))
                        memcache.delete(minisite.name + '/' + page.name)
                        return HttpResponseRedirect('/backstage-minisite/' + minisite.name)
                    else:
                        path = os.path.join('desktop', 'backstage_page.html')
                        return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/backstage')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageRemovePageHandler(request):
    def get(self, page_key):
        member = CheckAuth(request)
        if member:
            if member.level == 0:
                page = db.get(db.Key(page_key))
                if page:
                    memcache.delete('Page_' + str(page.num))
                    memcache.delete('Page::' + str(page.name))
                    memcache.delete(page.minisite.name + '/' + page.name)
                    minisite = page.minisite
                    page.delete()
                    minisite.pages = minisite.pages - 1
                    minisite.put()
                    self.redirect('/backstage/minisite/' + minisite.name)
            else:
                self.redirect('/')
        else:
            self.redirect('/signin')

def BackstageNewSectionHandler(request):
    if request.method == 'GET':
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                path = os.path.join('mobile', 'backstage_new_section.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                errors = 0
                # Verification: name
                section_name_error = 0
                section_name_error_messages = ['',
                    u'请输入区域名',
                    u'区域名长度不能超过 32 个字符',
                    u'区域名只能由 a-Z 0-9 及 - 和 _ 组成',
                    u'抱歉这个区域名已经存在了']
                section_name = request.POST['name'].strip().lower()
                if (len(section_name) == 0):
                    errors = errors + 1
                    section_name_error = 1
                else:
                    if (len(section_name) > 32):
                        errors = errors + 1
                        section_name_error = 2
                    else:
                        if (re.search('^[a-zA-Z0-9\-\_]+$', section_name)):
                            q = Section.objects.filter(name=section_name.lower())
                            if (len(q) > 0):
                                errors = errors + 1
                                section_name_error = 4
                        else:
                            errors = errors + 1
                            section_name_error = 3
                template_values['section_name'] = section_name
                template_values['section_name_error'] = section_name_error
                template_values['section_name_error_message'] = section_name_error_messages[section_name_error]
                # Verification: title
                section_title_error = 0
                section_title_error_messages = ['',
                    u'请输入区域标题',
                    u'区域标题长度不能超过 32 个字符'
                ]
                section_title = request.POST['title'].strip()
                if (len(section_title) == 0):
                    errors = errors + 1
                    section_title_error = 1
                else:
                    if (len(section_title) > 32):
                        errors = errors + 1
                        section_title_error = 2
                template_values['section_title'] = section_title
                template_values['section_title_error'] = section_title_error
                template_values['section_title_error_message'] = section_title_error_messages[section_title_error]
                # Verification: title
                section_title_alternative_error = 0
                section_title_alternative_error_messages = ['',
                    u'请输入区域副标题',
                    u'区域标题长度不能超过 32 个字符'
                ]
                section_title_alternative = request.POST['title_alternative'].strip()
                if (len(section_title_alternative) == 0):
                    errors = errors + 1
                    section_title_alternative_error = 1
                else:
                    if (len(section_title_alternative) > 32):
                        errors = errors + 1
                        section_title_alternative_error = 2
                template_values['section_title_alternative'] = section_title_alternative
                template_values['section_title_alternative_error'] = section_title_alternative_error
                template_values['section_title_alternative_error_message'] = section_title_alternative_error_messages[section_title_alternative_error]
                template_values['errors'] = errors
                if (errors == 0):
                    section = Section()
                    q = Counter.objects.filter(name='section.max')
                    if (len(q) == 1):
                        counter = q[0]
                        counter.value = counter.value + 1
                    else:
                        counter = Counter()
                        counter.name = 'section.max'
                        counter.value = 1
                    section.num = counter.value
                    section.name = section_name
                    section.title = section_title
                    section.title_alternative = section_title_alternative
                    section.save()
                    counter.save()
                    return HttpResponseRedirect('/backstage')
                else:
                    path = os.path.join('mobile', 'backstage_new_section.html')
                    return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageSectionHandler(request,section_name):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['rnd'] = random.randrange(1, 100)
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                template_values['member'] = member
                q = Section.objects.filter(name=section_name)
                section = False
                if (len(q) == 1):
                    section = q[0]
                    template_values['section'] = section
                    template_values['page_title'] = site.title + u' › 后台 › ' + section.title
                    template_values['section_name'] = section.name
                    template_values['section_title'] = section.title
                    template_values['section_title_alternative'] = section.title_alternative
                    if section.header:
                        template_values['section_header'] = section.header
                    else:
                        template_values['section_header'] = ''
                    if section.footer:
                        template_values['section_footer'] = section.footer
                    else:
                        template_values['section_footer'] = ''
                else:
                    template_values['section'] = section
                if (section):
                    q = Node.objects.filter(section_num=section.num).order_by('-topics')
                    template_values['nodes'] = q
                    section.nodes = len(q)
                    section.save()
                    template_values['section'] = section
                    q2 = Node.objects.filter(section_num=section.num).order_by('-last_modified')[:10]
                    template_values['recent_modified'] = q2
                else:
                    template_values['nodes'] = False
                if browser['ios']:
                    path = os.path.join('mobile', 'backstage_section.html')
                else:
                    path = os.path.join('desktop', 'backstage_section.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['rnd'] = random.randrange(1, 100)
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['member'] = member
                section = GetKindByName('Section', section_name)
                if section is not False:
                    template_values['section'] = section
                    errors = 0
                    # Verification: name
                    section_name_error = 0
                    section_name_error_messages = ['',
                        u'请输入区域名',
                        u'区域名长度不能超过 32 个字符',
                        u'区域名只能由 a-Z 0-9 及 - 和 _ 组成',
                        u'抱歉这个区域名已经存在了']
                    section_name = request.POST['name'].strip().lower()
                    if (len(section_name) == 0):
                        errors = errors + 1
                        section_name_error = 1
                    else:
                        if (len(section_name) > 32):
                            errors = errors + 1
                            section_name_error = 2
                        else:
                            if (re.search('^[a-zA-Z0-9\-\_]+$', section_name)):
                                q = Section.objects.filter(name=section_name.lower())
                                if (len(q) > 0):
                                    for possible_conflict in q:
                                        if possible_conflict.num != section.num:
                                            errors = errors + 1
                                            section_name_error = 4
                            else:
                                errors = errors + 1
                                section_name_error = 3
                    template_values['section_name'] = section_name
                    template_values['section_name_error'] = section_name_error
                    template_values['section_name_error_message'] = section_name_error_messages[section_name_error]
                    # Verification: title
                    section_title_error = 0
                    section_title_error_messages = ['',
                        u'请输入区域标题',
                        u'区域标题长度不能超过 32 个字符'
                    ]
                    section_title = request.POST['title'].strip()
                    if (len(section_title) == 0):
                        errors = errors + 1
                        section_title_error = 1
                    else:
                        if (len(section_title) > 32):
                            errors = errors + 1
                            section_title_error = 2
                    template_values['section_title'] = section_title
                    template_values['section_title_error'] = section_title_error
                    template_values['section_title_error_message'] = section_title_error_messages[section_title_error]
                    # Verification: title_alternative
                    section_title_alternative_error = 0
                    section_title_alternative_error_messages = ['',
                        u'请输入区域副标题',
                        u'区域标题长度不能超过 32 个字符'
                    ]
                    section_title_alternative = request.POST['title_alternative'].strip()
                    if (len(section_title_alternative) == 0):
                        errors = errors + 1
                        section_title_alternative_error = 1
                    else:
                        if (len(section_title_alternative) > 32):
                            errors = errors + 1
                            section_title_alternative_error = 2
                    template_values['section_title_alternative'] = section_title_alternative
                    template_values['section_title_alternative_error'] = section_title_alternative_error
                    template_values['section_title_alternative_error_message'] = section_title_alternative_error_messages[section_title_alternative_error]
                    # Verification: header
                    section_header_error = 0
                    section_header_error_messages = ['',
                        u'区域头部信息不能超过 1000 个字符'
                    ]
                    section_header = request.POST['header'].strip()
                    if len(section_header) > 1000:
                        errors = errors + 1
                        section_header_error = 1
                    template_values['section_header'] = section_header
                    template_values['section_header_error'] = section_header_error
                    template_values['section_header_error_message'] = section_header_error_messages[section_header_error]
                    # Verification: footer
                    section_footer_error = 0
                    section_footer_error_messages = ['',
                        u'区域尾部信息不能超过 1000 个字符'
                    ]
                    section_footer = request.POST['footer'].strip()
                    if len(section_footer) > 1000:
                        errors = errors + 1
                        section_footer_error = 1
                    template_values['section_footer'] = section_footer
                    template_values['section_footer_error'] = section_footer_error
                    template_values['section_footer_error_message'] = section_footer_error_messages[section_footer_error]
                    template_values['errors'] = errors
                    if (errors == 0):
                        memcache.delete('Section::' + section.name)
                        section.name = section_name
                        section.title = section_title
                        section.title_alternative = section_title_alternative
                        section.header = section_header
                        section.footer = section_footer
                        section.save()
                        memcache.delete('Section_' + str(section.num))
                        memcache.delete('Section::' + section_name)
                        return HttpResponseRedirect('/backstage')
                    else:
                        path = os.path.join('desktop', 'backstage_section.html')
                        return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/backstage')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageNewNodeHandler(request,section_name):
    if request.method == 'GET':
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                template_values['member'] = CheckAuth(request)
                q = Section.objects.filter(name=section_name)
                if (len(q) == 1):
                    template_values['section'] = q[0]
                else:
                    template_values['section'] = False
                path = os.path.join('mobile', 'backstage_new_node.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                template_values['member'] = member
                section = False
                q = Section.objects.filter(name=section_name)
                if (len(q) == 1):
                    section = q[0]
                    template_values['section'] = section
                else:
                    template_values['section'] = False
                errors = 0
                # Verification: name
                node_name_error = 0
                node_name_error_messages = ['',
                    u'请输入节点名',
                    u'节点名长度不能超过 32 个字符',
                    u'节点名只能由 a-Z 0-9 及 - 和 _ 组成',
                    u'抱歉这个节点名已经存在了']
                node_name = request.POST['name'].strip().lower()
                if (len(node_name) == 0):
                    errors = errors + 1
                    node_name_error = 1
                else:
                    if (len(node_name) > 32):
                        errors = errors + 1
                        node_name_error = 2
                    else:
                        if (re.search('^[a-zA-Z0-9\-\_]+$', node_name)):
                            q = Node.objects.filter(name=node_name.lower())
                            if (len(q) > 0):
                                errors = errors + 1
                                node_name_error = 4
                        else:
                            errors = errors + 1
                            node_name_error = 3
                template_values['node_name'] = node_name
                template_values['node_name_error'] = node_name_error
                template_values['node_name_error_message'] = node_name_error_messages[node_name_error]
                # Verification: title
                node_title_error = 0
                node_title_error_messages = ['',
                    u'请输入节点标题',
                    u'节点标题长度不能超过 32 个字符'
                ]
                node_title = request.POST['title'].strip()
                if (len(node_title) == 0):
                    errors = errors + 1
                    node_title_error = 1
                else:
                    if (len(node_title) > 32):
                        errors = errors + 1
                        node_title_error = 2
                template_values['node_title'] = node_title
                template_values['node_title_error'] = node_title_error
                template_values['node_title_error_message'] = node_title_error_messages[node_title_error]
                # Verification: title
                node_title_alternative_error = 0
                node_title_alternative_error_messages = ['',
                    u'请输入节点副标题',
                    u'节点标题长度不能超过 32 个字符'
                ]
                node_title_alternative = request.POST['title_alternative'].strip()
                if (len(node_title_alternative) == 0):
                    errors = errors + 1
                    node_title_alternative_error = 1
                else:
                    if (len(node_title_alternative) > 32):
                        errors = errors + 1
                        node_title_alternative_error = 2
                template_values['node_title_alternative'] = node_title_alternative
                template_values['node_title_alternative_error'] = node_title_alternative_error
                template_values['node_title_alternative_error_message'] = node_title_alternative_error_messages[node_title_alternative_error]
                template_values['errors'] = errors
                if (errors == 0):
                    node = Node()
                    q = Counter.objects.filter(name='node.max')
                    if (len(q) == 1):
                        counter = q[0]
                        counter.value = counter.value + 1
                    else:
                        counter = Counter()
                        counter.name = 'node.max'
                        counter.value = 1
                    node.num = counter.value
                    node.section_num = section.num
                    node.name = node_name
                    node.title = node_title
                    node.title_alternative = node_title_alternative
                    node.save()
                    counter.save()
                    memcache.delete('index_categories')
                    memcache.delete('home_nodes_new')
                    return HttpResponseRedirect('/backstage-node/' + node.name)
                else:
                    path = os.path.join('mobile', 'backstage_new_node.html')
                    return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageNodeHandler(request, node_name):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        session = request.session
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                if 'message' in session:
                    template_values['message'] = session['message']
                    del session['message']
                template_values['member'] = member
                template_values['member'] = member
                q = Node.objects.filter(name=node_name)
                if (len(q) == 1):
                    node = q[0]
                    if node.parent_node_name is None:
                        siblings = []
                    else:
                        siblings = Node.objects.filter(parent_node_name=node.parent_node_name).exclude(name=node.name)
                    template_values['siblings'] = siblings
                    template_values['node'] = node
                    template_values['node_name'] = node.name
                    template_values['node_title'] = node.title
                    template_values['node_title_alternative'] = q[0].title_alternative
                    if q[0].category is None:
                        template_values['node_category'] = ''
                    else:
                        template_values['node_category'] = q[0].category
                    if q[0].parent_node_name is None:
                        template_values['node_parent_node_name'] = ''
                    else:
                        template_values['node_parent_node_name'] = q[0].parent_node_name
                    if q[0].header is None:
                        template_values['node_header'] = ''
                    else:
                        template_values['node_header'] = q[0].header
                    if q[0].footer is None:
                        template_values['node_footer'] = ''
                    else:
                        template_values['node_footer'] = q[0].footer
                    if q[0].sidebar is None:
                        template_values['node_sidebar'] = ''
                    else:
                        template_values['node_sidebar'] = q[0].sidebar
                    if q[0].sidebar_ads is None:
                        template_values['node_sidebar_ads'] = ''
                    else:
                        template_values['node_sidebar_ads'] = q[0].sidebar_ads
                    template_values['node_topics'] = q[0].topics
                else:
                    template_values['node'] = False
                section = GetKindByNum('Section', node.section_num)
                template_values['section'] = section
                if section is not False:
                    template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8') + u' › ' + section.title + u' › ' + node.title
                if browser['ios']:
                    path = os.path.join('mobile', 'backstage_node.html')
                else:
                    path = os.path.join('desktop', 'backstage_node.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                template_values['member'] = member
                node = False
                q = Node.objects.filter(name=node_name)
                if (len(q) == 1):
                    node = q[0]
                    template_values['node'] = q[0]
                    template_values['node_name'] = q[0].name
                    template_values['node_title'] = q[0].title
                    template_values['node_title_alternative'] = q[0].title_alternative
                    if q[0].category is None:
                        template_values['node_category'] = ''
                    else:
                        template_values['node_category'] = q[0].category
                    if q[0].parent_node_name is None:
                        template_values['node_parent_node_name'] = ''
                    else:
                        template_values['node_parent_node_name'] = q[0].parent_node_name
                    if q[0].header is None:
                        template_values['node_header'] = ''
                    else:
                        template_values['node_header'] = q[0].header
                    if q[0].footer is None:
                        template_values['node_footer'] = ''
                    else:
                        template_values['node_footer'] = q[0].footer
                    if q[0].sidebar is None:
                        template_values['node_sidebar'] = ''
                    else:
                        template_values['node_sidebar'] = q[0].sidebar
                    if q[0].sidebar_ads is None:
                        template_values['node_sidebar_ads'] = ''
                    else:
                        template_values['node_sidebar_ads'] = q[0].sidebar_ads
                    template_values['node_topics'] = q[0].topics
                else:
                    template_values['node'] = False
                section = False
                q2 = Section.objects.filter(num=q[0].section_num)
                if (len(q2) == 1):
                    section = q2[0]
                    template_values['section'] = q2[0]
                else:
                    template_values['section'] = False
                if section is not False:
                    template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8') + u' › ' + section.title + u' › ' + node.title
                errors = 0
                # Verification: name
                node_name_error = 0
                node_name_error_messages = ['',
                    u'请输入节点名',
                    u'节点名长度不能超过 32 个字符',
                    u'节点名只能由 a-Z 0-9 及 - 和 _ 组成',
                    u'抱歉这个节点名已经存在了']
                node_name = request.POST['name'].strip().lower()
                if (len(node_name) == 0):
                    errors = errors + 1
                    node_name_error = 1
                else:
                    if (len(node_name) > 32):
                        errors = errors + 1
                        node_name_error = 2
                    else:
                        if (re.search('^[a-zA-Z0-9\-\_]+$', node_name)):
                            q = Node.objects.filter(name=node_name.lower()).exclude(num=node.num)
                            if (len(q) > 0):
                                errors = errors + 1
                                node_name_error = 4
                        else:
                            errors = errors + 1
                            node_name_error = 3
                template_values['node_name'] = node_name
                template_values['node_name_error'] = node_name_error
                template_values['node_name_error_message'] = node_name_error_messages[node_name_error]
                # Verification: title
                node_title_error = 0
                node_title_error_messages = ['',
                    u'请输入节点标题',
                    u'节点标题长度不能超过 32 个字符'
                ]
                node_title = request.POST['title'].strip()
                if (len(node_title) == 0):
                    errors = errors + 1
                    node_title_error = 1
                else:
                    if (len(node_title) > 32):
                        errors = errors + 1
                        node_title_error = 2
                template_values['node_title'] = node_title
                template_values['node_title_error'] = node_title_error
                template_values['node_title_error_message'] = node_title_error_messages[node_title_error]
                # Verification: title_alternative
                node_title_alternative_error = 0
                node_title_alternative_error_messages = ['',
                    u'请输入节点副标题',
                    u'节点标题长度不能超过 32 个字符'
                ]
                node_title_alternative = request.POST['title_alternative'].strip()
                if (len(node_title_alternative) == 0):
                    errors = errors + 1
                    node_title_alternative_error = 1
                else:
                    if (len(node_title_alternative) > 32):
                        errors = errors + 1
                        node_title_alternative_error = 2
                template_values['node_title_alternative'] = node_title_alternative
                template_values['node_title_alternative_error'] = node_title_alternative_error
                template_values['node_title_alternative_error_message'] = node_title_alternative_error_messages[node_title_alternative_error]
                # Verification: node_category
                node_category = request.POST['category'].strip()
                template_values['node_category'] = node_category
                # Verification: node_parent_node_name
                node_parent_node_name = request.POST['parent_node_name'].strip()
                template_values['node_parent_node_name'] = node_parent_node_name
                # Verification: node_header
                node_header = request.POST['header'].strip()
                template_values['node_header'] = node_header
                # Verification: node_footer
                node_footer = request.POST['footer'].strip()
                template_values['node_footer'] = node_footer
                # Verification: node_sidebar
                node_sidebar = request.POST['sidebar'].strip()
                template_values['node_sidebar'] = node_sidebar
                # Verification: node_sidebar_ads
                node_sidebar_ads = request.POST['sidebar_ads'].strip()
                template_values['node_sidebar_ads'] = node_sidebar_ads
                template_values['errors'] = errors
                if (errors == 0):
                    node.name = node_name
                    node.title = node_title
                    node.title_alternative = node_title_alternative
                    node.category = node_category
                    node.parent_node_name = node_parent_node_name
                    node.header = node_header
                    node.footer = node_footer
                    node.sidebar = node_sidebar
                    node.sidebar_ads = node_sidebar_ads
                    node.save()
                    memcache.delete('Node_' + str(node.num))
                    memcache.delete('Node::' + node.name)
                    memcache.delete('index_categories')
                    memcache.delete('home_nodes_new')
                    return HttpResponseRedirect('/backstage-section/' + section.name)
                else:
                    path = os.path.join('mobile', 'backstage_node.html')
                    return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageNodeAvatarHandler(request, node_name):
    if request.method == 'GET':
        return HttpResponseRedirect('/backstage-node/' + node_name)
    else:
        site = GetSite()
        session = request.session
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if (member.level == 0):
                template_values['member'] = member
                node = GetKindByName('Node', node_name)
                if node is None:
                    return HttpResponseRedirect('/backstage')
                dest = '/backstage-node/' + node.name
                timestamp = str(int(time.time()))
                try:
                    image_req = request.FILES['avatar']
                    if image_req is None:
                        return HttpResponseRedirect(dest)
                    ext = str(image_req).split('.');
                    # 图片文件格式，并且文件大小不能超过2MB
                    if len(ext) == 2 and image_req.size<1024*1024*2:
                        ext = ext[1].lower()
                        if ext=="jpg" or ext=="jpeg" or ext=="bmp" or  ext=='png':
                            timestamp = str(int(time.mktime(datetime.datetime.now().timetuple())))
                            datetoday= str(datetime.datetime.today())[0:10].replace('-', '')
                            new_name_src = timestamp + "." + ext
                            new_name_large = timestamp + "_l." + ext
                            new_name_normal = timestamp + "_n." + ext
                            new_name_small = timestamp + "_s." + ext
                            save_path = settings.STATIC_UPLOAD + "/" + member.user.username + "/" + datetoday
                            if not os.path.exists(save_path):
                                os.makedirs(save_path)
                            # Source image
                            image = Image.open(image_req)
                            image.save(save_path + "/" + new_name_src, 'jpeg')
                            # Large 73x73
                            image.thumbnail((73,73),Image.ANTIALIAS)
                            image.save(save_path + "/" + new_name_large, 'jpeg')
                            node.avatar_large_url =settings.STATIC_UPLOAD_WEB + member.user.username + "/" + datetoday + "/" + new_name_large
                            # Normal 48x48
                            image.thumbnail((48,48),Image.ANTIALIAS)
                            image.save(save_path + "/" + new_name_normal, 'jpeg')
                            node.avatar_normal_url = settings.STATIC_UPLOAD_WEB + member.user.username + "/" + datetoday + "/" + new_name_normal
                            # Small 24x24
                            image.thumbnail((24,24),Image.ANTIALIAS)
                            image.save(save_path + "/" + new_name_small, 'jpeg')
                            node.avatar_mini_url = settings.STATIC_UPLOAD_WEB + member.user.username + "/" + datetoday + "/" + new_name_small
                            # Save avatar info
                            node.save()
                        else:
                            return HttpResponseRedirect(dest)
                    else:
                        return HttpResponseRedirect(dest)
                except:
                    print "Unexpected error:", sys.exc_info()
                    return HttpResponseRedirect(dest)
                memcache.set('Node_' + str(node.num), node, 86400 * 365)
                memcache.set('Node::' + node.name, node, 86400 * 365)
                memcache.delete('Avatar::node_' + str(node.num) + '_large')
                memcache.delete('Avatar::node_' + str(node.num) + '_normal')
                memcache.delete('Avatar::node_' + str(node.num) + '_mini')
                session['message'] = '新节点头像设置成功'
                return HttpResponseRedirect(dest)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageRemoveReplyHandler(request, reply_num):
    if request.method == 'GET':
        member = CheckAuth(request)
        if (member):
            if (member.level == 0):
                q = Reply.objects.filter(num=int(reply_num))
                if (len(q) == 1):
                    reply = q[0]
                    topic = reply.topic
                    reply.delete()
                    q = Reply.objects.filter(topic=topic)
                    topic.replies = len(q)
                    if (topic.replies == 0):
                        topic.last_reply_by = None
                    topic.save()
                    pages = 1
                    memcache.delete('Topic_' + str(topic.num))
                    memcache.delete('topic_' + str(topic.num) + '_replies_desc_compressed')
                    memcache.delete('topic_' + str(topic.num) + '_replies_asc_compressed')
                    memcache.delete('topic_' + str(topic.num) + '_replies_filtered_compressed')
                    memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_desktop_' + str(pages))
                    memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_desktop_' + str(pages))
                    memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_desktop_' + str(pages))
                    memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_ios_' + str(pages))
                    memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_ios_' + str(pages))
                    memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_ios_' + str(pages))
                    return HttpResponseRedirect('/t/' + str(topic.num))
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageTidyReplyHandler(request, reply_num):
    if request.method == 'GET':
        member = CheckAuth(request)
        if (member):
            if (member.level == 0):
                q = Reply.objects.filter(num=int(reply_num))
                if (len(q) == 1):
                    reply = q[0]
                    topic_num = reply.topic_num
                    q2 = Member.objects.filter(username_lower=reply.created_by.lower())
                    member = q2[0]
                    reply.member = member
                    reply.member_num = member.num
                    q3 = Topic.objects.filter(num=topic_num)
                    topic = q3[0]
                    # Begin to do real stuff
                    reply2 = Reply()
                    reply2.topic = topic
                    reply2.num = reply.num
                    reply2.content = reply.content
                    reply2.topic = topic
                    reply2.topic_num = topic.num
                    reply2.member = reply.member
                    reply2.member_num = reply.member_num
                    reply2.created_by = reply.created_by
                    reply2.source = reply.source
                    reply2.created = reply.created
                    reply2.last_modified = reply.last_modified
                    reply2.save()
                    reply.delete()
                    return HttpResponseRedirect('/t/' + str(topic_num))
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageTidyTopicHandler(request, topic_num):
    if request.method == 'GET':
        member = CheckAuth(request)
        if (member):
            if (member.level == 0):
                q = Topic.objects.filter(num=int(topic_num))
                if (len(q) == 1):
                    topic = q[0]
                    q2 = Member.objects.filter(num=topic.member_num)
                    member = q2[0]
                    topic.member = member
                    q3 = Node.objects.filter(num=topic.node_num)
                    node = q3[0]
                    topic.node = node
                    topic.save()
                    memcache.delete('Topic_' + str(topic.num))
                    return HttpResponseRedirect('/t/' + str(topic.num))
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageDeactivateUserHandler(request):
    def get(self, key):
        member = CheckAuth(request)
        if member:
            if member.level == 0:
                one = db.get(db.Key(key))
                if one:
                    if one.num != 1:
                        memcache.delete(one.auth)
                        one.deactivated = int(time.time())
                        one.password = hashlib.sha1(str(time.time())).hexdigest()
                        one.auth = hashlib.sha1(str(one.num) + ':' + one.password).hexdigest()
                        one.newbie = 1
                        one.noob = 1
                        one.put()
                        memcache.delete('Member_' + str(one.num))
                        return self.redirect('/member/' + one.username)
        return self.redirect('/')

def BackstageMoveTopicHandler(request, topic_id):
    if request.method == 'GET':
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        topic = Topic.objects.get(id=topic_id)
        can_move = False
        ttl = 0
        if member:
            if member.level == 0:
                can_move = True
            if topic:
                if topic.member_num == member.num:
                    now = datetime.datetime.now()
                    ttl = 300 - int((now - topic.created).seconds)
                    if ttl > 0:
                        can_move = True
                        template_values['ttl'] = ttl
        template_values['can_move'] = can_move
        if member:
            template_values['member'] = member
            if can_move:
                template_values['page_title'] = site.title + u' › 移动主题'
                template_values['site'] = site
                if topic is not None:
                    node = topic.node
                    template_values['topic'] = topic
                    template_values['node'] = node
                    template_values['system_version'] = SYSTEM_VERSION
                    themes = os.listdir(settings.STATIC_THEMES)
                    template_values['themes'] = themes
                    path = os.path.join('desktop', 'backstage_move_topic.html')
                    return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

    else:
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        topic = Topic.objects.get(id=int(topic_id))
        can_move = False
        ttl = 0
        if member:
            if member.level == 0:
                can_move = True
            if topic:
                if topic.member_num == member.num:
                    now = datetime.datetime.now()
                    ttl = 300 - int((now - topic.created).seconds)
                    if ttl > 0:
                        can_move = True
                        template_values['ttl'] = ttl
        template_values['can_move'] = can_move
        if member:
            template_values['member'] = member
            if can_move:
                template_values['page_title'] = site.title + u' › 移动主题'
                template_values['site'] = site
                if topic is not None:
                    errors = 0
                    node = topic.node
                    template_values['topic'] = topic
                    template_values['node'] = node
                    template_values['system_version'] = SYSTEM_VERSION
                    destination = request.POST['destination']
                    if destination is not None:
                        node_new = GetKindByName('Node', destination)
                        if node_new is not False:
                            node_new = Node.objects.get(id=node_new.id)
                            node_old = topic.node
                            node_old.topics = node_old.topics - 1
                            node_old.save()
                            node_new.topics = node_new.topics + 1
                            node_new.save()
                            topic.node = node_new
                            topic.node_num = node_new.num
                            topic.node_name = node_new.name
                            topic.node_title = node_new.title
                            topic.save()
                            memcache.delete('Topic_' + str(topic.num))
                            memcache.delete('Node_' + str(node_old.num))
                            memcache.delete('Node_' + str(node_new.num))
                            memcache.delete('Node::' + str(node_old.name))
                            memcache.delete('Node::' + str(node_new.name))
                            return HttpResponseRedirect('/t/' + str(topic.num))
                        else:
                            errors = errors + 1
                    else:
                        errors = errors + 1
                    if errors > 0:
                        themes = os.listdir(settings.STATIC_THEMES)
                        template_values['themes'] = themes
                        path = os.path.join('desktop', 'backstage_move_topic.html')
                        return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageSiteHandler(request):
    if request.method == 'GET':
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › 站点设置'
                template_values['site'] = site
                template_values['site_title'] = site.title
                template_values['site_slogan'] = site.slogan
                template_values['site_domain'] = site.domain
                template_values['site_description'] = site.description
                if site.home_categories is not None:
                    template_values['site_home_categories'] = site.home_categories
                else:
                    template_values['site_home_categories'] = ''
                if site.analytics is not None:
                    template_values['site_analytics'] = site.analytics
                else:
                    template_values['site_analytics'] = ''
                if site.topic_view_level is not None:
                    template_values['site_topic_view_level'] = site.topic_view_level
                else:
                    template_values['site_topic_view_level'] = -1
                if site.topic_create_level is not None:
                    template_values['site_topic_create_level'] = site.topic_create_level
                else:
                    template_values['site_topic_create_level'] = 1000
                if site.topic_reply_level is not None:
                    template_values['site_topic_reply_level'] = site.topic_reply_level
                else:
                    template_values['site_topic_reply_level'] = 1000
                if site.meta is not None:
                    template_values['site_meta'] = site.meta
                else:
                    template_values['site_meta'] = ''
                if site.home_top is not None:
                    template_values['site_home_top'] = site.home_top
                else:
                    template_values['site_home_top'] = ''
                if site.theme is not None:
                    template_values['site_theme'] = site.theme
                else:
                    template_values['site_theme'] = 'default'
                s = GetLanguageSelect(site.l10n)
                template_values['s'] = s
                template_values['member'] = member
                template_values['system_version'] = SYSTEM_VERSION
                themes = os.listdir(settings.STATIC_THEMES)
                template_values['themes'] = themes
                path = os.path.join('desktop', 'backstage_site.html')
                return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/')

    else:
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › 站点设置'
                template_values['site'] = site
                template_values['member'] = member
                template_values['system_version'] = SYSTEM_VERSION
                errors = 0
                # Verification: title (required)
                site_title_error = 0
                site_title_error_messages = ['',
                    u'请输入站点名',
                    u'站点名长度不能超过 40 个字符'
                ]
                site_title = request.POST['title'].strip()
                if (len(site_title) == 0):
                    errors = errors + 1
                    site_title_error = 1
                else:
                    if (len(site_title) > 40):
                        errors = errors + 1
                        site_title_error = 1
                template_values['site_title'] = site_title
                template_values['site_title_error'] = site_title_error
                template_values['site_title_error_message'] = site_title_error_messages[site_title_error]
                # Verification: slogan (required)
                site_slogan_error = 0
                site_slogan_error_messages = ['',
                    u'请输入站点标语',
                    u'站点标语长度不能超过 140 个字符'
                ]
                site_slogan = request.POST['slogan'].strip()
                if (len(site_slogan) == 0):
                    errors = errors + 1
                    site_slogan_error = 1
                else:
                    if (len(site_slogan) > 140):
                        errors = errors + 1
                        site_slogan_error = 1
                template_values['site_slogan'] = site_slogan
                template_values['site_slogan_error'] = site_slogan_error
                template_values['site_slogan_error_message'] = site_slogan_error_messages[site_slogan_error]
                # Verification: domain (required)
                site_domain_error = 0
                site_domain_error_messages = ['',
                    u'请输入主要域名',
                    u'主要域名长度不能超过 40 个字符'
                ]
                site_domain = request.POST['domain'].strip()
                if (len(site_domain) == 0):
                    errors = errors + 1
                    site_domain_error = 1
                else:
                    if (len(site_domain) > 40):
                        errors = errors + 1
                        site_domain_error = 1
                template_values['site_domain'] = site_domain
                template_values['site_domain_error'] = site_domain_error
                template_values['site_domain_error_message'] = site_domain_error_messages[site_domain_error]
                # Verification: description (required)
                site_description_error = 0
                site_description_error_messages = ['',
                    u'请输入站点简介',
                    u'站点简介长度不能超过 200 个字符'
                ]
                site_description = request.POST['description'].strip()
                if (len(site_description) == 0):
                    errors = errors + 1
                    site_description_error = 1
                else:
                    if (len(site_description) > 200):
                        errors = errors + 1
                        site_description_error = 1
                template_values['site_description'] = site_description
                template_values['site_description_error'] = site_description_error
                template_values['site_description_error_message'] = site_description_error_messages[site_description_error]
                # Verification: analytics (optional)
                site_analytics_error = 0
                site_analytics_error_messages = ['',
                    u'Analytics ID 格式不正确'
                ]
                site_analytics = request.POST['analytics'].strip()
                if len(site_analytics) > 0:
                    if re.findall('^UA\-[0-9]+\-[0-9]+$', site_analytics):
                        site_analytics_error = 0
                    else:
                        errors = errors + 1
                        site_analytics_error = 1
                else:
                    site_analytics = ''
                template_values['site_analytics'] = site_analytics
                template_values['site_analytics_error'] = site_analytics_error
                template_values['site_analytics_error_message'] = site_analytics_error_messages[site_analytics_error]
                # Verification: l10n (required)
                site_l10n = request.POST['l10n'].strip()
                supported = GetSupportedLanguages()
                if site_l10n == '':
                    site_l10n = site.l10n
                else:
                    if site_l10n not in supported:
                        site_l10n = site.l10n
                s = GetLanguageSelect(site_l10n)
                template_values['s'] = s
                template_values['site_l10n'] = site_l10n
                # Verification: home_categories (optional)
                site_home_categories_error = 0
                site_home_categories_error_messages = ['',
                    u'首页分类信息不要超过 2000 个字符'
                ]
                site_home_categories = request.POST['home_categories'].strip()
                site_home_categories_length = len(site_home_categories)
                if len(site_home_categories) > 0:
                    if site_home_categories_length > 2000:
                        errors = errors + 1
                        site_home_categories_error = 1
                else:
                    site_home_categories = ''
                template_values['site_home_categories'] = site_home_categories
                template_values['site_home_categories_error'] = site_home_categories_error
                template_values['site_home_categories_error_message'] = site_home_categories_error_messages[site_home_categories_error]
                # Verification: topic_view_level (default=-1)
                site_topic_view_level = request.POST['topic_view_level']
                try:
                    site_topic_view_level = int(site_topic_view_level)
                    if site_topic_view_level < -1:
                        site_topic_view_level = -1
                except:
                    site_topic_view_level = -1
                template_values['site_topic_view_level'] = site_topic_view_level
                # Verification: topic_create_level (default=1000)
                site_topic_create_level = request.POST['topic_create_level']
                try:
                    site_topic_create_level = int(site_topic_create_level)
                    if site_topic_create_level < -1:
                        site_topic_create_level = 1000
                except:
                    site_topic_create_level = 1000
                template_values['site_topic_create_level'] = site_topic_create_level
                # Verification: topic_reply_level (default=1000)
                site_topic_reply_level = request.POST['topic_reply_level']
                try:
                    site_topic_reply_level = int(site_topic_reply_level)
                    if site_topic_reply_level < -1:
                        site_topic_reply_level = 1000
                except:
                    site_topic_reply_level = 1000
                template_values['site_topic_reply_level'] = site_topic_reply_level
                # Verification: meta
                site_meta = request.POST['meta']
                template_values['site_meta'] = site_meta
                # Verification: home_top
                site_home_top = request.POST['home_top']
                template_values['site_home_top'] = site_home_top
                # Verification: theme
                site_theme = request.POST['theme']
                themes = os.listdir(settings.STATIC_THEMES)
                template_values['themes'] = themes
                if site_theme in themes:
                    template_values['site_theme'] = site_theme
                else:
                    site_theme = 'default'
                    template_values['site_theme'] = site_theme

                template_values['errors'] = errors

                if errors == 0:
                    site.title = site_title
                    site.slogan = site_slogan
                    site.domain = site_domain
                    site.description = site_description
                    if site_home_categories != '':
                        site.home_categories = site_home_categories
                    if site_analytics != '':
                        site.analytics = site_analytics
                    site.l10n = site_l10n
                    site.topic_view_level = site_topic_view_level
                    site.topic_create_level = site_topic_create_level
                    site.topic_reply_level = site_topic_reply_level
                    site.meta = site_meta
                    site.home_top = site_home_top
                    site.theme = site_theme
                    site.save()
                    memcache.delete('index_categories')
                    template_values['message'] = l10n.site_settings_updated;
                    template_values['site'] = site
                    memcache.delete('site')
                path = os.path.join('desktop', 'backstage_site.html')
                return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/')

def BackstageTopicHandler(request):
    if request.method == 'GET':
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8') + u' › ' + l10n.topic_settings.decode('utf-8')
                template_values['site'] = site
                template_values['site_use_topic_types'] = site.use_topic_types
                if site.topic_types is None:
                    template_values['site_topic_types'] = ''
                else:
                    template_values['site_topic_types'] = site.topic_types
                if site.use_topic_types is not True:
                    s = '<select name="use_topic_types"><option value="1">Enabled</option><option value="0" selected="selected">Disabled</option></select>'
                else:
                    s = '<select name="use_topic_types"><option value="1" selected="selected">Enabled</option><option value="0">Disabled</option></select>'
                template_values['s'] = s
                template_values['member'] = member
                template_values['system_version'] = SYSTEM_VERSION
                path = os.path.join('desktop', 'backstage_topic.html')
                return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/')

    else:
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8') + u' › ' + l10n.topic_settings.decode('utf-8')
                template_values['site'] = site
                template_values['site_use_topic_types'] = site.use_topic_types
                if site.topic_types is None:
                    template_values['site_topic_types'] = ''
                else:
                    template_values['site_topic_types'] = site.topic_types
                if site.use_topic_types is not True:
                    s = '<select name="use_topic_types"><option value="1">Enabled</option><option value="0" selected="selected">Disabled</option></select>'
                else:
                    s = '<select name="use_topic_types"><option value="1" selected="selected">Enabled</option><option value="0">Disabled</option></select>'
                template_values['s'] = s
                template_values['member'] = member
                template_values['system_version'] = SYSTEM_VERSION
                errors = 0
                # Verification: use_topic_types
                site_use_topic_types = request.POST['use_topic_types'].strip()
                if site_use_topic_types is None:
                    s = '<select name="use_topic_types"><option value="1">Enabled</option><option value="0" selected="selected">Disabled</option></select>'
                else:
                    if site_use_topic_types == '1':
                        s = '<select name="use_topic_types"><option value="1" selected="selected">Enabled</option><option value="0">Disabled</option></select>'
                    else:
                        s = '<select name="use_topic_types"><option value="1">Enabled</option><option value="0" selected="selected">Disabled</option></select>'
                template_values['s'] = s
                # Verification: topic_types
                site_topic_types = request.POST['topic_types'].strip()
                if errors == 0:
                    if site_use_topic_types == '1':
                        site.use_topic_types = True
                    else:
                        site.use_topic_types = False
                    site.topic_types = site_topic_types
                    site.save()
                    memcache.delete('site')
                    return HttpResponseRedirect('/backstage')
                else:
                    path = os.path.join('desktop', 'backstage_topic.html')
                    return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/')


def BackstageRemoveMemcacheHandler(request):
    def post(self):
        member = CheckAuth(request)
        if member:
            if member.level == 0:
                mc = self.request.get('mc')
                if mc is not None:
                    memcache.delete(mc)
        self.redirect('/backstage')


def BackstageMemberHandler(request, member_username):
    if request.method == 'GET':
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                member_username_lower = member_username.lower()
                q = Member.objects.filter(username_lower=member_username_lower)
                if (len(q) == 1):
                    one = q[0]
                    template_values['one'] = one
                    errors = 0
                    template_values['one_username'] = one.user.username
                    template_values['one_email'] = one.user.email
                    if one.avatar_large_url is None:
                        template_values['one_avatar_large_url'] = ''
                    else:
                        template_values['one_avatar_large_url'] = one.avatar_large_url
                    if one.avatar_normal_url is None:
                        template_values['one_avatar_normal_url'] = ''
                    else:
                        template_values['one_avatar_normal_url'] = one.avatar_normal_url
                    if one.avatar_mini_url is None:
                        template_values['one_avatar_mini_url'] = ''
                    else:
                        template_values['one_avatar_mini_url'] = one.avatar_mini_url
                    if one.bio is None:
                        template_values['one_bio'] = ''
                    else:
                        template_values['one_bio'] = one.bio
                    template_values['one_level'] = one.level
                    template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8') + u' › ' + one.user.username
                    template_values['site'] = site
                    template_values['member'] = member
                    template_values['system_version'] = SYSTEM_VERSION
                    template_values['latest_members'] = Member.objects.filter().order_by('-created')[:5]
                    path = os.path.join('desktop', 'backstage_member.html')
                    return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/backstage')

        else:
            return HttpResponseRedirect('/')


    else:
        template_values = {}
        site = GetSite()
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                member_username_lower = member_username.lower()
                q = Member.objects.filter(username_lower=member_username_lower)
                if (len(q)== 1):
                    one = q[0]
                    template_values['one'] = one
                    errors = 0
                    # Verification: username
                    one_username_error = 0
                    one_username_error_messages = ['',
                        l10n.username_empty,
                        l10n.username_too_long,
                        l10n.username_too_short,
                        l10n.username_invalid,
                        l10n.username_taken]
                    one_username = request.POST['username'].strip()
                    if (len(one_username) == 0):
                        errors = errors + 1
                        one_username_error = 1
                    else:
                        if (len(one_username) > 32):
                            errors = errors + 1
                            one_username_error = 2
                        else:
                            if (len(one_username) < 3):
                                errors = errors + 1
                                one_username_error = 3
                            else:
                                if (re.search('^[a-zA-Z0-9\_]+$', one_username)):
                                    q = Member.objects.filter(username_lower=one_username.lower()).exclude(num=one.num)
                                    if (len(q) > 0):
                                        errors = errors + 1
                                        one_username_error = 5
                                else:
                                    errors = errors + 1
                                    one_username_error = 4
                    template_values['one_username'] = one_username
                    template_values['one_username_error'] = one_username_error
                    template_values['one_username_error_message'] = one_username_error_messages[one_username_error]
                    # Verification: email
                    one_email_error = 0
                    one_email_error_messages = ['',
                        u'请输入电子邮件地址',
                        u'电子邮件地址长度不能超过 32 个字符',
                        u'输入的电子邮件地址不符合规则',
                        u'这个电子邮件地址已经有人注册过了']
                    one_email = request.POST['email'].strip()
                    if (len(one_email) == 0):
                        errors = errors + 1
                        one_email_error = 1
                    else:
                        if (len(one_email) > 32):
                            errors = errors + 1
                            one_email_error = 2
                        else:
                            p = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
                            if (p.search(one_email)):
                                q = Member.objects.filter(user__email__exact=one_email.lower()).exclude(num=one.num)
                                if (len(q) > 0):
                                    errors = errors + 1
                                    one_email_error = 4
                            else:
                                errors = errors + 1
                                one_email_error = 3
                    template_values['one_email'] = one_email.lower()
                    template_values['one_email_error'] = one_email_error
                    template_values['one_email_error_message'] = one_email_error_messages[one_email_error]
                    # Verification: avatar
                    one_avatar_large_url = request.POST['avatar_large_url']
                    template_values['one_avatar_large_url'] = one_avatar_large_url
                    one_avatar_normal_url = request.POST['avatar_normal_url']
                    template_values['one_avatar_normal_url'] = one_avatar_normal_url
                    one_avatar_mini_url = request.POST['avatar_mini_url']
                    template_values['one_avatar_mini_url'] = one_avatar_mini_url
                    # Verification: bio
                    one_bio = request.POST['bio']
                    template_values['one_bio'] = one_bio
                    # Verification: level
                    one_level = request.POST['level']
                    try:
                        one_level = int(one_level)
                    except:
                        if one.num == 1:
                            one_level = 0
                        else:
                            one_level = 1000
                    template_values['one_level'] = one_level
                    if errors == 0:
                        user = one.user
                        user.username = one_username
                        user.email = one_email
                        one.username_lower = one_username.lower()
                        one.avatar_large_url = one_avatar_large_url
                        one.avatar_normal_url = one_avatar_normal_url
                        one.avatar_mini_url = one_avatar_mini_url
                        one.bio = one_bio
                        one.level = one_level
                        user.save()
                        one.save()
                        memcache.delete('Member_' + str(one.num))
                        memcache.delete('Member::' + one_username.lower())
                        return HttpResponseRedirect('/backstage')
                    else:
                        template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8') + u' › ' + one.username
                        template_values['site'] = site
                        template_values['member'] = member
                        template_values['system_version'] = SYSTEM_VERSION
                        template_values['latest_members'] = Member.objects.filter().order_by('-created')[:5]
                        path = os.path.join('desktop', 'backstage_member.html')
                        return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/backstage')

        else:
            return HttpResponseRedirect('/')

def BackstageMembersHandler(request):
    if request.method == 'GET':
        template_values = {}
        site = GetSite()
        template_values['site'] = site
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['member'] = member
                template_values['page_title'] = site.title + u' › ' + l10n.backstage.decode('utf-8') + u' › 浏览所有会员'
                member_total = memcache.get('member_total')
                if member_total is None:
                    q3 = Counter.objects.filter(name='member.total')
                    if (len(q3) > 0):
                        member_total = q3[0].value
                    else:
                        member_total = 0
                    memcache.set('member_total', member_total, 600)
                template_values['member_total'] = member_total
                page_size = 60
                pages = 1
                if member_total > page_size:
                    if (member_total % page_size) > 0:
                        pages = int(math.floor(member_total / page_size)) + 1
                    else:
                        pages = int(math.floor(member_total / page_size))
                try:
                    page_current = int(request.GET['p'])
                    if page_current < 1:
                        page_current = 1
                    if page_current > pages:
                        page_current = pages
                except:
                    page_current = 1
                page_start = (page_current - 1) * page_size
                template_values['pages'] = pages
                template_values['page_current'] = page_current
                i = 1
                ps = []
                while i <= pages:
                    ps.append(i)
                    i = i + 1
                template_values['ps'] = ps
                q = Member.objects.filter().order_by('-created')[int(page_start):int(page_start)+int(page_size)]
                template_values['members'] = q
                path = os.path.join('desktop', 'backstage_members.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def BackstageRemoveNotificationHandler(request, notification_id):
    if request.method == 'GET':
        o = Notification.objects.get(id=int(notification_id))
        member = CheckAuth(request)
        if o and member:
            if type(o).__name__ == 'Notification':
                if o.for_member_num == member.num:
                    o.delete()
        return HttpResponseRedirect('/notifications')

#def main():
#    application = webapp.WSGIApplication([
#    ('/backstage', BackstageHomeHandler),
#    ('/backstage/new/minisite', BackstageNewMinisiteHandler),
#    ('/backstage/minisite/(.*)', BackstageMinisiteHandler),
#    ('/backstage/remove/minisite/(.*)', BackstageRemoveMinisiteHandler),
#    ('/backstage/new/page/(.*)', BackstageNewPageHandler),
#    ('/backstage/page/(.*)', BackstagePageHandler),
#    ('/backstage/remove/page/(.*)', BackstageRemovePageHandler),
#    ('/backstage/new/section', BackstageNewSectionHandler),
#    ('/backstage/section/(.*)', BackstageSectionHandler),
#    ('/backstage/new/node/(.*)', BackstageNewNodeHandler),
#    ('/backstage/node/([a-z0-9A-Z]+)', BackstageNodeHandler),
#    ('/backstage/node/([a-z0-9A-Z]+)/avatar', BackstageNodeAvatarHandler),
#    ('/backstage/remove/reply/(.*)', BackstageRemoveReplyHandler),
#    ('/backstage/tidy/reply/([0-9]+)', BackstageTidyReplyHandler),
#    ('/backstage/tidy/topic/([0-9]+)', BackstageTidyTopicHandler),
#    ('/backstage/deactivate/user/(.*)', BackstageDeactivateUserHandler),
#    ('/backstage/move/topic/(.*)', BackstageMoveTopicHandler),
#    ('/backstage/site', BackstageSiteHandler),
#    ('/backstage/topic', BackstageTopicHandler),
#    ('/backstage/remove/mc', BackstageRemoveMemcacheHandler),
#    ('/backstage/member/(.*)', BackstageMemberHandler),
#    ('/backstage/members', BackstageMembersHandler),
#    ('/backstage/remove/notification/(.*)', BackstageRemoveNotificationHandler),
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()