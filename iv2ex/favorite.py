#coding=utf-8
'''
Created on 11-9-14

@author: qiaoshun8888
'''
from django.http import HttpResponseRedirect
from iv2ex.itaskqueue import ITaskQueueManage
from iv2ex.models import NodeBookmark, Member, TopicBookmark, MemberBookmark, Topic
from v2ex.babel.da import GetKindByName, GetKindByNum
from v2ex.babel.security import CheckAuth

from django.core.cache import cache as memcache


def FavoriteNodeHandler(request, node_name):
    if request.method == 'GET':
        if 'HTTP_REFERER' in request.META:
            go = request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(request)
        if member:
            node = GetKindByName('Node', node_name)
            if node is not False:
                q =NodeBookmark.objects.filter(node=node, member=member)
                if len(q) == 0:
                    bookmark = NodeBookmark()
                    bookmark.node = node
                    bookmark.member = member
                    bookmark.save()
                    member = Member.objects.get(id=member.id)
                    member.favorited_nodes = member.favorited_nodes + 1
                    member.save()
                    memcache.set('Member_' + str(member.num), member, 86400)
                    n = 'r/n' + str(node.num) + '/m' + str(member.num)
                    memcache.set(n, True, 86400 * 14)
        return HttpResponseRedirect(go)

def UnfavoriteNodeHandler(request, node_name):
    print node_name
    if request.method == 'GET':
        if 'HTTP_REFERER' in request.META:
            go = request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(request)
        if member:
            node = GetKindByName('Node', node_name)
            if node is not False:
                q = NodeBookmark.objects.filter(node=node, member=member)
                if len(q) > 0:
                    bookmark = q[0]
                    bookmark.delete()
                    member = Member.objects.get(id=member.id)
                    member.favorited_nodes = member.favorited_nodes - 1
                    member.save()
                    memcache.set('Member_' + str(member.num), member, 86400)
                    n = 'r/n' + str(node.num) + '/m' + str(member.num)
                    memcache.delete(n)
        return HttpResponseRedirect(go)

def FavoriteTopicHandler(request, topic_num):
    if request.method == 'GET':
        if 'HTTP_REFERER' in request.META:
            go = request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(request)
        if member:
            topic = GetKindByNum('Topic', int(topic_num))
            if topic is not False:
                q = TopicBookmark.objects.filter(topic=topic, member=member)
                if len(q) == 0:
                    bookmark = TopicBookmark()
                    bookmark.topic = topic
                    bookmark.member = member
                    bookmark.save()
                    member = Member.objects.get(id=member.id)
                    member.favorited_topics = member.favorited_topics + 1
                    member.save()
                    memcache.set('Member_' + str(member.num), member, 86400)
                    n = 'r/t' + str(topic.num) + '/m' + str(member.num)
                    memcache.set(n, True, 86400 * 14)
                    AddStarTopicHandler(topic.id)
        return HttpResponseRedirect(go)

def UnfavoriteTopicHandler(request, topic_num):
    if request.method == 'GET':
        if 'HTTP_REFERER' in request.META:
            go = request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(request)
        if member:
            topic = GetKindByNum('Topic', int(topic_num))
            if topic is not False:
                q = TopicBookmark.objects.filter(topic=topic, member=member)
                if len(q) > 0:
                    bookmark = q[0]
                    bookmark.delete()
                    member = Member.objects.get(id=member.id)
                    member.favorited_topics = member.favorited_topics - 1
                    member.save()
                    memcache.set('Member_' + str(member.num), member, 86400)
                    n = 'r/t' + str(topic.num) + '/m' + str(member.num)
                    memcache.delete(n)
                    MinusStarTopicHandler(topic.id)
        return HttpResponseRedirect(go)

def FollowMemberHandler(request, one_num):
    if request.method == 'GET':
        if 'HTTP_REFERER' in request.META:
            go = request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(request)
        if member:
            one = GetKindByNum('Member', int(one_num))
            if one is not False:
                if one.num != member.num:
                    q = MemberBookmark.objects.filter(one=one, member_num=member.num)
                    if len(q) == 0:
                        member = Member.objects.get(id=member.id)
                        member.favorited_members = member.favorited_members + 1
                        if member.favorited_members > 30:
                            session = request.session
                            session['message'] = '最多只能添加 30 位特别关注'
                        else:
                            bookmark = MemberBookmark()
                            bookmark.one = one
                            bookmark.member_num = member.num
                            bookmark.save()
                            member.save()
                            memcache.set('Member_' + str(member.num), member, 86400)
                            n = 'r/m' + str(one.num) + '/m' + str(member.num)
                            memcache.set(n, True, 86400 * 14)
                            one = Member.objects.get(id=one.id)
                            one.followers_count = one.followers_count + 1
                            one.save()
                            memcache.set('Member_' + str(one.num), one, 86400)
                            memcache.set('Member::' + str(one.username_lower), one, 86400)
                            session = request.session
                            session['message'] = '特别关注添加成功，还可以添加 ' + str(30 - member.favorited_members) + ' 位'
        return HttpResponseRedirect(go)

def UnfollowMemberHandler(request, one_num):
    if request.method == 'GET':
        if 'HTTP_REFERER' in request.META:
            go = request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(request)
        if member:
            one = GetKindByNum('Member', int(one_num))
            if one is not False:
                if one.num != member.num:
                    q = MemberBookmark.objects.filter(one=one, member_num=member.num)
                    if len(q) > 0:
                        bookmark = q[0]
                        bookmark.delete()
                        member = Member.objects.get(id=member.id)
                        member.favorited_members = member.favorited_members - 1
                        member.save()
                        memcache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/m' + str(one.num) + '/m' + str(member.num)
                        memcache.delete(n)
                        one = Member.objects.get(id=one.id)
                        one.followers_count = one.followers_count - 1
                        one.save()
                        memcache.set('Member_' + str(one.num), one, 86400)
                        memcache.set('Member::' + str(one.username_lower), one, 86400)
        return HttpResponseRedirect(go)

def AddStarTopicHandler(topic_id):
    topic = Topic.objects.get(id=topic_id)
    if topic:
        topic.stars = topic.stars + 1
        topic.save()
        memcache.set('Topic_' + str(topic.num), topic, 86400)

def MinusStarTopicHandler(topic_id):
    topic = Topic.objects.get(id=topic_id)
    if topic:
        topic.stars = topic.stars - 1
        if topic.stars < 0:
            topic.stars = 0
        topic.save()
        memcache.set('Topic_' + str(topic.num), topic, 86400)


#def main():
#    application = webapp.WSGIApplication([
#    ('/favorite/node/([a-zA-Z0-9]+)', FavoriteNodeHandler),
#    ('/unfavorite/node/([a-zA-Z0-9]+)', UnfavoriteNodeHandler),
#    ('/favorite/topic/([0-9]+)', FavoriteTopicHandler),
#    ('/unfavorite/topic/([0-9]+)', UnfavoriteTopicHandler),
#    ('/follow/([0-9]+)', FollowMemberHandler),
#    ('/unfollow/([0-9]+)', UnfollowMemberHandler)
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()