#coding=utf-8
'''
Created on 11-9-17

@intro: Based on Project Babel(V2EX) made by @Livid
@author: qiaoshun8888

'''
import logging
import os
import random
import datetime
from django.core.cache import cache as memcache
from django.http import HttpResponseRedirect
import time
from django.shortcuts import render_to_response
from iv2ex.models import Member
from twitter_api.oauth import OAuthToken
from twitter_api.oauthtwitter import OAuthApi
from v2ex.babel.da import GetKindByNum, GetSite
from v2ex.babel.l10n import GetMessages
from v2ex.babel.security import CheckAuth
import config


def TwitterLinkHandler(request):
    if request.method == 'GET':
        session = request.session
        member = CheckAuth(request)
        if member:
            twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret)
            request_token = twitter.getRequestToken()
            authorization_url = twitter.getAuthorizationURL(request_token)
            session['request_token'] = request_token
            return HttpResponseRedirect(authorization_url)
        else:
            return HttpResponseRedirect('/signin')

def TwitterUnlinkHandler(request):
    if request.method == 'GET':
        member = CheckAuth(request)
        if member:
            memcache.delete('Member_' + str(member.num))
            member = GetKindByNum('Member', member.num)
            member.twitter_oauth = 0
            member.twitter_oauth_key = ''
            member.twitter_oauth_secret = ''
            member.twitter_sync = 0
            member.save()
            memcache.set('Member_' + str(member.num), member, 86400)
            return HttpResponseRedirect('/settings')
        else:
            return HttpResponseRedirect('/signin')

def TwitterCallbackHandler(request):
    if request.method == 'GET':
        session = request.session
        member = CheckAuth(request)
        host = request.META['HTTP_HOST']
        if host == 'localhost:8000' or host == '127.0.0.1:8000':
            # Local debugging logic
            if member:
                request_token = session['request_token']
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, request_token)
                access_token = twitter.getAccessToken()
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, access_token)
                user = twitter.GetUserInfo()
                memcache.delete('Member_' + str(member.num))
                member = Member.objects.filter(num=member.num)[0]
                member.twitter_oauth = 1
                member.twitter_oauth_key = access_token.key
                member.twitter_oauth_secret = access_token.secret
                member.twitter_oauth_string = access_token.to_string()
                member.twitter_sync = 0
                member.twitter_id = user.id
                member.twitter_name = user.name
                member.twitter_screen_name = user.screen_name
                member.twitter_location = user.location
                member.twitter_description = user.description
                member.twitter_profile_image_url = user.profile_image_url
                member.twitter_url = user.url
                member.twitter_statuses_count = user.statuses_count
                member.twitter_followers_count = user.followers_count
                member.twitter_friends_count = user.friends_count
                member.twitter_favourites_count = user.favourites_count
                member.save()
                memcache.set('Member_' + str(member.num), member, 86400)
                return HttpResponseRedirect('/settings')
            else:
                return HttpResponseRedirect('/signin')
        else:
            # Remote production logic
            if member and 'request_token' in session:
                request_token = session['request_token']
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, request_token)
                access_token = twitter.getAccessToken()
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, access_token)
                user = twitter.GetUserInfo()
                memcache.delete('Member_' + str(member.num))
                member = Member.objects.filter(num=member.num)[0]
                member.twitter_oauth = 1
                member.twitter_oauth_key = access_token.key
                member.twitter_oauth_secret = access_token.secret
                member.twitter_oauth_string = access_token.to_string()
                member.twitter_sync = 0
                member.twitter_id = user.id
                member.twitter_name = user.name
                member.twitter_screen_name = user.screen_name
                member.twitter_location = user.location
                member.twitter_description = user.description
                member.twitter_profile_image_url = user.profile_image_url
                member.twitter_url = user.url
                member.twitter_statuses_count = user.statuses_count
                member.twitter_followers_count = user.followers_count
                member.twitter_friends_count = user.friends_count
                member.twitter_favourites_count = user.favourites_count
                member.save()
                memcache.set('Member_' + str(member.num), member, 86400)
                return HttpResponseRedirect('/settings')
            else:
                oauth_token = request.GET['oauth_token']
                if host == 'www.woosuko.com':
                    return HttpResponseRedirect('http://www.woosuko.com/twitter-oauth?oauth_token=' + oauth_token)
                else:
                    return HttpResponseRedirect('http://localhost:8000/twitter-oauth?oauth_token=' + oauth_token)

def TwitterHomeHandler(request):
    if request.method == 'GET':
        site = GetSite()
        member = CheckAuth(request)
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › Home'
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, access_token)
                rate_limit = memcache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        memcache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'member::' + str(member.num) + '::twitter::home'
                statuses = memcache.get(cache_tag)
                if statuses is None:
                    statuses = twitter.GetHomeTimeline(count = 50)
                    i = 0;
                    for status in statuses:
                        statuses[i].source = statuses[i].source.replace('<a', '<a def="dark"')
                        statuses[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        statuses[i].text = twitter.ConvertMentions(status.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    memcache.set(cache_tag, statuses, 120)
                template_values['statuses'] = statuses
                path = os.path.join('desktop', 'twitter_home.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/settings')
        else:
            return HttpResponseRedirect('/')

def TwitterMentionsHandler(request):
    if request.method == 'GET':
        site = GetSite()
        member = CheckAuth(request)
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › Mentions'
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, access_token)
                rate_limit = memcache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        memcache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'member::' + str(member.num) + '::twitter::mentions'
                statuses = memcache.get(cache_tag)
                if statuses is None:
                    statuses = twitter.GetReplies()
                    i = 0;
                    for status in statuses:
                        statuses[i].source = statuses[i].source.replace('<a', '<a def="dark"')
                        statuses[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        statuses[i].text = twitter.ConvertMentions(status.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    memcache.set(cache_tag, statuses, 120)
                template_values['statuses'] = statuses
                path = os.path.join('desktop', 'twitter_mentions.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/settings')
        else:
            return HttpResponseRedirect('/')

def TwitterDMInboxHandler(request):
    if request.method == 'GET':
        member = CheckAuth(request)
        site = GetSite()
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › Direct Messages › Inbox'
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, access_token)
                rate_limit = memcache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        memcache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'member::' + str(member.num) + '::twitter::dm::inbox'
                messages = memcache.get(cache_tag)
                if messages is None:
                    messages = twitter.GetDirectMessages()
                    i = 0;
                    for message in messages:
                        messages[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(message.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        messages[i].text = twitter.ConvertMentions(message.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    memcache.set(cache_tag, messages, 120)
                template_values['messages'] = messages
                path = os.path.join('desktop', 'twitter_dm_inbox.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/settings')
        else:
            return HttpResponseRedirect('/')

def TwitterUserTimelineHandler(request, screen_name):
    if request.method == 'GET':
        site = GetSite()
        member = CheckAuth(request)
        if member:
            if member.twitter_oauth == 1:
                template_values = {}
                template_values['site'] = site
                template_values['rnd'] = random.randrange(1, 100)
                template_values['member'] = member
                l10n = GetMessages(member, site)
                template_values['l10n'] = l10n
                template_values['page_title'] = site.title + u' › Twitter › ' + screen_name
                template_values['screen_name'] = screen_name
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, access_token)
                rate_limit = memcache.get(str(member.twitter_id) + '::rate_limit')
                if rate_limit is None:
                    try:
                        rate_limit = twitter.GetRateLimit()
                        memcache.set(str(member.twitter_id) + '::rate_limit', rate_limit, 60)
                    except:
                        logging.info('Failed to get rate limit for @' + member.twitter_screen_name)
                template_values['rate_limit'] = rate_limit
                cache_tag = 'twitter::' + screen_name + '::home'
                statuses = memcache.get(cache_tag)
                if statuses is None:
                    statuses = twitter.GetUserTimeline(user=screen_name, count = 50)
                    i = 0;
                    for status in statuses:
                        statuses[i].source = statuses[i].source.replace('<a', '<a def="dark"')
                        statuses[i].datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y')))
                        statuses[i].text = twitter.ConvertMentions(status.text)
                        #statuses[i].text = twitter.ExpandBitly(status.text)
                        i = i + 1
                    memcache.set(cache_tag, statuses, 120)
                template_values['statuses'] = statuses
                path = os.path.join('desktop', 'twitter_user.html')
                return render_to_response(path, template_values)
            else:
                return HttpResponseRedirect('/settings/')
        else:
            return HttpResponseRedirect('/')

def TwitterTweetHandler(request):
    if request.method == 'POST':
        if 'HTTP_REFERER' in request.META:
            go = request.META['HTTP_REFERER']
        else:
            go = '/'
        member = CheckAuth(request)
        if member:
            if member.twitter_oauth == 1:
                status = request.POST['status']
                if len(status) > 140:
                    status = status[0:140]
                access_token = OAuthToken.from_string(member.twitter_oauth_string)
                twitter = OAuthApi(config.twitter_consumer_key, config.twitter_consumer_secret, access_token)
                try:
                    twitter.PostUpdate(status.encode('utf-8'))
                    memcache.delete('member::' + str(member.num) + '::twitter::home')
                except:
                    logging.error('Failed to tweet: ' + status)
                return HttpResponseRedirect(go)
            else:
                return HttpResponseRedirect('/twitter/link/')
        else:
            return HttpResponseRedirect('/')

def TwitterApiCheatSheetHandler(request):
    if request.method == 'GET':
        template_values = {}
        path = os.path.join('desktop', 'twitter_api_cheat_sheet.html')
        return render_to_response(path, template_values)

def main():
    application = webapp.WSGIApplication([
    ('/twitter/?', TwitterHomeHandler),
    ('/twitter/mentions/?', TwitterMentionsHandler),
    ('/twitter/inbox/?', TwitterDMInboxHandler),
    ('/twitter/user/([a-zA-Z0-9\_]+)', TwitterUserTimelineHandler),
    ('/twitter/link', TwitterLinkHandler),
    ('/twitter/unlink', TwitterUnlinkHandler),
    ('/twitter-oauth/', TwitterCallbackHandler),
    ('/twitter/tweet', TwitterTweetHandler),
    ('/twitter/api/?', TwitterApiCheatSheetHandler)
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()