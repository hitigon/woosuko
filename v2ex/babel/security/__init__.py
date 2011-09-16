# coding=utf-8

import os
import hashlib
import logging

from django.core.cache import cache as memcache
from iv2ex.models import Member

def CheckAuth(request):
    ip = GetIP(request)
    if request.user:
        member = Member.objects.filter(user__id__exact=request.user.id)
        if len(member)==1:
            member = member[0]
            member.ip = ip
            return member
        else:
            return False
    else:
        return False
    '''
    ip = GetIP(request)
    #cookies = Cookies(handler, max_age = 86400 * 365, path = '/')
    cookies = request.COOKIES
    if 'auth' in cookies:
        auth = cookies['auth']
        member_num = memcache.get(auth)
        if (member_num > 0):
            member = memcache.get('Member_' + str(member_num))
            if member is None:
                q = Member.objects.filter(num=member_num)
                if len(q) == 1:
                    member = q[0]
                    memcache.set('Member_' + str(member_num), member, 86400 * 365)
                else:
                    member = False
            if member:
                member.ip = ip
            return member
        else:
            q = Member.objects.filter(auth=auth)
            if (len(q) == 1):
                member_num = q[0].num
                member = q[0]
                memcache.set(auth, member_num, 86400 * 365)
                memcache.set('Member_' + str(member_num), member, 86400 * 365)
                member.ip = ip
                return member
            else:
                return False
    else:
        return False
    '''

def DoAuth(request, destination, message = None):
    if message != None:
        request.session['message'] = message
    else:
        request.session['message'] = u'请首先登入或注册'
    return request.redirect('/signin?destination=' + destination)

def GetIP(request):
    if 'X-Real-IP' in request.META:
        return request.META['X-Real-IP']
    else:
        return request.META['REMOTE_ADDR']