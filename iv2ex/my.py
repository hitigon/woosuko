#coding=utf-8
'''
Created on 11-9-14

@author: qiaoshun8888
'''
import os
import random
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from iv2ex.models import NodeBookmark, TopicBookmark, MemberBookmark, Topic
from v2ex.babel.da import GetSite
from v2ex.babel.l10n import GetMessages
from v2ex.babel.security import CheckAuth

def MyNodesHandler(request):
    if request.method == 'GET':
        member = CheckAuth(request)
        if member:
            site = GetSite()
            l10n = GetMessages(member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我收藏的节点'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_nodes > 0:
                template_values['has_nodes'] = True
                q = NodeBookmark.objects.filter(member=member).order_by('-created')[:10]
                template_values['column_1'] = q
                if member.favorited_nodes > 10:
                    q2 = NodeBookmark.objects.filter(member=member).order_by('-created')[10:10]
                    template_values['column_2'] = q2
            else:
                template_values['has_nodes'] = False
            path = os.path.join('desktop', 'my_nodes.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/')

def MyTopicsHandler(request):
    if request.method == 'GET':
        member = CheckAuth(request)
        if member:
            site = GetSite()
            l10n = GetMessages(member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我收藏的主题'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_topics > 0:
                template_values['has_topics'] = True
                q = TopicBookmark.objects.filter(member=member).order_by('-created')
                bookmarks = []
                for bookmark in q:
                    try:
                        topic = bookmark.topic
                        bookmarks.append(bookmark)
                    except:
                        bookmark.delete()
                template_values['bookmarks'] = bookmarks
            else:
                template_values['has_topics'] = False
            path = os.path.join('desktop', 'my_topics.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/')

def MyFollowingHandler(request):
    if request.method == 'GET':
        member = CheckAuth(request)
        if member:
            site = GetSite()
            l10n = GetMessages(member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我的特别关注'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_members > 0:
                template_values['has_following'] = True
                q = MemberBookmark.objects.filter(member_num=member.num).order_by('-created')
                template_values['following'] = q
                following = []
                for bookmark in q:
                    following.append(bookmark.one.num)
                q2 = Topic.objects.filter(member_num__in=following).order_by('-created')[:20]
                template_values['latest'] = q2
            else:
                template_values['has_following'] = False
            path = os.path.join('desktop', 'my_following.html')
            return render_to_response(path, template_values)
        else:
            return HttpResponseRedirect('/')

#def main():
#    application = webapp.WSGIApplication([
#    ('/my/nodes', MyNodesHandler),
#    ('/my/topics', MyTopicsHandler),
#    ('/my/following', MyFollowingHandler)
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()