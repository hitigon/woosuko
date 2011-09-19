#coding=utf-8
'''
Created on 11-9-12

@author: qiaoshun8888
'''
import hashlib
import os
import pickle
import re
import datetime
import Image
from django import template
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
import time
import sys
from iv2ex import SYSTEM_VERSION
from iv2ex.models import Topic, Reply, Member
import settings
from v2ex.babel.da import GetSite, GetMemberByUsername
from django.core.cache import cache as memcache

import config
from v2ex.babel.l10n import GetMessages, GetLanguageSelect, GetSupportedLanguages
from v2ex.babel.security import CheckAuth
from v2ex.babel.ua import detect

#template.register_template_library('v2ex.templatetags.filters')

def MemberHandler(request, member_username):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        session = request.session
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        template_values['show_extra_options'] = False
        if member:
            if member.num == 1:
                template_values['show_extra_options'] = True
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        one = False
        one = GetMemberByUsername(member_username)
        if one is not False:
            if one.followers_count is None:
                one.followers_count = 0
            template_values['one'] = one
            template_values['page_title'] = site.title + u' › ' + one.user.username
            template_values['canonical'] = 'http://' + site.domain + '/member/' + one.user.username
        if one is not False:
            blog = Topic.objects.filter(node_name='blog',member_num=one.num).order_by('-created')
            if len(blog) > 0:
                template_values['blog'] = blog[0]
            q2 = Topic.objects.filter(member_num=one.num).order_by('-created')[:10]
            template_values['topics'] = q2
            replies = memcache.get('member::' + str(one.num) + '::participated')
            if replies is None:
                q3 = Reply.objects.filter(member_num=one.num).order_by('-created')[0:100]
                ids = []
                replies = []
                i = 0
                for reply in q3:
                    if reply.topic.num not in ids:
                        i = i + 1
                        if i > 10:
                            break
                        replies.append(reply)
                        ids.append(reply.topic.num)
                if len(replies) > 0:
                    memcache.set('member::' + str(one.num) + '::participated', replies, 7200)
            if len(replies) > 0:
                template_values['replies'] = replies
        template_values['show_block'] = False
        template_values['show_follow'] = False
        template_values['favorited'] = False
        if one and member:
            if one.num != member.num:
                template_values['show_follow'] = True
                template_values['show_block'] = True
                try:
                    blocked = pickle.loads(member.blocked.encode('utf-8'))
                except:
                    blocked = []
                if one.num in blocked:
                    template_values['one_is_blocked'] = True
                else:
                    template_values['one_is_blocked'] = False
                if member.hasFavorited(one):
                    template_values['favorited'] = True
                else:
                    template_values['favorited'] = False
        if 'message' in session:
            template_values['message'] = session['message']
            del session['message']
        if one is not False:
            if browser['ios']:
                path = os.path.join('mobile', 'member_home.html')
            else:
                path = os.path.join('desktop', 'member_home.html')
        else:
            if browser['ios']:
                path = os.path.join('mobile', 'member_not_found.html')
            else:
                path = os.path.join('desktop', 'member_not_found.html')
        return render_to_response(path, template_values)

def MemberApiHandler(request):
    def get(self, member_username):
        site = GetSite()
        one = GetMemberByUsername(member_username)
        if one:
            if one.avatar_mini_url:
                if (one.avatar_mini_url[0:1] == '/'):
                    one.avatar_mini_url = 'http://' + site.domain + one.avatar_mini_url
                    one.avatar_normal_url = 'http://' +  site.domain + one.avatar_normal_url
                    one.avatar_large_url = 'http://' + site.domain + one.avatar_large_url
            template_values = {}
            template_values['site'] = site
            template_values['one'] = one
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api', 'member.json')
            self.response.headers['Content-type'] = 'application/json;charset=UTF-8'
            output = template.render(path, template_values)
            self.response.out.write(output)
        else:
            self.error(404)

def SettingsHandler(request):
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
        template_values['page_title'] = site.title + u' › ' + l10n.settings.decode('utf-8')
        if (member):
            template_values['member'] = member
            template_values['member_realname'] = member.truename
            template_values['member_sex'] = member.sex
            template_values['member_username'] = member.user.username
            template_values['member_email'] = member.user.email
            if (member.website == None):
                member.website = ''
            template_values['member_website'] = member.website
            if (member.twitter == None):
                member.twitter = ''
            template_values['member_twitter'] = member.twitter
            if (member.location == None):
                member.location = ''
            if member.psn is None:
                member.psn = ''
            template_values['member_psn'] = member.psn
            if (member.my_home == None):
                member.my_home = ''
            template_values['member_my_home'] = member.my_home
            template_values['member_btc'] = member.btc
            template_values['member_location'] = member.location
            if (member.tagline == None):
                member.tagline = ''
            template_values['member_tagline'] = member.tagline
            if (member.bio == None):
                member.bio = ''
            template_values['member_bio'] = member.bio
            template_values['member_show_home_top'] = member.show_home_top
            template_values['member_show_quick_post'] = member.show_quick_post
            if member.l10n is None:
                member.l10n = 'en'
            template_values['member_l10n'] = member.l10n
            s = GetLanguageSelect(member.l10n)
            template_values['s'] = s
            if member.twitter_sync == 1:
                template_values['member_twitter_sync'] = 1
            if member.use_my_css == 1:
                template_values['member_use_my_css'] = 1
            if (member.my_css == None):
                member.my_css = ''
            template_values['member_my_css'] = member.my_css
            if 'message' in session:
                message = session['message']
                del session['message']
            else:
                message = None
            template_values['message'] = message
            try:
                blocked = pickle.loads(member.blocked.encode('utf-8'))
            except:
                blocked = []
            template_values['member_stats_blocks'] = len(blocked)
            if browser['ios']:
                path = os.path.join('mobile', 'member_settings.html')
            else:
                path = os.path.join('desktop', 'member_settings.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')

    else:
        session = request.session
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        errors = 0
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        template_values['page_title'] = site.title + u' › ' + l10n.settings.decode('utf-8')
        if (member):
            template_values['member'] = member
            template_values['member_realname'] = member.truename
            template_values['member_sex'] = member.sex
            template_values['member_username'] = member.user.username
            template_values['member_email'] = member.user.email
            template_values['member_website'] = member.website
            template_values['member_twitter'] = member.twitter
            # Verification: realname
            member_realname_error = 0
            member_realname_error_messages = ['',
                l10n.realname_empty,
                l10n.realname_too_long,]
            member_realname = request.POST['realname'].strip()
            if (len(member_realname) == 0):
                errors = errors + 1
                member_realname_error = 1
            else:
                if (len(member_realname) > 20):
                    errors = errors + 1
                    member_realname_error = 2
            template_values['member_realname'] = member_realname
            template_values['member_realname_error'] = member_realname_error
            template_values['member_realname_error_message'] = member_realname_error_messages[member_realname_error]
            # Verification: sex
            member_sex_error = 0
            member_sex_error_messages = ['',
                l10n.sex_empty,]
            if 'sex' in request.POST:
                member_sex = request.POST['sex'].strip()
            else:
                member_sex = ''
            if (len(member_sex) == 0):
                errors = errors + 1
                member_sex_error = 1
            template_values['member_sex'] = member_sex
            template_values['member_sex_error'] = member_sex_error
            template_values['member_sex_error_message'] = member_sex_error_messages[member_sex_error]
            # Verification: username
            member_username_error = 0
            member_username_error_messages = ['',
                l10n.username_empty,
                l10n.username_too_long,
                l10n.username_too_short,
                l10n.username_invalid,
                l10n.username_taken,
                '你已经更改过一次账户']
            member_username = request.POST['username'].strip()
            if (len(member_username) == 0):
                errors = errors + 1
                member_username_error = 1
            else:
                if (len(member_username) > 16):
                    errors = errors + 1
                    member_username_error = 2
                else:
                    if (len(member_username) < 3):
                        errors = errors + 1
                        member_username_error = 3
                    else:
                        if (re.search('^[a-zA-Z0-9\_]+$', member_username)):
                            q = Member.objects.filter(username_lower=member_username.lower()).exclude(id=member.id)
                            if len(q) > 0:
                                errors = errors + 1
                                member_username_error = 5
                            else:
                                if request.user.username != member_username and member.username_editable == 0:
                                    errors = errors + 1
                                    member_username_error = 6
                        else:
                            errors = errors + 1
                            member_username_error = 4
            template_values['member_username'] = member_username
            template_values['member_username_error'] = member_username_error
            template_values['member_username_error_message'] = member_username_error_messages[member_username_error]
            # Verification: email
            member_email_error = 0
            member_email_error_messages = ['',
                u'请输入你的电子邮件地址',
                u'电子邮件地址长度不能超过 32 个字符',
                u'你输入的电子邮件地址不符合规则',
                u'抱歉这个电子邮件地址已经有人注册过了']
            if 'email' in request.POST:
                member_email = request.POST['email'].strip()
            else:
                member_email = ''
            if (len(member_email) == 0):
                errors = errors + 1
                member_email_error = 1
            else:
                if (len(member_email) > 32):
                    errors = errors + 1
                    member_email_error = 2
                else:
                    p = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)
                    if (p.search(member_email)):
                        q = User.objects.filter(email=member_email.lower()).exclude(id=request.user.id)
                        if (len(q) > 0):
                            errors = errors + 1
                            member_email_error = 4
                    else:
                        errors = errors + 1
                        member_email_error = 3
            template_values['member_email'] = member_email
            template_values['member_email_error'] = member_email_error
            template_values['member_email_error_message'] = member_email_error_messages[member_email_error]
            # Verification: website
            member_website_error = 0
            member_website_error_messages = ['',
                u'个人网站地址长度不能超过 200 个字符',
                u'这个网站地址不符合规则'
            ]
            member_website = request.POST['website'].strip()
            if (len(member_website) == 0):
                member_website = ''
            else:
                if (len(member_website) > 200):
                    errors = errors + 1
                    member_website_error = 1
                else:
                    p = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
                    if (p.search(member_website)):
                        errors = errors
                    else:
                        errors = errors + 1
                        member_website_error = 2
            template_values['member_website'] = member_website
            template_values['member_website_error'] = member_website_error
            template_values['member_website_error_message'] = member_website_error_messages[member_website_error]
            # Verification: Twitter
            member_twitter_error = 0
            member_twitter_error_messages = ['',
                u'Twitter 用户名长度不能超过 20 个字符',
                u'Twitter 用户名不符合规则'
            ]
            member_twitter = request.POST['twitter'].strip()
            if (len(member_twitter) == 0):
                member_twitter = ''
            else:
                if (len(member_twitter) > 20):
                    errors = errors + 1
                    member_twitter_error = 1
                else:
                    p = re.compile('[a-zA-Z0-9\_]+')
                    if (p.search(member_twitter)):
                        errors = errors
                    else:
                        errors = errors + 1
                        member_twitter_error = 2
            template_values['member_twitter'] = member_twitter
            template_values['member_twitter_error'] = member_twitter_error
            template_values['member_twitter_error_message'] = member_twitter_error_messages[member_twitter_error]
            # Verification: psn
            member_psn_error = 0
            member_psn_error_messages = ['',
                u'PSN ID 长度不能超过 20 个字符',
                u'PSN ID 不符合规则'
            ]
            member_psn = request.POST['psn'].strip()
            if (len(member_psn) == 0):
                member_psn = ''
            else:
                if (len(member_psn) > 20):
                    errors = errors + 1
                    member_psn_error = 1
                else:
                    p = re.compile('^[a-zA-Z0-9\-\_]+$')
                    if (p.search(member_psn)):
                        errors = errors
                    else:
                        errors = errors + 1
                        member_psn_error = 2
            template_values['member_psn'] = member_psn
            template_values['member_psn_error'] = member_psn_error
            template_values['member_psn_error_message'] = member_psn_error_messages[member_psn_error]
            # Verification: my_home
            member_my_home_error = 0
            member_my_home_error_messages = ['',
                u'不是一个合法的自定义首页跳转位置',
                u'自定义首页跳转位置长度不能超过 32 个字符',
                u'自定义首页跳转位置必须以 / 开头'
            ]
            member_my_home = request.POST['my_home'].strip()
            if len(member_my_home) > 0:
                if member_my_home == '/' or member_my_home.startswith('/signout'):
                    member_my_home_error = 1
                    errors = errors + 1
                else:
                    if len(member_my_home) > 32:
                        member_my_home_error = 2
                        errors = errors + 1
                    else:
                        if member_my_home.startswith('/') is not True:
                            member_my_home_error = 3
                            errors = errors + 1
            template_values['member_my_home'] = member_my_home
            template_values['member_my_home_error'] = member_my_home_error
            template_values['member_my_home_error_message'] = member_my_home_error_messages[member_my_home_error]
            # Verification: btc
            member_btc_error = 0
            member_btc_error_messages = ['',
                u'BTC 收款地址长度不能超过 40 个字符',
                u'BTC 收款地址不符合规则'
            ]
            member_btc = request.POST['btc'].strip()
            if (len(member_btc) == 0):
                member_btc = ''
            else:
                if (len(member_btc) > 40):
                    errors = errors + 1
                    member_btc_error = 1
                else:
                    p = re.compile('^[a-zA-Z0-9]+$')
                    if (p.search(member_btc)):
                        errors = errors
                    else:
                        errors = errors + 1
                        member_btc_error = 2
            template_values['member_btc'] = member_btc
            template_values['member_btc_error'] = member_btc_error
            template_values['member_btc_error_message'] = member_btc_error_messages[member_btc_error]
            # Verification: location
            member_location_error = 0
            member_location_error_messages = ['',
                u'所在地长度不能超过 40 个字符'
            ]
            member_location = request.POST['location'].strip()
            if (len(member_location) == 0):
                member_location = ''
            else:
                if (len(member_location) > 40):
                    errors = errors + 1
                    member_location_error = 1
            template_values['member_location'] = member_location
            template_values['member_location_error'] = member_location_error
            template_values['member_location_error_message'] = member_location_error_messages[member_location_error]
            # Verification: tagline
            member_tagline_error = 0
            member_tagline_error_messages = ['',
                u'个人签名长度不能超过 70 个字符'
            ]
            member_tagline = request.POST['tagline'].strip()
            if (len(member_tagline) == 0):
                member_tagline = ''
            else:
                if (len(member_tagline) > 70):
                    errors = errors + 1
                    member_tagline_error = 1
            template_values['member_tagline'] = member_tagline
            template_values['member_tagline_error'] = member_tagline_error
            template_values['member_tagline_error_message'] = member_tagline_error_messages[member_tagline_error]
            # Verification: bio
            member_bio_error = 0
            member_bio_error_messages = ['',
                u'个人简介长度不能超过 2000 个字符'
            ]
            member_bio = request.POST['bio'].strip()
            if (len(member_bio) == 0):
                member_bio = ''
            else:
                if (len(member_bio) > 2000):
                    errors = errors + 1
                    member_bio_error = 1
            template_values['member_bio'] = member_bio
            template_values['member_bio_error'] = member_bio_error
            template_values['member_bio_error_message'] = member_bio_error_messages[member_bio_error]
            # Verification: show_home_top and show_quick_post
            try:
                member_show_home_top = int(request.POST['show_home_top'])
            except:
                member_show_home_top = 1
            try:
                member_show_quick_post = int(request.POST['show_quick_post'])
            except:
                member_show_quick_post = 0
            if member_show_home_top not in [0, 1]:
                member_show_home_top = 1
            if member_show_quick_post not in [0, 1]:
                member_show_quick_post = 0
            # Verification: l10n
            member_l10n = request.POST['l10n'].strip()
            supported = GetSupportedLanguages()
            if member_l10n == '':
                member_l10n = site.l10n
            else:
                if member_l10n not in supported:
                    member_l10n = site.l10n
            s = GetLanguageSelect(member_l10n)
            template_values['s'] = s
            template_values['member_l10n'] = member_l10n
            # Verification: twitter_sync
            if member.twitter_oauth == 1:
                if 'twitter_sync' in request.POST:
                    member_twitter_sync = request.POST['twitter_sync']
                else:
                    member_twitter_sync = ''
                if member_twitter_sync == 'on':
                    member_twitter_sync = 1
                else:
                    member_twitter_sync = 0
                template_values['member_twitter_sync'] = member_twitter_sync
            # Verification: use_my_css
            member_use_my_css = None
            if 'user_my_css' in request.POST:
                member_use_my_css = request.POST['use_my_css']
            else:
                member_use_my_css = ''
            if member_use_my_css == 'on':
                member_use_my_css = 1
            else:
                member_use_my_css = 0
            template_values['member_use_my_css'] = member_use_my_css
            # Verification: my_css
            member_my_css_error = 0
            member_my_css_error_messages = ['',
                u'CSS Hack cannot be longer than 2000 characters'
            ]
            member_my_css = request.POST['my_css'].strip()
            if (len(member_my_css) == 0):
                member_my_css = ''
            else:
                if (len(member_my_css) > 2000):
                    errors = errors + 1
                    member_my_css_error = 1
            template_values['member_my_css'] = member_my_css
            template_values['member_my_css_error'] = member_my_css_error
            template_values['member_my_css_error_message'] = member_my_css_error_messages[member_my_css_error]
            template_values['errors'] = errors
            if (errors == 0):
                user = request.user
                member.truename = member_realname
                member.sex = member_sex
                # 如果用户更改了账户,则editable置为0
                if user.username != member_username:
                    user.username = member_username
                    member.username_editable = 0
                    member.username_lower = member_username.lower()
                user.email = member_email.lower()
                member.website = member_website
                member.twitter = member_twitter
                member.psn = member_psn
                member.btc = member_btc
                member.location = member_location
                member.tagline = member_tagline
                if member.twitter_oauth == 1:
                    member.twitter_sync = member_twitter_sync
                member.use_my_css = member_use_my_css
                member.my_css = member_my_css
                if member_my_home_error == 0 and len(member_my_home) > 0:
                    member.my_home = member_my_home
                else:
                    if member_my_home_error == 0:
                        member.my_home = ''
                member.bio = member_bio
                member.show_home_top = member_show_home_top
                member.show_quick_post = member_show_quick_post
                member.l10n = member_l10n
                user.save()
                member.save()
                memcache.delete('Member::' + str(member.user.username))
                memcache.delete('Member::' + str(member.username_lower))
                memcache.set('Member_' + str(member.num), member, 86400)
                session['message'] = '个人设置成功更新'
                return HttpResponseRedirect('/settings')
            else:
                if browser['ios']:
                    path = os.path.join('mobile', 'member_settings.html')
                else:
                    path = os.path.join('desktop', 'member_settings.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')

def SettingsPasswordHandler(request):
    if request.method == 'POST':
        site = GetSite()
        browser = detect(request)
        session = request.session
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 密码设置'
        template_values['system_version'] = SYSTEM_VERSION
        errors = 0
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            template_values['member'] = member
            template_values['member_username'] = member.user.username
            template_values['member_email'] = member.user.email
            # Verification: password
            password_error = 0
            password_update = False
            password_error_messages = ['',
                '新密码长度不能超过 32 个字符',
                '请输入当前密码',
                '当前密码不正确'
            ]
            password_new = request.POST['password_new'].strip()
            if (len(password_new) > 0):
                password_update = True
                if (len(password_new) > 32):
                    password_error = 1
                else:
                    password_current = request.POST['password_current'].strip()
                    if (len(password_current) == 0):
                        password_error = 2
                    else:
                        if not member.user.check_password(password_current):
                            password_error = 3
            template_values['password_error'] = password_error
            template_values['password_error_message'] = password_error_messages[password_error]
            if ((password_error == 0) and (password_update == True)):
                member.user.set_password(password_new)
                member.user.save()
                member.auth = hashlib.sha1(str(member.num) + ':' + member.user.password).hexdigest()
                member.save()
                memcache.set(member.auth, member.num, 86400 * 365)
                memcache.set('Member_' + str(member.num), member, 86400 * 365)
                session['message'] = '密码已成功更新，下次请用新密码登录'
                #self.response.headers['Set-Cookie'] = 'auth=' + member.auth + '; expires=' + (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%a, %d-%b-%Y %H:%M:%S GMT") + '; path=/'
                #self.redirect('/settings')
                return HttpResponseRedirect('/settings')
            else:
                if browser['ios']:
                    path = os.path.join('mobile', 'member_settings_password.html')
                else:
                    path = os.path.join('desktop', 'member_settings_password.html')
                return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')

def SettingsAvatarHandler(request):
    if request.method == 'GET':
        site = GetSite()
        session = request.session
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 头像'
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if (member):
            if 'message' in session:
                template_values['message'] = session['message']
                del session['message']
            template_values['member'] = member
            if browser['ios']:
                path = os.path.join('mobile', 'member_settings_avatar.html')
            else:
                path = os.path.join('desktop', 'member_settings_avatar.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')

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
            dest = '/settings-avatar/'
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
                        member.avatar_large_url = settings.STATIC_UPLOAD_WEB + member.user.username + "/" + datetoday + "/" + new_name_large
                        # Normal 48x48
                        image.thumbnail((48,48),Image.ANTIALIAS)
                        image.save(save_path + "/" + new_name_normal, 'jpeg')
                        member.avatar_normal_url = settings.STATIC_UPLOAD_WEB + member.user.username + "/" + datetoday + "/" + new_name_normal
                        # Small 24x24
                        image.thumbnail((24,24),Image.ANTIALIAS)
                        image.save(save_path + "/" + new_name_small, 'jpeg')
                        member.avatar_mini_url = settings.STATIC_UPLOAD_WEB + member.user.username + "/" + datetoday + "/" + new_name_small
                        # Save avatar info
                        member.save()
                    else:
                        return HttpResponseRedirect(dest)
                else:
                    return HttpResponseRedirect(dest)
            except:
                print "Unexpected error:", sys.exc_info()
                return HttpResponseRedirect(dest)
            memcache.set('Member_' + str(member.num), member, 86400 * 365)
            memcache.set('Member::' + member.username_lower, member, 86400 * 365)
            memcache.delete('Avatar::avatar_' + str(member.num) + '_large')
            memcache.delete('Avatar::avatar_' + str(member.num) + '_normal')
            memcache.delete('Avatar::avatar_' + str(member.num) + '_mini')
            session['message'] = '新头像设置成功'
            return HttpResponseRedirect('/settings-avatar/')
        else:
            return HttpResponseRedirect('/signin')

def MemberBlockHandler(request):
    def get(self, key):
        go = '/'
        member = CheckAuth(request)
        if member:
            member = db.get(member.key())
            one = db.get(db.Key(key))
            if one:
                if one.num != member.num:
                    try:
                        blocked = pickle.loads(member.blocked.encode('utf-8'))
                    except:
                        blocked = []
                    if len(blocked) == 0:
                        blocked = []
                    if one.num not in blocked:
                        blocked.append(one.num)
                    member.blocked = pickle.dumps(blocked)
                    member.put()
                    memcache.set('Member_' + str(member.num), member, 86400)
        self.redirect(go)

def MemberUnblockHandler(request):
    def get(self, key):
        go = '/'
        member = CheckAuth(request)
        if member:
            member = db.get(member.key())
            one = db.get(db.Key(key))
            if one:
                if one.num != member.num:
                    try:
                        blocked = pickle.loads(member.blocked.encode('utf-8'))
                    except:
                        blocked = []
                    if len(blocked) == 0:
                        blocked = []
                    if one.num  in blocked:
                        blocked.remove(one.num)
                    member.blocked = pickle.dumps(blocked)
                    member.put()
                    memcache.set('Member_' + str(member.num), member, 86400)
        self.redirect(go)

#def main():
#    application = webapp.WSGIApplication([
#    ('/member/([a-z0-9A-Z\_\-]+)', MemberHandler),
#    ('/member/([a-z0-9A-Z\_\-]+).json', MemberApiHandler),
#    ('/settings', SettingsHandler),
#    ('/settings/password', SettingsPasswordHandler),
#    ('/settings/avatar', SettingsAvatarHandler),
#    ('/block/(.*)', MemberBlockHandler),
#    ('/unblock/(.*)', MemberUnblockHandler)
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()