#coding=utf-8
'''
Created on 11-9-13

@intro: Based on Project Babel(V2EX) made by @Livid
@author: qiaoshun8888

'''
import logging
import os
import datetime
import pickle
import random
import re
import Image
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import get_template, Context
from django.core.cache import cache as memcache
import math
from django.utils import simplejson
import time

from iv2ex import SYSTEM_VERSION
from iv2ex.models import Node, Section, Topic, Counter, Reply, Notification, Page
import settings
from twitter_api.oauth import OAuthToken
from twitter_api.oauthtwitter import OAuthApi
from v2ex.babel.da import GetSite, GetKindByName, GetKindByNum, GetPacked, GetUnpacked
from v2ex.babel.l10n import GetMessages
from v2ex.babel.security import CheckAuth
from v2ex.babel.ua import detect

from iv2ex.itaskqueue import ITaskQueueManage

import config

from config import twitter_consumer_key as CONSUMER_KEY
from config import twitter_consumer_secret as CONSUMER_SECRET

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  

TOPIC_PAGE_SIZE = 100

def NewTopicHandler(request, node_name):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        template_values['page_title'] = site.title + u' › ' + l10n.create_new_topic.decode('utf-8')
        can_create = False
        if site.topic_create_level > 999:
            if member:
                can_create = True
        else:
            if member:
                if member.level <= site.topic_create_level:
                    can_create = True
        if (member):
            template_values['member'] = member
            node = GetKindByName('Node', node_name)
            if node is False:
                path = os.path.join('desktop', 'node_not_found.html')
                return render_to_response(path, template_values)
            template_values['node'] = node
            section = GetKindByNum('Section', node.section_num)
            template_values['section'] = section
            if site.use_topic_types:
                types = site.topic_types.split("\n")
                options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                i = 0
                for a_type in types:
                    i = i + 1
                    detail = a_type.split(':')
                    options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                tt = '<div def="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                template_values['tt'] = tt
            else:
                template_values['tt'] = ''
            if can_create:
                if browser['ios']:
                    if node:
                        path = os.path.join('mobile', 'new_topic.html')
                    else:
                        path = os.path.join('mobile', 'node_not_found.html')
                else:
                    if node:
                        path = os.path.join('desktop', 'new_topic.html')
                    else:
                        path = os.path.join('desktop', 'node_not_found.html')
            else:
                path = os.path.join('desktop', 'access_denied.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        '''
        ### BEGIN: CAN CONTINUE
        can_continue = True
        if ('HTTP_HOST' in request.META):
            if (request.META['HTTP_HOST'] not in ['www.v2ex.com', 'v2ex.appspot.com', 'fast.v2ex.com', 'beta.v2ex.com', 'localhost:10000']):
                can_continue = False
        else:
            can_continue = False
        if ('HTTP_USER_AGENT' not in request.META):
            can_continue = False
        if ('HTTP_COOKIE' not in request.META):
            can_continue = False
        if ('HTTP_REFERER' in request.META):
            has_v2ex = False
            if ('http://localhost:10000' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://www.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://v2ex.appspot.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('https://www.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('https://v2ex.appspot.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://fast.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://beta.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://' + str(site.domain) in request.META['HTTP_REFERER']):
                has_v2ex = True
            if has_v2ex is False:
                can_continue = False
        else:
            can_continue = False
        if ('CONTENT_TYPE' in request.META):
            if request.META['CONTENT_TYPE'] != 'application/x-www-form-urlencoded':
                can_continue = False
        else:
            can_continue = False
        if can_continue is False:
            return HttpResponseRedirect('http://' + site.domain + '/')
        ### END: CAN CONTINUE
        '''
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        template_values['page_title'] = site.title + u' › ' + l10n.create_new_topic.decode('utf-8')
        can_create = False
        if site.topic_create_level > 999:
            if member:
                can_create = True
        else:
            if member:
                if member.level <= site.topic_create_level:
                    can_create = True
        if (member):
            template_values['member'] = member
            if can_create:
                q = Node.objects.filter(name=node_name)
                node = False
                if (len(q) == 1):
                    node = q[0]
                template_values['node'] = node
                section = False
                if node:
                    q2 = Section.objects.filter(num=node.section_num)
                    if (len(q2) == 1):
                        section = q2[0]
                template_values['section'] = section
                errors = 0
                # Verification: title
                topic_title_error = 0
                topic_title_error_messages = ['',
                    u'请输入主题标题',
                    u'主题标题长度不能超过 120 个字符'
                    ]
                topic_title = request.POST['title'].strip()
                if (len(topic_title) == 0):
                    errors = errors + 1
                    topic_title_error = 1
                else:
                    if (len(topic_title) > 120):
                        errors = errors + 1
                        topic_title_error = 2
                template_values['topic_title'] = topic_title
                template_values['topic_title_error'] = topic_title_error
                template_values['topic_title_error_message'] = topic_title_error_messages[topic_title_error]
                # Verification: content
                topic_content_error = 0
                topic_content_error_messages = ['',
                    u'主题内容长度不能超过 200000 个字符'
                ]
                topic_content = request.POST['content'].strip()
                topic_content_length = len(topic_content)
                if (topic_content_length > 0):
                    if (topic_content_length > 200000):
                        errors = errors + 1
                        topic_content_error = 1
                template_values['topic_content'] = topic_content
                template_values['topic_content_error'] = topic_content_error
                template_values['topic_content_error_message'] = topic_content_error_messages[topic_content_error]
                # Verification: type
                if site.use_topic_types:
                    types = site.topic_types.split("\n")
                    if len(types) > 0:
                        topic_type = request.POST['type'].strip()
                        try:
                            topic_type = int(topic_type)
                            if topic_type < 0:
                                topic_type = 0
                            if topic_type > len(types):
                                topic_type = 0
                            if topic_type > 0:
                                detail = types[topic_type - 1].split(':')
                                topic_type_label = detail[0]
                                topic_type_color = detail[1]
                        except:
                            topic_type = 0
                    else:
                        topic_type = 0
                    options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                    i = 0
                    for a_type in types:
                        i = i + 1
                        detail = a_type.split(':')
                        if topic_type == i:
                            options = options + '<option value="' + str(i) + '" selected="selected">' + detail[0] + '</option>'
                        else:
                            options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                    tt = '<div def="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                    template_values['tt'] = tt
                else:
                    template_values['tt'] = ''
                template_values['errors'] = errors
                if (errors == 0):
                    topic = Topic()
                    topic.node = node
                    q = Counter.objects.filter(name='topic.max')
                    if (len(q) == 1):
                        counter = q[0]
                        counter.value = counter.value + 1
                    else:
                        counter = Counter()
                        counter.name = 'topic.max'
                        counter.value = 1
                    q2 = Counter.objects.filter(name='topic.total')
                    if (len(q2) == 1):
                        counter2 = q2[0]
                        counter2.value = counter2.value + 1
                    else:
                        counter2 = Counter()
                        counter2.name = 'topic.total'
                        counter2.value = 1
                    topic.num = counter.value
                    topic.title = topic_title
                    topic.content = topic_content
                    if len(topic_content) > 0:
                        topic.has_content = True
                        topic.content_length = topic_content_length
                    else:
                        topic.has_content = False
                    path = os.path.join('portion', 'topic_content.html')
                    output = get_template(path).render(Context({'topic' : topic}))
                    topic.content_rendered = output.decode('utf-8')
                    topic.node = node
                    topic.node_num = node.num
                    topic.node_name = node.name
                    topic.node_title = node.title
                    topic.created_by = member.user.username
                    topic.member = member
                    topic.member_num = member.num
                    topic.last_touched = datetime.datetime.now()
                    ua = request.META['HTTP_USER_AGENT']
                    if (re.findall('Mozilla\/5.0 \(iPhone;', ua)):
                        topic.source = 'iPhone'
                    if (re.findall('Mozilla\/5.0 \(iPod;', ua)):
                        topic.source = 'iPod'
                    if (re.findall('Mozilla\/5.0 \(iPad;', ua)):
                        topic.source = 'iPad'
                    if (re.findall('Android', ua)):
                        topic.source = 'Android'
                    if (re.findall('Mozilla\/5.0 \(PLAYSTATION 3;', ua)):
                        topic.source = 'PS3'
                    if site.use_topic_types:
                        if topic_type > 0:
                            topic.type = topic_type_label
                            topic.type_color = topic_type_color
                    node.topics = node.topics + 1
                    node.save()
                    topic.save()
                    counter.save()
                    counter2.save()
                    memcache.delete('feed_index')
                    memcache.delete('Node_' + str(topic.node_num))
                    memcache.delete('Node::' + str(node.name))
                    memcache.delete('q_latest_16')
                    memcache.delete('home_rendered')
                    memcache.delete('home_rendered_mobile')
                    ITQM = ITaskQueueManage()
                    #ITQM.add(data='/index/topic/' + str(topic.num))
                    #taskqueue.add(url='/index/topic/' + str(topic.num))
                    # Twitter Sync
                    if member.twitter_oauth == 1 and member.twitter_sync == 1:
                        access_token = OAuthToken.from_string(member.twitter_oauth_string)
                        twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                        status = topic.title + ' #' + topic.node.name + ' http://' + request.META['HTTP_HOST'] + '/t/' + str(topic.num)
                        try:
                            twitter.PostUpdate(status.encode('utf-8'))
                        except:
                            logging.error("Failed to sync to Twitter for Topic #" + str(topic.num))
                    # Change newbie status?
                    if member.newbie == 1:
                        now = datetime.datetime.now()
                        created = member.created
                        diff = now - created
                        if diff.seconds > (86400 * 60):
                            member.newbie = 0
                            member.save()

                    # Notifications: mention_topic
                    ITQM.add(data='/notifications/topic/' + str(topic.id))
                    #taskqueue.add(url='/notifications/topic/' + str(topic.key()))

                    return HttpResponseRedirect('/t/' + str(topic.num) + '#reply0')
                else:
                    if browser['ios']:
                        path = os.path.join('mobile', 'new_topic.html')
                    else:
                        path = os.path.join('desktop', 'new_topic.html')
                    return render_to_response(path, template_values)
            else:
                path = os.path.join('desktop', 'access_denied.html')
                return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')

def TopicHandler(request, topic_num):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)

        if 'r' in request.GET:
            reply_reversed = request.GET['r']
            if reply_reversed == '1':
                reply_reversed = True
            else:
                reply_reversed = False
        else:
            reply_reversed = False

        if 'f' in request.GET:
            filter_mode = request.GET['f']
            if filter_mode == '1':
                filter_mode = True
            else:
                filter_mode = False
        else:
            filter_mode = False

        template_values['reply_reversed'] = reply_reversed
        template_values['filter_mode'] = filter_mode
        template_values['system_version'] = SYSTEM_VERSION
        errors = 0
        template_values['errors'] = errors
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member is not False:
            try:
                blocked = pickle.loads(member.blocked.encode('utf-8'))
            except:
                blocked = []
            if (len(blocked) > 0):
                template_values['blocked'] = ','.join(map(str, blocked))
            if member.level == 0:
                template_values['is_admin'] = 1
            else:
                template_values['is_admin'] = 0
        topic_num_str = str(topic_num)
        if len(topic_num_str) > 8:
            if browser['ios']:
                path = os.path.join('mobile', 'topic_not_found.html')
            else:
                path = os.path.join('desktop', 'topic_not_found.html')
            return render_to_response(path, template_values)
        topic = False
        topic = memcache.get('Topic_' + str(topic_num))
        if topic is None:
            q = Topic.objects.filter(num=int(topic_num))
            if (len(q) == 1):
                topic = q[0]
                memcache.set('Topic_' + str(topic_num), topic, 86400)
        can_edit = False
        can_move = False
        if topic:
            if member:
                if member.level == 0:
                    can_edit = True
                    can_move = True
                if topic.member_num == member.num:
                    now = datetime.datetime.now()
                    if (now - topic.created).seconds < 300:
                        can_edit = True
                        can_move = True
            #ITQM.add(data='/hit/topic/' + str(topic.key()))
            TopicHitHandler(topic.id)
            #taskqueue.add(url='/hit/topic/' + str(topic.key()))
            template_values['page_title'] = site.title + u' › ' + topic.title
            template_values['canonical'] = 'http://' + site.domain + '/t/' + str(topic.num)
            if topic.content_rendered is None:
                path = os.path.join('portion', 'topic_content.html')
                output = get_template(path).render(Context({'topic' : topic}))
                topic = Topic.objects.get(id=topic.id)
                topic.content_rendered = output.decode('utf-8')
                memcache.delete('Topic_' + str(topic.num))
                topic.save()
        else:
            template_values['page_title'] = site.title + u' › 主题未找到'
        template_values['topic'] = topic
        template_values['can_edit'] = can_edit
        template_values['can_move'] = can_move
        if (topic):
            node = False
            section = False
            node = GetKindByNum('Node', topic.node_num)
            if (node):
                section = GetKindByNum('Section', node.section_num)
            template_values['node'] = node
            template_values['section'] = section

            page_size = TOPIC_PAGE_SIZE
            pages = 1
            if topic.replies > page_size:
                if (topic.replies % page_size) > 0:
                    pages = int(math.floor(topic.replies / page_size)) + 1
                else:
                    pages = int(math.floor(topic.replies / page_size))
            try:
                page_current = int(request.GET['p'])
                if page_current < 1:
                    page_current = 1
                if page_current > pages:
                    page_current = pages
            except:
                page_current = pages
            page_start = (page_current - 1) * page_size
            template_values['pages'] = pages
            template_values['page_current'] = page_current

            template_values['ps'] = False
            i = 1
            ps = []
            while i <= pages:
                ps.append(i)
                i = i + 1
            if len(ps) > 1:
                template_values['ps'] = ps
            replies = False
            if browser['ios']:
                path = os.path.join('portion', 'topic_replies_mobile.html')
            else:
                path = os.path.join('portion', 'topic_replies.html')
            if filter_mode:
                if browser['ios']:
                    r_tag = 'topic_' + str(topic.num) + '_replies_filtered_rendered_ios_' + str(page_current)
                else:
                    r_tag = 'topic_' + str(topic.num) + '_replies_filtered_rendered_desktop_' + str(page_current)
                r = memcache.get(r_tag)
                if r is None:
                    replies = memcache.get('topic_' + str(topic.num) + '_replies_filtered_compressed_' + str(page_current))
                    if replies is None:
                        q5 = Reply.objects.filter(topic_num=int(topic_num),member_num=topic.member.num).order_by('created')[int(page_start):int(page_start)+int(page_size)]
                        replies = q5
                        memcache.set('topic_' + str(topic.num) + '_replies_filtered_compressed_' + str(page_current), GetPacked(replies), 7200)
                    else:
                        replies = GetUnpacked(replies)
                    template_values['replies'] = replies
                    template_values['replies_count'] = replies.count()
                    r = get_template(path).render(Context(template_values))
                    memcache.set(r_tag, r, 86400)
            else:
                if reply_reversed:
                    if browser['ios']:
                        r_tag = 'topic_' + str(topic.num) + '_replies_desc_rendered_ios_' + str(page_current)
                    else:
                        r_tag = 'topic_' + str(topic.num) + '_replies_desc_rendered_desktop_' + str(page_current)
                    r = memcache.get(r_tag)
                    if r is None:
                        replies = memcache.get('topic_' + str(topic.num) + '_replies_desc_compressed_' + str(page_current))
                        if replies is None:
                            q4 = Reply.objects.filter(topic_num=int(topic.num)).order_by('-created')[int(page_start):int(page_start)+int(page_size)]
                            replies = q4
                            memcache.set('topic_' + str(topic.num) + '_replies_desc_compressed_' + str(page_current), GetPacked(q4), 86400)
                        else:
                            replies = GetUnpacked(replies)
                        template_values['replies'] = replies
                        template_values['replies_count'] = replies.count()
                        r = get_template(path).render(Context(template_values))
                        memcache.set(r_tag, r, 86400)
                else:
                    if browser['ios']:
                        r_tag = 'topic_' + str(topic.num) + '_replies_asc_rendered_ios_' + str(page_current)
                    else:
                        r_tag = 'topic_' + str(topic.num) + '_replies_asc_rendered_desktop_' + str(page_current)
                    r = memcache.get(r_tag)
                    if r is None:
                        replies = memcache.get('topic_' + str(topic.num) + '_replies_asc_compressed_' + str(page_current))
                        if replies is None:
                            q4 = Reply.objects.filter(topic_num=int(topic.num)).order_by('created')[int(page_start):int(page_start)+int(page_size)]
                            replies = q4
                            memcache.set('topic_' + str(topic.num) + '_replies_asc_compressed_' + str(page_current), GetPacked(q4), 86400)
                        else:
                            replies = GetUnpacked(replies)
                        template_values['replies'] = replies
                        template_values['replies_count'] = replies.count()
                        r = get_template(path).render(Context(template_values))
                        memcache.set(r_tag, r, 86400)
            template_values['r'] = r
            if topic and member:
                if member.hasFavorited(topic):
                    template_values['favorited'] = True
                else:
                    template_values['favorited'] = False
            if browser['ios']:
                path = os.path.join('mobile', 'topic.html')
            else:
                path = os.path.join('desktop', 'topic.html')
        else:
            if browser['ios']:
                path = os.path.join('mobile', 'topic_not_found.html')
            else:
                path = os.path.join('desktop', 'topic_not_found.html')
        return render_to_response(path, template_values)

    else:
        site = GetSite()
        '''
        ### BEGIN: CAN CONTINUE
        can_continue = True
        if ('HTTP_HOST' in request.META):
            if (request.META['HTTP_HOST'] not in ['www.v2ex.com', 'v2ex.appspot.com', 'fast.v2ex.com', 'beta.v2ex.com', 'localhost:10000']):
                can_continue = False
        else:
            can_continue = False
        if ('HTTP_USER_AGENT' not in request.META):
            can_continue = False
        if ('HTTP_COOKIE' not in request.META):
            can_continue = False
        if ('HTTP_REFERER' in request.META):
            has_v2ex = False
            if ('http://localhost:10000' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://www.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://v2ex.appspot.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('https://www.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('https://v2ex.appspot.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://fast.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://beta.v2ex.com' in request.META['HTTP_REFERER']):
                has_v2ex = True
            if ('http://' + str(site.domain) in request.META['HTTP_REFERER']):
                has_v2ex = True
            if has_v2ex is False:
                can_continue = False
        else:
            can_continue = False
        if ('CONTENT_TYPE' in request.META):
            if request.META['CONTENT_TYPE'] != 'application/x-www-form-urlencoded':
                can_continue = False
        else:
            can_continue = False
        if can_continue is False:
            return HttpResponseRedirect('http://' + site.domain + '/')
        ### END: CAN CONTINUE
        '''
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        topic_num_str = str(topic_num)
        if len(topic_num_str) > 8:
            if browser['ios']:
                path = os.path.join('mobile', 'topic_not_found.html')
            else:
                path = os.path.join('desktop', 'topic_not_found.html')
            return render_to_response(path, template_values)
        if (member):
            topic = False
            q = Topic.objects.filter(num=int(topic_num))
            if (len(q) == 1):
                topic = q[0]
                try:
                    topic.hits = topic.hits + 1
                    topic.put()
                except:
                    topic.hits = topic.hits - 1
            template_values['topic'] = topic
            errors = 0
            # Verification: content
            reply_content_error = 0
            reply_content_error_messages = ['',
                u'请输入回复内容',
                u'回复内容长度不能超过 200000 个字符'
            ]
            reply_content = request.POST['content'].strip()
            if (len(reply_content) == 0):
                errors = errors + 1
                reply_content_error = 1
            else:
                if (len(reply_content) > 200000):
                    errors = errors + 1
                    reply_content_error = 2
            template_values['reply_content'] = reply_content
            template_values['reply_content_error'] = reply_content_error
            template_values['reply_content_error_message'] = reply_content_error_messages[reply_content_error]
            template_values['errors'] = errors
            if (topic and (errors == 0)):
                reply = Reply()
                reply.topic = topic
                q = Counter.objects.filter(name='reply.max')
                if (len(q) == 1):
                    counter = q[0]
                    counter.value = counter.value + 1
                else:
                    counter = Counter()
                    counter.name = 'reply.max'
                    counter.value = 1
                q2 = Counter.objects.filter(name='reply.total')
                if (len(q2) == 1):
                    counter2 = q2[0]
                    counter2.value = counter2.value + 1
                else:
                    counter2 = Counter()
                    counter2.name = 'reply.total'
                    counter2.value = 1
                node = False
                section = False
                if topic:
                    q3 = Node.objects.filter(num=topic.node_num)
                    node = q3[0]
                    q4 = Section.objects.filter(num=node.section_num)
                    section = q4[0]
                reply.num = counter.value
                reply.content = reply_content
                reply.topic = topic
                reply.topic_num = topic.num
                reply.member = member
                reply.member_num = member.num
                reply.created_by = member.user.username
                topic.replies = topic.replies + 1
                topic.node_name = node.name
                topic.node_title = node.title
                topic.last_reply_by = member.user.username
                topic.last_touched = datetime.datetime.now()
                ua = request.META['HTTP_USER_AGENT']
                if (re.findall('Mozilla\/5.0 \(iPhone', ua)):
                    reply.source = 'iPhone'
                if (re.findall('Mozilla\/5.0 \(iPod', ua)):
                    reply.source = 'iPod'
                if (re.findall('Mozilla\/5.0 \(iPad', ua)):
                    reply.source = 'iPad'
                if (re.findall('Android', ua)):
                    reply.source = 'Android'
                if (re.findall('Mozilla\/5.0 \(PLAYSTATION 3;', ua)):
                    reply.source = 'PS3'
                reply.save()
                topic.save()
                counter.save()
                counter2.save()

                # Update member.ua

                member.ua = ua.replace(',gzip(gfe),gzip(gfe),gzip(gfe)', '')
                member.save()

                # Notifications

                notified_members = []
                keys = []
                ITQM = ITaskQueueManage()

                # type: reply

                if reply.member_num != topic.member_num:
                    q = Counter.objects.filter(name='notification.max')
                    if (len(q) == 1):
                        counter = q[0]
                        counter.value = counter.value + 1
                    else:
                        counter = Counter()
                        counter.name = 'notification.max'
                        counter.value = 1
                    q2 = Counter.objects.filter(name='notification.total')
                    if (len(q2) == 1):
                        counter2 = q2[0]
                        counter2.value = counter2.value + 1
                    else:
                        counter2 = Counter()
                        counter2.name = 'notification.total'
                        counter2.value = 1

                    notification = Notification()
                    notification.member = topic.member
                    notification.num = counter.value
                    notification.type = 'reply'
                    notification.payload = reply.content
                    notification.label1 = topic.title
                    notification.link1 = '/t/' + str(topic.num) + '#reply' + str(topic.replies)
                    notification.member = member
                    notification.for_member_num = topic.member_num

                    keys.append(str(topic.member.id))

                    counter.save()
                    counter2.save()
                    notification.save()

                    for key in keys:
                        ITQM.add(data='/notifications/check/' + key)
                        #taskqueue.add(url='/notifications/check/' + key)

                ITQM.add(data='/notifications/reply/' + str(reply.id))
                #taskqueue.add(url='/notifications/reply/' + str(reply.id))

                page_size = TOPIC_PAGE_SIZE
                pages = 1
                if topic.replies > page_size:
                    if (topic.replies % page_size) > 0:
                        pages = int(math.floor(topic.replies / page_size)) + 1
                    else:
                        pages = int(math.floor(topic.replies / page_size))

                memcache.set('Topic_' + str(topic.num), topic, 86400)
                memcache.delete('topic_' + str(topic.num) + '_replies_desc_compressed_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_asc_compressed_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_filtered_compressed_' + str(pages))

                memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_desktop_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_desktop_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_desktop_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_ios_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_ios_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_ios_' + str(pages))

                memcache.delete('member::' + str(member.num) + '::participated')
                memcache.delete('q_latest_16')
                memcache.delete('home_rendered')
                memcache.delete('home_rendered_mobile')
                if topic.replies < 50:
                    if config.fts_enabled:
                        try:
                            ITQM.add(data='/index/topic/' + str(topic.num))
                            #taskqueue.add(url='/index/topic/' + str(topic.num))
                        except:
                            pass
                # Twitter Sync
                if member.twitter_oauth == 1 and member.twitter_sync == 1:
                    access_token = OAuthToken.from_string(member.twitter_oauth_string)
                    twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                    if topic.replies > page_size:
                        link = 'http://' + request.META['HTTP_HOST'] + '/t/' + str(topic.num) + '?p=' + str(pages) + '#r' + str(topic.replies)
                    else:
                        link = 'http://' + request.META['HTTP_HOST'] + '/t/' + str(topic.num) + '#r' + str(topic.replies)
                    link_length = len(link)
                    reply_content_length = len(reply.content)
                    available = 140 - link_length - 1
                    if available > reply_content_length:
                        status = reply.content + ' ' + link
                    else:
                        status = reply.content[0:(available - 4)] + '... ' + link
                    HttpResponse('Status: ' + status)
                    logging.error('Status: ' + status)
                    try:
                        twitter.PostUpdate(status.encode('utf-8'))
                    except:
                        logging.error("Failed to sync to Twitter for Reply #" + str(reply.num))
                if pages > 1:
                    return HttpResponseRedirect('/t/' + str(topic.num) + '?p=' + str(pages) + '#reply' + str(topic.replies))
                else:
                    return HttpResponseRedirect('/t/' + str(topic.num) + '#reply' + str(topic.replies))
            else:
                node = False
                section = False
                if topic:
                    q2 = Node.objects.filter(num=topic.node_num)
                    node = q2[0]
                    q3 = Section.objects.filter(num=node.section_num)
                    section = q3[0]
                template_values['node'] = node
                template_values['section'] = section
                if browser['ios']:
                    path = os.path.join('mobile', 'topic.html')
                else:
                    path = os.path.join('desktop', 'topic.html')
                return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')


def TopicEditHandler(request, topic_num):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        errors = 0
        template_values['errors'] = errors
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        topic = False
        q = Topic.objects.filter(num=int(topic_num))
        if (len(q) == 1):
            topic = q[0]
            template_values['topic'] = topic
        can_edit = False
        ttl = 0
        if member:
            if member.level == 0:
                can_edit = True
            if topic.member_num == member.num:
                now = datetime.datetime.now()
                if (now - topic.created).seconds < 300:
                    can_edit = True
                    ttl = 300 - (now - topic.created).seconds
                    template_values['ttl'] = ttl
        if (member):
            if (can_edit):
                template_values['member'] = member
                if (topic):
                    template_values['page_title'] = site.title + u' › ' + topic.title + u' › 编辑'
                    template_values['topic_title'] = topic.title
                    template_values['topic_content'] = topic.content
                    node = False
                    section = False
                    if topic:
                        q2 = Node.objects.filter(num=topic.node_num)
                        node = q2[0]
                        q3 = Section.objects.filter(num=node.section_num)
                        section = q3[0]
                    template_values['node'] = node
                    template_values['section'] = section
                    if site.use_topic_types:
                        types = site.topic_types.split("\n")
                        options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                        i = 0
                        for a_type in types:
                            i = i + 1
                            detail = a_type.split(':')
                            if detail[0] == topic.type:
                                options = options + '<option value="' + str(i) + '" selected="selected">' + detail[0] + '</option>'
                            else:
                                options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                        tt = '<div def="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                        template_values['tt'] = tt
                    else:
                        template_values['tt'] = ''
                    q4 = Reply.objects.filter(topic_num=topic.num)
                    template_values['replies'] = q4
                    if browser['ios']:
                        path = os.path.join('mobile', 'edit_topic.html')
                    else:
                        path = os.path.join('desktop', 'edit_topic.html')
                else:
                    path = os.path.join('mobile', 'topic_not_found.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/t/' + str(topic_num))
        else:
            return HttpResponseRedirect('/signin')

    else:
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        browser = detect(request)
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        topic = False
        q = Topic.objects.filter(num=int(topic_num))
        if (len(q) == 1):
            topic = q[0]
            template_values['topic'] = topic
        can_edit = False
        ttl = 0
        if member:
            if member.level == 0:
                can_edit = True
            if topic.member_num == member.num:
                now = datetime.datetime.now()
                if (now - topic.created).seconds < 300:
                    can_edit = True
                    ttl = 300 - (now - topic.created).seconds
                    template_values['ttl'] = ttl
        if member:
            if can_edit:
                template_values['member'] = member
                if (topic):
                    template_values['page_title'] = site.title + u' › ' + topic.title + u' › 编辑'
                    q2 = Node.objects.filter(num=topic.node_num)
                    node = False
                    if (len(q2) == 1):
                        node = q2[0]
                    template_values['node'] = node
                    section = False
                    if node:
                        q3 = Section.objects.filter(num=node.section_num)
                        if (len(q3) == 1):
                            section = q3[0]
                    template_values['section'] = section
                    errors = 0
                    # Verification: title
                    topic_title_error = 0
                    topic_title_error_messages = ['',
                        u'请输入主题标题',
                        u'主题标题长度不能超过 120 个字符'
                        ]
                    topic_title = request.POST['title'].strip()
                    if (len(topic_title) == 0):
                        errors = errors + 1
                        topic_title_error = 1
                    else:
                        if (len(topic_title) > 120):
                            errors = errors + 1
                            topic_title_error = 2
                    template_values['topic_title'] = topic_title
                    template_values['topic_title_error'] = topic_title_error
                    template_values['topic_title_error_message'] = topic_title_error_messages[topic_title_error]
                    # Verification: content
                    topic_content_error = 0
                    topic_content_error_messages = ['',
                        u'主题内容长度不能超过 200000 个字符'
                    ]
                    topic_content = request.POST['content'].strip()
                    topic_content_length = len(topic_content)
                    if (topic_content_length > 200000):
                        errors = errors + 1
                        topic_content_error = 1
                    template_values['topic_content'] = topic_content
                    template_values['topic_content_error'] = topic_content_error
                    template_values['topic_content_error_message'] = topic_content_error_messages[topic_content_error]
                    # Verification: type
                    if site.use_topic_types:
                        types = site.topic_types.split("\n")
                        if len(types) > 0:
                            topic_type = request.POST['type'].strip()
                            try:
                                topic_type = int(topic_type)
                                if topic_type < 0:
                                    topic_type = 0
                                if topic_type > len(types):
                                    topic_type = 0
                                if topic_type > 0:
                                    detail = types[topic_type - 1].split(':')
                                    topic_type_label = detail[0]
                                    topic_type_color = detail[1]
                            except:
                                topic_type = 0
                        else:
                            topic_type = 0
                        options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                        i = 0
                        for a_type in types:
                            i = i + 1
                            detail = a_type.split(':')
                            if topic_type == i:
                                options = options + '<option value="' + str(i) + '" selected="selected">' + detail[0] + '</option>'
                            else:
                                options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                        tt = '<div def="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                        template_values['tt'] = tt
                    else:
                        template_values['tt'] = ''
                    template_values['errors'] = errors
                    if (errors == 0):
                        topic.title = topic_title
                        topic.content = topic_content
                        if topic_content_length > 0:
                            topic.has_content = True
                            topic.content_length = topic_content_length
                        else:
                            topic.has_content = False
                        path = os.path.join('portion', 'topic_content.html')
                        output = get_template(path).render(Context({'topic' : topic}))
                        topic.content_rendered = output.decode('utf-8')
                        if member.level != 0:
                            topic.last_touched = datetime.datetime.now()
                        if site.use_topic_types:
                            if topic_type > 0:
                                topic.type = topic_type_label
                                topic.type_color = topic_type_color
                            else:
                                topic.type = ''
                                topic.type_color = ''
                        topic.save()
                        memcache.delete('Topic_' + str(topic.num))
                        memcache.delete('q_latest_16')
                        memcache.delete('home_rendered')
                        memcache.delete('home_rendered_mobile')
                        ITQM = ITaskQueueManage()
                        if topic.replies < 50:
                            try:
                                ITQM.add(data='/index/topic/' + str(topic.num))
                                #taskqueue.add(url='/index/topic/' + str(topic.num))
                            except:
                                pass
                        return HttpResponseRedirect('/t/' + str(topic.num) + '#reply' + str(topic.replies))
                    else:
                        if browser['ios']:
                            path = os.path.join('mobile', 'edit_topic.html')
                        else:
                            path = os.path.join('desktop', 'edit_topic.html')
                        return render_to_response(path, template_values)
                else:
                    path = os.path.join('mobile', 'topic_not_found.html')
                    return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/t/' + str(topic_num))
        else:
            return HttpResponseRedirect('/signin')

def TopicDeleteHandler(request, topic_num):
    if request.method == 'GET':
        site = GetSite()
        member = CheckAuth(request)
        if member:
            if member.level == 0:
                q = Topic.objects.filter(num=int(topic_num))
                if len(q) == 1:
                    topic = q[0]
                    # Take care of Node
                    node = topic.node
                    node.topics = node.topics - 1
                    node.save()
                    # Take care of Replies
                    q2 = Reply.objects.filter(topic_num=int(topic_num))
                    replies_count = len(q2)
                    if replies_count > 0:
                        for reply in q2:
                            reply.delete()
                        q3 = Counter.objects.filter(name='reply.total')
                        if len(q3) == 1:
                            counter = q3[0]
                            counter.value = counter.value - replies_count
                            counter.save()
                    memcache.delete('Topic_' + str(topic.num))
                    topic.delete()
                    q4 = Counter.objects.filter(name='topic.total')
                    if len(q4) == 1:
                        counter2 = q4[0]
                        counter2.value = counter2.value - 1
                        counter2.save()
                    memcache.delete('q_latest_16')
                    memcache.delete('home_rendered')
                    memcache.delete('home_rendered_mobile')
        return HttpResponseRedirect('/')


def TopicPlainTextHandler(request):
    def get(self, topic_num):
        site = GetSite()
        topic = GetKindByNum('topic', topic_num)
        if topic:
            template_values = {}
            template_values['topic'] = topic
            replies = memcache.get('topic_' + str(topic_num) + '_replies_asc')
            if replies is None:
                q = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1 ORDER BY created ASC", topic.num)
                replies = q
                memcache.set('topic_' + str(topic_num) + '_replies_asc', q, 86400)
            if replies:
                template_values['replies'] = replies
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api', 'topic.txt')
            output = template.render(path, template_values)
            self.response.headers['Content-type'] = 'text/plain;charset=UTF-8'
            self.response.out.write(output)
        else:
            self.error(404)


#def TopicIndexHandler(request):
#    def post(self, topic_num):
#        site = GetSite()
#        if config.fts_enabled:
#            if os.environ['SERVER_SOFTWARE'] == 'Development/1.0':
#                try:
#                    urlfetch.fetch('http://127.0.0.1:20000/index/' + str(topic_num), headers = {"Authorization" : "Basic %s" % base64.b64encode(config.fts_username + ':' + config.fts_password)})
#                except:
#                    pass
#            else:
#                urlfetch.fetch('http://' + config.fts_server + '/index/' + str(topic_num), headers = {"Authorization" : "Basic %s" % base64.b64encode(config.fts_username + ':' + config.fts_password)})

def ReplyEditHandler(request, reply_num):
    if request.method == 'GET':
        template_values = {}
        site = GetSite()
        template_values['site'] = site
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › 编辑回复'
                template_values['member'] = member
                q = Reply.objects.filter(num=int(reply_num))
                if q[0]:
                    reply = q[0]
                    topic = reply.topic
                    node = topic.node
                    template_values['reply'] = reply
                    template_values['topic'] = topic
                    template_values['node'] = node
                    template_values['reply_content'] = reply.content
                    path = os.path.join('desktop', 'edit_reply.html')
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
        template_values['site'] = site
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › 编辑回复'
                template_values['member'] = member
                q = Reply.objects.filter(num=int(reply_num))
                if q[0]:
                    reply = q[0]
                    topic = reply.topic
                    node = topic.node
                    template_values['reply'] = reply
                    template_values['topic'] = topic
                    template_values['node'] = node
                    # Verification: content
                    errors = 0
                    reply_content_error = 0
                    reply_content_error_messages = ['',
                        u'请输入回复内容',
                        u'回复内容长度不能超过 2000 个字符'
                    ]
                    reply_content = request.POST['content'].strip()
                    if (len(reply_content) == 0):
                        errors = errors + 1
                        reply_content_error = 1
                    else:
                        if (len(reply_content) > 2000):
                            errors = errors + 1
                            reply_content_error = 2
                    template_values['reply_content'] = reply_content
                    template_values['reply_content_error'] = reply_content_error
                    template_values['reply_content_error_message'] = reply_content_error_messages[reply_content_error]
                    template_values['errors'] = errors
                    if (errors == 0):
                        reply.content = reply_content
                        reply.save()
                        memcache.delete('topic_' + str(topic.num) + '_replies_desc_compressed')
                        memcache.delete('topic_' + str(topic.num) + '_replies_asc_compressed')
                        memcache.delete('topic_' + str(topic.num) + '_replies_filtered_compressed')

                        pages = 1
                        memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_desktop_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_desktop_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_desktop_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_ios_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_ios_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_ios_' + str(pages))

                        return HttpResponseRedirect('/t/' + str(topic.num) + '#reply' + str(topic.replies))
                    else:
                        path = os.path.join('desktop', 'edit_reply.html')
                        return render_to_response(path, template_values)
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')

def TopicUploadImage(request):
    if request.method == 'POST':
        member = CheckAuth(request)
        if (member):
            try:
                image_req = request.FILES['imgFile']
                if image_req is None:
                    return HttpResponse(simplejson.dumps({'error':1},{'message','Can not found upload image.'}))
                ext = str(image_req).split('.');
                # 图片文件格式，并且文件大小不能超过2MB
                if len(ext) == 2 and image_req.size<1024*1024*2:
                    ext = ext[1].lower()
                    if ext=="jpg" or ext=="jpeg" or ext=="bmp" or  ext=='png':
                        timestamp = str(int(time.mktime(datetime.datetime.now().timetuple())))
                        datetoday= str(datetime.datetime.today())[0:10].replace('-', '')
                        new_name_src = timestamp + "." + ext
                        save_path = settings.STATIC_UPLOAD + "/" + member.user.username + "/" + datetoday
                        if not os.path.exists(save_path):
                            os.makedirs(save_path)
                        # Source image
                        image = Image.open(image_req)
                        if image.width>600:
                            image.thumbnail((600,600),Image.ANTIALIAS)
                        image.save(save_path + "/" + new_name_src, 'jpeg')
                        url = settings.STATIC_UPLOAD_WEB + member.user.username + "/" + datetoday + "/" + new_name_src
                        return HttpResponse(simplejson.dumps({'error':0},{'url',url}))
                    else:
                        return HttpResponse(simplejson.dumps({'error':1},{'message','Image type is not supported.(jpg,jpeg,bmp,png)'}))
                else:
                    return HttpResponse(simplejson.dumps({'error':1},{'message','The image is too large (too many bytes)'}))
            except:
                return HttpResponse(simplejson.dumps({'error':1},{'message','Server error: ' + sys.exc_info()}))
        return HttpResponse(simplejson.dumps({'error':1},{'message','Non login user.'}))
    return HttpResponse(simplejson.dumps({'error':1},{'message','Request type error.'}))

def TopicHitHandler(topic_id):
    topic = Topic.objects.get(id=int(topic_id))
    if topic:
        topic.hits = topic.hits + 1
        topic.save()

def PageHitHandler(page_id):
    page = Page.objects.get(id=int(page_id))
    if page:
        page.hits = page.hits + 1
        page.save()

#def main():
#    application = webapp.WSGIApplication([
#    ('/new/(.*)', NewTopicHandler),
#    ('/t/([0-9]+)', TopicHandler),
#    ('/t/([0-9]+).txt', TopicPlainTextHandler),
#    ('/edit/topic/([0-9]+)', TopicEditHandler),
#    ('/delete/topic/([0-9]+)', TopicDeleteHandler),
#    ('/index/topic/([0-9]+)', TopicIndexHandler),
#    ('/edit/reply/([0-9]+)', ReplyEditHandler),
#    ('/hit/topic/(.*)', TopicHitHandler),
#    ('/hit/page/(.*)', PageHitHandler)
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()
