#coding=utf-8
'''
Created on 2011-9-12

@author: JohnQiao
'''
import hashlib
import logging
import os
import pickle
import random
import re
import datetime
import time
from django.contrib.auth import authenticate, login, logout
from django.template.loader import get_template
from django.template import Context;
from django.contrib.auth.models import User
from django.core.context_processors import request
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.cache import cache as memcache
from django.core.exceptions import ObjectDoesNotExist
import math
from iv2ex import SYSTEM_VERSION
from iv2ex import config
from iv2ex.models import Member, Counter, Node, Section, Topic
from v2ex.babel.da import GetSite, GetKindByName, GetKindByNum
from v2ex.babel.ext import captcha
from v2ex.babel.l10n import GetMessages
from v2ex.babel.security import CheckAuth
from v2ex.babel.ua import detect


def HomeHandler(request):
    if request.method == 'GET':
#        host = request.headers['Host']
#        if host == 'beta.v2ex.com':
#            return self.redirect('http://www.v2ex.com/')
        response = HttpResponse()
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = GetSite()
        template_values['canonical'] = 'http://' + site.domain + '/'
        template_values['rnd'] = random.randrange(1, 100)
        template_values['page_title'] = site.title
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        if member:
            if member.my_home != None and len(member.my_home) > 0:
                return HttpResponseRedirect(member.my_home)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            expire = datetime.datetime.now() + datetime.timedelta(days=365)
            expire_f = time.mktime(expire.timetuple())
            response.set_cookie("auth", member.auth, expire_f)
            template_values['member'] = member
            try:
                blocked = pickle.loads(member.blocked.encode('utf-8'))
            except:
                blocked = []
            if (len(blocked) > 0):
                template_values['blocked'] = ','.join(map(str, blocked))
        if member:
            recent_nodes = memcache.get('member::' + str(member.num) + '::recent_nodes')
            if recent_nodes:
                template_values['recent_nodes'] = recent_nodes
        nodes_new = []
        nodes_new = memcache.get('home_nodes_new')
        if nodes_new is None:
            nodes_new = []
            qnew = Node.objects.filter().order_by('-created')[:10]
            if (len(qnew) > 0):
                i = 0
                for node in qnew:
                    nodes_new.append(node)
                    i = i + 1
            memcache.set('home_nodes_new', nodes_new, 3600)
        template_values['nodes_new'] = nodes_new
        if browser['ios']:
            s = ''
            s = memcache.get('home_sections_neue')
            if (s == None):
                s = ''
                q = Section.objects.filter().order_by('created')
                if (len(q) > 0):
                    for section in q:
                        q2 = Node.objects.filter(section_num=section.num).order_by('created')
                        n = ''
                        if (len(q2) > 0):
                            nodes = []
                            i = 0
                            for node in q2:
                                nodes.append(node)
                                i = i + 1
                            random.shuffle(nodes)
                            for node in nodes:
                                fs = random.randrange(12, 16)
                                n = n + '<a href="/go/' + node.name + '" style="font-size: ' + str(fs) + 'px;">' + node.title + '</a>&nbsp; '
                        s = s + '<div class="section">' + section.title + '</div><div class="cell">' + n + '</div>'
                memcache.set('home_sections_neue', s, 600)
            template_values['s'] = s
        ignored = ['newbie', 'in', 'flamewar', 'pointless', 'tuan', '528491', 'chamber', 'autistic', 'blog', 'love', 'flood', 'beforesunrise']
        if browser['ios']:
            home_rendered = memcache.get('home_rendered_mobile')
            if home_rendered is None:
                latest = memcache.get('q_latest_16')
                if (latest):
                    template_values['latest'] = latest
                else:
                    q2 = Topic.objects.filter().order_by('-last_touched')[:16]
                    topics = []
                    for topic in q2:
                        if topic.node_name not in ignored:
                            topics.append(topic)
                    memcache.set('q_latest_16', topics, 600)
                    latest = topics
                    template_values['latest'] = latest
                path = os.path.join('portion', 'home_mobile.html')
                home_rendered = get_template(path).render(Context(template_values))
                memcache.set('home_rendered_mobile', home_rendered, 600)
            template_values['home'] = home_rendered
        else:
            home_rendered = memcache.get('home_rendered')
            if home_rendered is None:
                latest = memcache.get('q_latest_16')
                if (latest):
                    template_values['latest'] = latest
                else:
                    q2 = Topic.objects.filter().order_by('-last_touched')[:16]
                    topics = []
                    for topic in q2:
                        if topic.node_name not in ignored:
                            topics.append(topic)
                    memcache.set('q_latest_16', topics, 600)
                    latest = topics
                    template_values['latest'] = latest
                path = os.path.join('portion', 'home.html')
                home_rendered = get_template(path).render(Context(template_values))
                memcache.set('home_rendered', home_rendered, 600)
            template_values['home'] = home_rendered
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
        if (browser['ios']):
            path = os.path.join('mobile', 'index.html')
        else:
            hottest = memcache.get('index_hottest_sidebar')
            if hottest is None:
                qhot = Node.objects.filter().order_by('-topics')[:25]
                hottest = u''
                for node in qhot:
                    hottest = hottest + '<a href="/go/' + node.name + '" class="item_node">' + node.title + '</a>'
                memcache.set('index_hottest_sidebar', hottest, 5000)
            template_values['index_hottest_sidebar'] = hottest
            c = memcache.get('index_categories')
            if c is None:
                c = ''
                i = 0
                if site.home_categories is not None:
                    categories = site.home_categories.split("\n")
                else:
                    categories = []
                for category in categories:
                    category = category.strip()
                    i = i + 1
                    if i == len(categories):
                        css_class = 'inner'
                    else:
                        css_class = 'cell'
                    c = c + '<div class="' + css_class + '"><table cellpadding="0" cellspacing="0" border="0"><tr><td align="right" width="60"><span class="fade">' + category + '</span></td><td style="line-height: 200%; padding-left: 15px;">'
                    qx = Node.objects.filter(category=category).order_by('-topics')
                    for node in qx:
                        c = c + '<a href="/go/' + node.name + '" style="font-size: 14px;">' + node.title + '</a>&nbsp; &nbsp; '
                    c = c + '</td></tr></table></div>'
                    memcache.set('index_categories', c, 3600)
            template_values['c'] = c
            path = os.path.join('desktop', 'index.html')
        return render_to_response(path, template_values)

def PlanesHandler(request):
    if request.method == 'GET':
        template_values = {}
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = GetSite()
        template_values['canonical'] = 'http://' + site.domain + '/'
        template_values['rnd'] = random.randrange(1, 100)
        template_values['page_title'] = site.title
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        template_values['member'] = member
        c = 0
        c = memcache.get('planes_c')
        s = ''
        s = memcache.get('planes')
        if (s == None):
            c = 0
            s = ''
            q = Section.objects.filter().order_by('-nodes')
            if (len(q) > 0):
                for section in q:
                    q2 = Node.objects.filter(section_num=section.num).order_by('-topics')
                    n = ''
                    if (len(q2) > 0):
                        nodes = []
                        i = 0
                        for node in q2:
                            nodes.append(node)
                            i = i + 1
                        random.shuffle(nodes)
                        for node in nodes:
                            fs = random.randrange(12, 16)
                            n = n + '<a href="/go/' + node.name + '" class="item_node">' + node.title + '</a>'
                            c = c + 1
                    s = s + '<div class="sep20"></div><div class="box"><div class="cell"><div class="fr"><strong class="snow">' + section.title_alternative + u'</strong><small class="snow"> • ' + str(section.nodes) + ' nodes</small></div>' + section.title + '</div><div class="inner" align="center">' + n + '</div></div>'
            memcache.set('planes', s, 3600)
            memcache.set('planes_c', c, 3600)
        template_values['c'] = c
        template_values['s'] = s
        path = os.path.join('desktop', 'planes.html')
        return render_to_response(path, template_values)

def RecentHandler(request):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        template_values['system_version'] = SYSTEM_VERSION
        template_values['page_title'] = site.title + u' › 最近的 50 个主题'
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            template_values['member'] = member
            try:
                blocked = pickle.loads(member.blocked.encode('utf-8'))
            except:
                blocked = []
            if (len(blocked) > 0):
                template_values['blocked'] = ','.join(map(str, blocked))
        latest = memcache.get('q_recent_50')
        if (latest):
            template_values['latest'] = latest
        else:
            q2 = Topic.objects.filter().order_by('-last_touched')[16:50]
            topics = []
            IGNORED_RECENT = ['flamewar', 'pointless', 'in', 'autistic', 'chamber', 'flood']
            for topic in q2:
                if topic.node_name not in IGNORED_RECENT:
                    topics.append(topic)
            memcache.set('q_recent_50', topics, 80)
            template_values['latest'] = topics
            template_values['latest_total'] = len(topics)
        if browser['ios']:
            path = os.path.join('mobile', 'recent.html')
        else:
            path = os.path.join('desktop', 'recent.html')
#        expires_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
#        expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
#        self.response.headers.add_header("Expires", expires_str)
#        self.response.headers['Cache-Control'] = 'max-age=120, must-revalidate'
        return render_to_response(path, template_values)

def UAHandler(request):
    def get(self):
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        template_values['ua'] = os.environ['HTTP_USER_AGENT']
        template_values['page_title'] = site.title + u' › 用户代理字符串'
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile', 'ua.html')
        output = template.render(path, template_values)
        self.response.out.write(output)

def SigninHandler(request):
    if request.method == 'GET':
        site = GetSite()
        member = False
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 登入'
        template_values['system_version'] = SYSTEM_VERSION
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        errors = 0
        template_values['errors'] = errors
        if browser['ios']:
            path = os.path.join('mobile', 'signin.html')
        else:
            path = os.path.join('desktop', 'signin.html')
        return render_to_response(path, template_values)

    else:
        response = HttpResponse()
        site = GetSite()
        member = False
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 登入'
        template_values['system_version'] = SYSTEM_VERSION
        u = request.POST['u'].strip()
        p = request.POST['p'].strip()
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        errors = 0
        error_messages = ['', '请输入用户名和密码', '你输入的用户名或密码不正确', '请勿采用ROOT账号登陆']
        if (len(u) > 0 and len(p) > 0):
            # 邮箱登陆,转化为用户名登陆
            if '@' in u:
                q = User.objects.filter(email=u.lower())
                if len(q) == 1:
                    q = q[0]
                    u = q.username
            # 用户名登陆
            user = authenticate(username=u, password=p)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    try:
                        member = Member.objects.get(user__id__exact=user.id)
                    except ObjectDoesNotExist:
                        errors = 3
                    else:
                        expire = datetime.datetime.now() + datetime.timedelta(days=365)
                        expire_f = time.mktime(expire.timetuple())
                        response.set_cookie("auth", member.auth, expire_f)
                        return HttpResponseRedirect('/')
            else:
                errors = 2
        else:
            errors = 1
        template_values['u'] = u
        template_values['p'] = p
        template_values['errors'] = errors
        template_values['error_message'] = error_messages[errors]
        if browser['ios']:
            path = os.path.join('mobile', 'signin.html')
        else:
            path = os.path.join('desktop', 'signin.html')
        return render_to_response(path, template_values)

# 注册
def SignupHandler(request):
    if request.method == 'GET':
        site = GetSite()
        member = False
        chtml = captcha.displayhtml(
            public_key = config.recaptcha_public_key,
            use_ssl = False,
            error = None)
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 注册'
        template_values['system_version'] = SYSTEM_VERSION
        template_values['errors'] = 0
        template_values['captchahtml'] = chtml
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if browser['ios']:
            path = os.path.join('mobile', 'signup.html')
        else:
            path = os.path.join('desktop', 'signup.html')

        return render_to_response(path, template_values)

    else:
        response = HttpResponse()
        site = GetSite()
        member = False
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 注册'
        template_values['system_version'] = SYSTEM_VERSION
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        errors = 0
        # Verification: username
        member_username_error = 0
        member_username_error_messages = ['',
            l10n.username_empty,
            l10n.username_too_long,
            l10n.username_too_short,
            l10n.username_invalid,
            l10n.username_taken]
        member_username = request.POST['username'].strip()
        # Special cases
        if 'vpn' in member_username:
            return HttpResponseRedirect('/')#('http://www.v2ex.com/')
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
                        q = Member.objects.filter(username_lower=member_username.lower())
                        if len(q) > 0:
                            errors = errors + 1
                            member_username_error = 5
                    else:
                        errors = errors + 1
                        member_username_error = 4
        template_values['member_username'] = member_username
        template_values['member_username_error'] = member_username_error
        template_values['member_username_error_message'] = member_username_error_messages[member_username_error]
        # Verification: password
        member_password_error = 0
        member_password_error_messages = ['',
            u'请输入你的密码',
            u'密码长度不能超过 32 个字符'
        ]
        member_password = request.POST['password'].strip()
        if (len(member_password) == 0):
            errors = errors + 1
            member_password_error = 1
        else:
            if (len(member_password) > 32):
                errors = errors + 1
                member_password_error = 2
        template_values['member_password'] = member_password
        template_values['member_password_error'] = member_password_error
        template_values['member_password_error_message'] = member_password_error_messages[member_password_error]
        # Verification: email
        member_email_error = 0
        member_email_error_messages = ['',
            u'请输入你的电子邮件地址',
            u'电子邮件地址长度不能超过 32 个字符',
            u'你输入的电子邮件地址不符合规则',
            u'抱歉这个电子邮件地址已经有人注册过了']
        member_email = request.POST['email'].strip()
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
                    q = User.objects.filter(email=member_email.lower())
                    if (len(q) > 0):
                        errors = errors + 1
                        member_email_error = 4
                else:
                    errors = errors + 1
                    member_email_error = 3
        template_values['member_email'] = member_email
        template_values['member_email_error'] = member_email_error
        template_values['member_email_error_message'] = member_email_error_messages[member_email_error]
        # Verification: reCAPTCHA
        challenge = request.POST['recaptcha_challenge_field']
        response_t  = request.POST['recaptcha_response_field']
        remoteip  = request.META['REMOTE_ADDR']

        cResponse = captcha.submit(
                         challenge,
                         response_t,
                         config.recaptcha_private_key,
                         remoteip)

        if cResponse.is_valid:
            logging.info('reCAPTCHA verification passed')
            template_values['recaptcha_error'] = 0
        else:
            errors = errors + 1
            error = cResponse.error_code
            template_values['recaptcha_error'] = 1
            template_values['recaptcha_error_message'] = '请重新输入 reCAPTCHA 验证码'

        template_values['errors'] = errors
        if (errors == 0):
            member = Member()
            q = Counter.objects.filter(name='member.max')
            if (len(q) == 1):
                counter = q[0]
                counter.value = counter.value + 1
            else:
                counter = Counter()
                counter.name = 'member.max'
                counter.value = 1
            q2 = Counter.objects.filter(name='member.total')
            if (len(q2) == 1):
                counter2 = q2[0]
                counter2.value = counter2.value + 1
            else:
                counter2 = Counter()
                counter2.name = 'member.total'
                counter2.value = 1

            user = User.objects.create_user(member_username, member_email.lower(), member_password)

            member.num = counter.value
            member.username_lower = member_username.lower()
            member.auth = hashlib.sha1(str(member.num) + ':' + user.password).hexdigest()
            member.l10n = site.l10n
            member.newbie = 1
            member.noob = 0
            if member.num == 1:
                member.level = 0
            else:
                member.level = 1000
            user.save()
            member.user = user
            member.save()
            counter.save()
            counter2.save()
            expire = datetime.datetime.now() + datetime.timedelta(days=365)
            expire_f = time.mktime(expire.timetuple())
            response.set_cookie("auth", member.auth, expire_f)
            memcache.delete('member_total')
            return HttpResponseRedirect('/')
        else:
            chtml = captcha.displayhtml(
                public_key = config.recaptcha_public_key,
                use_ssl = False,
                error = cResponse.error_code)
            template_values['captchahtml'] = chtml
            if browser['ios']:
                path = os.path.join('mobile', 'signup.html')
            else:
                path = os.path.join('desktop', 'signup.html')
            return render_to_response(path, template_values)

def SignoutHandler(request):
    if request.method == 'GET':
        logout(request)
        site = GetSite()
        browser = detect(request)
        member = False
        template_values = {}
        template_values['site'] = site
        template_values['page_title'] = site.title + u' › 登出'
        template_values['system_version'] = SYSTEM_VERSION
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if browser['ios']:
            path = os.path.join('mobile', 'signout.html')
        else:
            path = os.path.join('desktop', 'signout.html')
        return render_to_response(path, template_values)

def ForgotHandler(request):
    def get(self):
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['rnd'] = random.randrange(1, 100)
        template_values['site'] = site
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › 重新设置密码'
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'forgot.html')
        output = template.render(path, template_values)
        self.response.out.write(output)

    def post(self):
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['rnd'] = random.randrange(1, 100)
        template_values['site'] = site
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › 重新设置密码'
        # Verification: username & email
        username = self.request.get('username').strip().lower()
        email = self.request.get('email').strip().lower()
        q = db.GqlQuery("SELECT * FROM Member WHERE username_lower = :1 AND email = :2", username, email)
        if q.count() == 1:
            one = q[0]
            q2 = db.GqlQuery("SELECT * FROM PasswordResetToken WHERE timestamp > :1 AND email = :2", (int(time.time()) - 86400), email)
            if q2.count() > 2:
                error_message = '你不能在 24 小时内进行超过 2 次的密码重设操作。'
                template_values['errors'] = 1
                template_values['error_message'] = error_message
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'forgot.html')
                output = template.render(path, template_values)
                self.response.out.write(output)
            else:
                token = ''.join([str(random.randint(0, 9)) for i in range(32)])
                prt = PasswordResetToken()
                prt.token = token
                prt.member = one
                prt.email = one.email
                prt.timestamp = int(time.time())
                prt.put()
                mail_template_values = {}
                mail_template_values['site'] = site
                mail_template_values['one'] = one
                mail_template_values['host'] = self.request.headers['Host']
                mail_template_values['token'] = token
                mail_template_values['ua'] = self.request.headers['User-Agent']
                mail_template_values['ip'] = self.request.remote_addr
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'mail', 'reset_password.txt')
                output = template.render(path, mail_template_values)
                result = mail.send_mail(sender="v2ex.livid@me.com",
                              to=one.email,
                              subject="=?UTF-8?B?" + base64.b64encode((u"[" + site.title + u"] 重新设置密码").encode('utf-8')) + "?=",
                              body=output)
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'forgot_sent.html')
                output = template.render(path, template_values)
                self.response.out.write(output)
        else:
            error_message = '无法找到匹配的用户名和邮箱记录'
            template_values['errors'] = 1
            template_values['error_message'] = error_message
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'forgot.html')
            output = template.render(path, template_values)
            self.response.out.write(output)

def PasswordResetHandler(BaseHandler):
    def get(self, token):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        member = False
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        token = str(token.strip().lower())
        q = db.GqlQuery("SELECT * FROM PasswordResetToken WHERE token = :1 AND valid = 1", token)
        if q.count() == 1:
            prt = q[0]
            template_values['page_title'] = site.title + u' › 重新设置密码'
            template_values['token'] = prt
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'reset_password.html')
            output = template.render(path, template_values)
            self.response.out.write(output)
        else:
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'token_not_found.html')
            output = template.render(path, template_values)
            self.response.out.write(output)

    def post(self, token):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        member = False
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        token = str(token.strip().lower())
        q = db.GqlQuery("SELECT * FROM PasswordResetToken WHERE token = :1 AND valid = 1", token)
        if q.count() == 1:
            prt = q[0]
            template_values['page_title'] = site.title + u' › 重新设置密码'
            template_values['token'] = prt
            # Verification
            errors = 0
            new_password = str(self.request.get('new_password').strip())
            new_password_again = str(self.request.get('new_password_again').strip())
            if new_password is '' or new_password_again is '':
                errors = errors + 1
                error_message = '请输入两次新密码'
            if errors == 0:
                if new_password != new_password_again:
                    errors = errors + 1
                    error_message = '两次输入的新密码不一致'
            if errors == 0:
                if len(new_password) > 32:
                    errors = errors + 1
                    error_message = '新密码长度不能超过 32 个字符'
            if errors == 0:
                q2 = db.GqlQuery("SELECT * FROM Member WHERE num = :1", prt.member.num)
                one = q2[0]
                one.password = hashlib.sha1(new_password).hexdigest()
                one.auth = hashlib.sha1(str(one.num) + ':' + one.password).hexdigest()
                one.put()
                prt.valid = 0
                prt.put()
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'reset_password_ok.html')
                output = template.render(path, template_values)
                self.response.out.write(output)
            else:
                template_values['errors'] = errors
                template_values['error_message'] = error_message
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'reset_password.html')
                output = template.render(path, template_values)
                self.response.out.write(output)
        else:
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'token_not_found.html')
            output = template.render(path, template_values)
            self.response.out.write(output)

def NodeGraphHandler(request, node_name):
    if request.method == 'GET':
        print node_name
        site = GetSite()
        browser = detect(request)
        session = request.session
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        if member:
            template_values['member'] = member
        can_create = False
        can_manage = False
        if site.topic_create_level > 999:
            if member:
                can_create = True
        else:
            if member:
                if member.level <= site.topic_create_level:
                    can_create = True
        if member:
            if member.level == 0:
                can_manage = True
        template_values['can_create'] = can_create
        template_values['can_manage'] = can_manage
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        node = GetKindByName('Node', node_name)
        template_values['node'] = node
        if node:
            template_values['feed_link'] = '/feed/' + node.name + '.xml'
            template_values['feed_title'] = site.title + u' › ' + node.title
            template_values['canonical'] = 'http://' + site.domain + '/go/' + node.name
            if node.parent_node_name is None:
                siblings = []
            else:
                siblings = Node.objects.filter(parent_node_name=node.parent_node_name).exclude(name=node.name)
            template_values['siblings'] = siblings
            if member:
                favorited = member.hasFavorited(node)
                template_values['favorited'] = favorited
                recent_nodes = memcache.get('member::' + str(member.num) + '::recent_nodes')
                recent_nodes_ids = memcache.get('member::' + str(member.num) + '::recent_nodes_ids')
                if recent_nodes and recent_nodes_ids:
                    if (node.num in recent_nodes_ids) is not True:
                        recent_nodes.insert(0, node)
                        recent_nodes_ids.insert(0, node.num)
                        memcache.set('member::' + str(member.num) + '::recent_nodes', recent_nodes, 7200)
                        memcache.set('member::' + str(member.num) + '::recent_nodes_ids', recent_nodes_ids, 7200)
                else:
                    recent_nodes = []
                    recent_nodes.append(node)
                    recent_nodes_ids = []
                    recent_nodes_ids.append(node.num)
                    memcache.set('member::' + str(member.num) + '::recent_nodes', recent_nodes, 7200)
                    memcache.set('member::' + str(member.num) + '::recent_nodes_ids', recent_nodes_ids, 7200)
                template_values['recent_nodes'] = recent_nodes
            template_values['page_title'] = site.title + u' › ' + node.title
        else:
            template_values['page_title'] = site.title + u' › 节点未找到'
        section = False
        if node:
            section = GetKindByNum('Section', node.section_num)
        template_values['section'] = section
        if browser['ios']:
            if (node):
                path = os.path.join('mobile', 'node_graph.html')
            else:
                path = os.path.join('mobile', 'node_not_found.html')
        else:
            if (node):
                path = os.path.join('desktop', 'node_graph.html')
            else:
                path = os.path.join('desktop', 'node_not_found.html')
        return render_to_response(path, template_values)

def NodeHandler(request, node_name):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        session = request.session
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(request)
        if member:
            template_values['member'] = member
        can_create = False
        can_manage = False
        if site.topic_create_level > 999:
            if member:
                can_create = True
        else:
            if member:
                if member.level <= site.topic_create_level:
                    can_create = True
        if member:
            if member.level == 0:
                can_manage = True
        template_values['can_create'] = can_create
        template_values['can_manage'] = can_manage
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        node = GetKindByName('Node', node_name)
        template_values['node'] = node
        pagination = False
        pages = 1
        page = 1
        page_size = 15
        start = 0
        has_more = False
        more = 1
        has_previous = False
        previous = 1
        if node:
            template_values['feed_link'] = '/feed/' + node.name + '.xml'
            template_values['feed_title'] = site.title + u' › ' + node.title
            template_values['canonical'] = 'http://' + site.domain + '/go/' + node.name
            if member:
                favorited = member.hasFavorited(node)
                template_values['favorited'] = favorited
                recent_nodes = memcache.get('member::' + str(member.num) + '::recent_nodes')
                recent_nodes_ids = memcache.get('member::' + str(member.num) + '::recent_nodes_ids')
                if recent_nodes and recent_nodes_ids:
                    if (node.num in recent_nodes_ids) is not True:
                        recent_nodes.insert(0, node)
                        recent_nodes_ids.insert(0, node.num)
                        memcache.set('member::' + str(member.num) + '::recent_nodes', recent_nodes, 7200)
                        memcache.set('member::' + str(member.num) + '::recent_nodes_ids', recent_nodes_ids, 7200)
                else:
                    recent_nodes = []
                    recent_nodes.append(node)
                    recent_nodes_ids = []
                    recent_nodes_ids.append(node.num)
                    memcache.set('member::' + str(member.num) + '::recent_nodes', recent_nodes, 7200)
                    memcache.set('member::' + str(member.num) + '::recent_nodes_ids', recent_nodes_ids, 7200)
                template_values['recent_nodes'] = recent_nodes
            template_values['page_title'] = site.title + u' › ' + node.title
            # Pagination
            if node.topics > page_size:
                pagination = True
            else:
                pagination = False
            if pagination:
                if node.topics % page_size == 0:
                    pages = int(node.topics / page_size)
                else:
                    pages = int(node.topics / page_size) + 1
                page = request.GET['p']
                if (page == '') or (page is None):
                    page = 1
                else:
                    page = int(page)
                    if page > pages:
                        page = pages
                    else:
                        if page < 1:
                            page = 1
                if page < pages:
                    has_more = True
                    more = page + 1
                if page > 1:
                    has_previous = True
                    previous = page - 1
                start = (page - 1) * page_size
                template_values['canonical'] = 'http://' + site.domain + '/go/' + node.name + '?p=' + str(page)
        else:
            template_values['page_title'] = site.title + u' › 节点未找到'
        template_values['pagination'] = pagination
        template_values['pages'] = pages
        template_values['page'] = page
        template_values['page_size'] = page_size
        template_values['has_more'] = has_more
        template_values['more'] = more
        template_values['has_previous'] = has_previous
        template_values['previous'] = previous
        section = False
        if node:
            section = GetKindByNum('Section', node.section_num)
        template_values['section'] = section
        topics = False
        if node:
            q3 = Topic.objects.filter(node_num=node.num).order_by('-last_touched')[int(start):int(start)+int(page_size)]
            topics = q3
        template_values['latest'] = topics
        if browser['ios']:
            if (node):
                path = os.path.join('mobile', 'node.html')
            else:
                path = os.path.join('mobile', 'node_not_found.html')
        else:
            if (node):
                path = os.path.join('desktop', 'node.html')
            else:
                path = os.path.join('desktop', 'node_not_found.html')
        return render_to_response(path, template_values)

def NodeApiHandler(request):
    def get(self, node_name):
        site = GetSite()
        node = GetKindByName('Node', node_name)
        if node:
            template_values = {}
            template_values['site'] = site
            template_values['node'] = node
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api', 'node.json')
            self.response.headers['Content-type'] = 'application/json;charset=UTF-8'
            output = template.render(path, template_values)
            self.response.out.write(output)
        else:
            self.error(404)

def SearchHandler(request):
    def get(self, q):
        site = GetSite()
        q = urllib.unquote(q)
        template_values = {}
        template_values['site'] = site
        member = CheckAuth(request)
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › 搜索 ' + q.decode('utf-8')
        template_values['q'] = q
        if config.fts_enabled is not True:
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'search_unavailable.html')
            output = template.render(path, template_values)
            self.response.out.write(output)
        else:
            if re.findall('^([a-zA-Z0-9\_]+)$', q):
                node = GetKindByName('Node', q.lower())
                if node is not None:
                    template_values['node'] = node
            # Fetch result
            q_lowered = q.lower()
            q_md5 = hashlib.md5(q_lowered).hexdigest()
            topics = memcache.get('q::' + q_md5)
            if topics is None:
                try:
                    if os.environ['SERVER_SOFTWARE'] == 'Development/1.0':
                        fts = u'http://127.0.0.1:20000/search?q=' + str(urllib.quote(q_lowered))
                    else:
                        fts = u'http://' + config.fts_server + '/search?q=' + str(urllib.quote(q_lowered))
                    response = urlfetch.fetch(fts, headers = {"Authorization" : "Basic %s" % base64.b64encode(config.fts_username + ':' + config.fts_password)})
                    if response.status_code == 200:
                        results = json.loads(response.content)
                        topics = []
                        for num in results:
                            topics.append(GetKindByNum('Topic', num))
                        template_values['topics'] = topics
                        memcache.set('q::' + q_md5, topics, 86400)
                except:
                    template_values['topics'] = []
            else:
                template_values['topics'] = topics
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'search.html')
            output = template.render(path, template_values)
            self.response.out.write(output)

def DispatcherHandler(request):
    def post(self):
        referer = self.request.headers['Referer']
        q = self.request.get('q').strip()
        if len(q) > 0:
            self.redirect('/q/' + q)
        else:
            self.redirect(referer)

def RouterHandler(request):
    def get(self, path):
        if path.find('/') != -1:
            # Page
            parts = path.split('/')
            if len(parts) == 2:
                minisite_name = parts[0]
                if parts[1] == '':
                    page_name = 'index.html'
                else:
                    page_name = parts[1]
                minisite = GetKindByName('Minisite', minisite_name)
                if minisite is not False:
                    page = memcache.get(path)
                    if page is None:
                        q = db.GqlQuery("SELECT * FROM Page WHERE name = :1 AND minisite = :2", page_name, minisite)
                        if q.count() == 1:
                            page = q[0]
                            memcache.set(path, page, 864000)
                    if page.mode == 1:
                        # Dynamic embedded page
                        template_values = {}
                        site = GetSite()
                        template_values['site'] = site
                        member = CheckAuth(request)
                        if member:
                            template_values['member'] = member
                        l10n = GetMessages(member, site)
                        template_values['l10n'] = l10n
                        template_values['rnd'] = random.randrange(1, 100)
                        template_values['page'] = page
                        template_values['minisite'] = page.minisite
                        template_values['page_title'] = site.title + u' › ' + page.minisite.title.decode('utf-8') + u' › ' + page.title.decode('utf-8')
                        taskqueue.add(url='/hit/page/' + str(page.key()))
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'page.html')
                        output = template.render(path, template_values)
                        self.response.out.write(output)
                    else:
                        # Static standalone page
                        taskqueue.add(url='/hit/page/' + str(page.key()))
                        expires_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
                        expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
                        self.response.headers.add_header("Expires", expires_str)
                        self.response.headers['Cache-Control'] = 'max-age=864000, must-revalidate'
                        self.response.headers['Content-Type'] = page.content_type
                        self.response.out.write(page.content)
            else:
                minisite_name = parts[0]
                page_name = 'index.html'
                minisite = GetKindByName('Minisite', minisite_name)
                if minisite is not False:
                    page = memcache.get(path)
                    if page is None:
                        q = db.GqlQuery("SELECT * FROM Page WHERE name = :1 AND minisite = :2", page_name, minisite)
                        if q.count() == 1:
                            page = q[0]
                            memcache.set(path, page, 864000)
                    if page.mode == 1:
                        # Dynamic embedded page
                        template_values = {}
                        site = GetSite()
                        template_values['site'] = site
                        member = CheckAuth(request)
                        if member:
                            template_values['member'] = member
                        l10n = GetMessages(member, site)
                        template_values['l10n'] = l10n
                        template_values['rnd'] = random.randrange(1, 100)
                        template_values['page'] = page
                        template_values['minisite'] = page.minisite
                        template_values['page_title'] = site.title + u' › ' + page.minisite.title.decode('utf-8') + u' › ' + page.title.decode('utf-8')
                        taskqueue.add(url='/hit/page/' + str(page.key()))
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'page.html')
                        output = template.render(path, template_values)
                        self.response.out.write(output)
                    else:
                        # Static standalone page
                        taskqueue.add(url='/hit/page/' + str(page.key()))
                        expires_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
                        expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
                        self.response.headers.add_header("Expires", expires_str)
                        self.response.headers['Cache-Control'] = 'max-age=864000, must-revalidate'
                        self.response.headers['Content-Type'] = page.content_type
                        self.response.out.write(page.content)
        else:
            # Site
            page = memcache.get(path + '/index.html')
            if page:
                taskqueue.add(url='/hit/page/' + str(page.key()))
                if page.mode == 1:
                    # Dynamic embedded page
                    template_values = {}
                    site = GetSite()
                    template_values['site'] = site
                    member = CheckAuth(request)
                    if member:
                        template_values['member'] = member
                    l10n = GetMessages(member, site)
                    template_values['l10n'] = l10n
                    template_values['rnd'] = random.randrange(1, 100)
                    template_values['page'] = page
                    template_values['minisite'] = page.minisite
                    template_values['page_title'] = site.title + u' › ' + page.minisite.title.decode('utf-8') + u' › ' + page.title.decode('utf-8')
                    taskqueue.add(url='/hit/page/' + str(page.key()))
                    path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'page.html')
                    output = template.render(path, template_values)
                    self.response.out.write(output)
                else:
                    expires_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
                    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
                    self.response.headers.add_header("Expires", expires_str)
                    self.response.headers['Cache-Control'] = 'max-age=864000, must-revalidate'
                    self.response.headers['Content-Type'] = page.content_type
                    self.response.out.write(page.content)
            else:
                minisite_name = path
                minisite = GetKindByName('Minisite', minisite_name)
                q = db.GqlQuery("SELECT * FROM Page WHERE name = :1 AND minisite = :2", 'index.html', minisite)
                if q.count() == 1:
                    page = q[0]
                    memcache.set(path + '/index.html', page, 864000)
                    if page.mode == 1:
                        # Dynamic embedded page
                        template_values = {}
                        site = GetSite()
                        template_values['site'] = site
                        member = CheckAuth(request)
                        if member:
                            template_values['member'] = member
                        l10n = GetMessages(member, site)
                        template_values['l10n'] = l10n
                        template_values['rnd'] = random.randrange(1, 100)
                        template_values['page'] = page
                        template_values['minisite'] = page.minisite
                        template_values['page_title'] = site.title + u' › ' + page.minisite.title.decode('utf-8') + u' › ' + page.title.decode('utf-8')
                        taskqueue.add(url='/hit/page/' + str(page.key()))
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'page.html')
                        output = template.render(path, template_values)
                        self.response.out.write(output)
                    else:
                        # Static standalone page
                        taskqueue.add(url='/hit/page/' + str(page.key()))
                        expires_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
                        expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
                        self.response.headers.add_header("Expires", expires_str)
                        self.response.headers['Cache-Control'] = 'max-age=864000, must-revalidate'
                        self.response.headers['Content-Type'] = page.content_type
                        self.response.out.write(page.content)

def ChangesHandler(request):
    if request.method == 'GET':
        site = GetSite()
        browser = detect(request)
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        template_values['system_version'] = SYSTEM_VERSION
        template_values['page_title'] = site.title + u' › 全站最新更改记录'
        member = CheckAuth(request)
        template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n

        topic_total = memcache.get('topic_total')
        if topic_total is None:
            q2 = Counter.objects.filter(name='topic.total')
            if (len(q2) > 0):
                topic_total = q2[0].value
            else:
                topic_total = 0
            memcache.set('topic_total', topic_total, 600)
        template_values['topic_total'] = topic_total

        page_size = 60
        pages = 1
        if topic_total > page_size:
            if (topic_total % page_size) > 0:
                pages = int(math.floor(topic_total / page_size)) + 1
            else:
                pages = int(math.floor(topic_total / page_size))
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

        latest = memcache.get('q_changes_' + str(page_current))
        if (latest):
            template_values['latest'] = latest
        else:
            q1 = Topic.objects.filter().order_by('-last_touched')[int(page_start):int(page_start)+int(page_size)]
            topics = []
            for topic in q1:
                topics.append(topic)
            memcache.set('q_changes_' + str(page_current), topics, 120)
            template_values['latest'] = topics
            template_values['latest_total'] = len(topics)
        if browser['ios']:
            path = os.path.join('mobile', 'changes.html')
        else:
            path = os.path.join('desktop', 'changes.html')
        return render_to_response(path, template_values)


'''
def main():
    application = webapp.WSGIApplication([
    ('/', HomeHandler),
    ('/planes/?', PlanesHandler),
    ('/recent', RecentHandler),
    ('/ua', UAHandler),
    ('/signin', SigninHandler),
    ('/signup', SignupHandler),
    ('/signout', SignoutHandler),
    ('/forgot', ForgotHandler),
    ('/reset/([0-9]+)', PasswordResetHandler),
    ('/go/([a-zA-Z0-9]+)/graph', NodeGraphHandler),
    ('/go/([a-zA-Z0-9]+)', NodeHandler),
    ('/n/([a-zA-Z0-9]+).json', NodeApiHandler),
    ('/q/(.*)', SearchHandler),
    ('/_dispatcher', DispatcherHandler),
    ('/changes', ChangesHandler),
    ('/(.*)', RouterHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
'''
