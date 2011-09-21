#coding=utf-8
'''
Created on 11-9-13

@author: qiaoshun8888
'''
import hashlib
import os
import re
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.html import escape
from iv2ex import config, SYSTEM_VERSION
from iv2ex.models import Topic, Counter, Notification
from v2ex.babel.da import GetMemberByUsername, GetSite

from django.core.cache import cache as memcache
from v2ex.babel.l10n import GetMessages
from v2ex.babel.security import CheckAuth
from v2ex.babel.ua import detect

def NotificationsHandler(request):
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
        if member:
            template_values['member'] = member
            if member.private_token is None:
                member.private_token = hashlib.sha256(str(member.num) + ';' + config.site_key).hexdigest()
                member.save()
            notifications = memcache.get('nn::' + member.username_lower)
            if notifications is None:
                q = Notification.objects.filter(for_member_num=member.num).order_by('-num')[:50]
                notifications = []
                i = 0
                for n in q:
                    if i == 0:
                        if member.notification_position != n.num:
                            member.notification_position = n.num
                            member.save()
                    if n.type == 'reply':
                        n.text = u'<a href="/member/' + n.member.user.username + u'"><strong>' + n.member.user.username + u'</strong></a> 在 <a href="' + n.link1 + '">' + escape(n.label1) + u'</a> 里回复了你'
                        notifications.append(n)
                    if n.type == 'mention_reply':
                        n.text = u'<a href="/member/' + n.member.user.username + u'"><strong>' + n.member.user.username + u'</strong></a> 在回复 <a href="' + n.link1 + '">' + escape(n.label1) + u'</a> 时提到了你'
                        notifications.append(n)
                    if n.type == 'mention_topic':
                        n.text = u'<a href="/member/' + n.member.user.username + u'"><strong>' + n.member.user.username + u'</strong></a> 在创建主题 <a href="' + n.link1 + '">' + escape(n.label1) + u'</a> 时提到了你'
                        notifications.append(n)
                    if n.type == 'follow':
                        n.text = u'<a href="/member/' + n.member.user.username + u'"><strong>' + n.member.user.username + u'</strong></a> 关注了你'
                        notifications.append(n)
                    i = i + 1
                member.notifications = 0
                member.save()
                memcache.set('Member_' + str(member.num), member, 86400)
                memcache.set('nn::' + member.username_lower, notifications, 360)
            template_values['notifications'] = notifications
            template_values['title'] = u'提醒系统'
            path = os.path.join('desktop', 'notifications.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/signin')

def NotificationsFeedHandler(request):
    def head(self, private_token):
        pass

    def get(self, private_token):
        n = memcache.get('n_' + private_token)
        if n is not None:
            self.values['notification'] = n
            self.response.headers['Content-type'] = 'application/xml;charset=UTF-8'
            self.values['member'] = self.member
            self.finalize(template_name='notifications', template_root='feed', template_type='xml')
        else:
            q = db.GqlQuery("SELECT * FROM Member WHERE private_token = :1", private_token)
            count = q.count()
            if count > 0:
                member = q[0]
                q = db.GqlQuery("SELECT * FROM Notification WHERE for_member_num = :1 ORDER BY num DESC LIMIT 50", member.num)
                notifications = []
                i = 0
                for n in q:
                    if n.type == 'reply':
                        n.title = u'' + n.member.user.username + u' 在 ' + self.escape(n.label1) + u' 里回复了你'
                        n.text = u'<a href="/member/' + n.member.user.username + u'"><strong>' + n.member.user.username + u'</strong></a> 在 <a href="' + n.link1 + '">' + self.escape(n.label1) + u'</a> 里回复了你'
                        notifications.append(n)
                    if n.type == 'mention_reply':
                        n.title = u'' + n.member.user.username + u' 在回复 ' + self.escape(n.label1) + u' 时提到了你'
                        n.text = u'<a href="/member/' + n.member.user.username + u'"><strong>' + n.member.user.username + u'</strong></a> 在回复 <a href="' + n.link1 + '">' + self.escape(n.label1) + u'</a> 时提到了你'
                        notifications.append(n)
                    i = i + 1
                self.values['notifications'] = notifications
                memcache.set('n_' + private_token, notifications, 600)
                self.response.headers['Content-type'] = 'application/xml;charset=UTF-8'
                self.values['member'] = member
                self.finalize(template_name='notifications', template_root='feed', template_type='xml')

#def main():
#    application = webapp.WSGIApplication([
#    ('/notifications/?', NotificationsHandler),
#    ('/notifications/check/(.+)', NotificationsCheckHandler),
#    ('/notifications/reply/(.+)', NotificationsReplyHandler),
#    ('/notifications/topic/(.+)', NotificationsTopicHandler),
#    ('/n/([a-z0-9]+).xml', NotificationsFeedHandler)
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    ma