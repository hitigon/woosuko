# coding=utf-8
# "da" means Data Access, this file contains various quick (or dirty) methods for accessing data.

import hashlib
import logging
import zlib
import pickle

from django.core.cache import cache as memcache
from iv2ex.models import Site, Node, Section, Member, Place, Counter, Minisite, Topic

def GetKindByNum(kind, num):
    K = str(kind.capitalize())
    one = memcache.get(K + '_' + str(num))
    if one:
        return one
    else:
        q = None
        if K.lower() == 'section':
            q = Section.objects.filter(num=int(num))
        elif K.lower() == 'node':
            q = Node.objects.filter(num=int(num))
        elif K.lower() == 'topic':
            q = Topic.objects.filter(num=int(num))
        elif K.lower() == 'member':
            q = Member.objects.filter(num=int(num))
        if len(q) == 1:
            one = q[0]
            memcache.set(K + '_' + str(num), one, 86400)
            return one
        else:
            return False
            
def GetKindByName(kind, name):
    K = str(kind.capitalize())
    one = memcache.get(K + '::' + str(name))
    if one:
        return one
    else:
        q = None
        if K.lower() == 'node':
            q = Node.objects.filter(name=str(name))
        elif K.lower() == 'minisite':
            q = Minisite.objects.filter(name=str(name))
        elif K.lower() == 'section':
            q = Section.objects.filter(name=str(name))

        if len(q) == 1:
            one = q[0]
            memcache.set(K + '::' + str(name), one, 86400)
            return one
        else:
            return False

def GetMemberByUsername(name):
    one = memcache.get('Member::' + str(name).lower())
    if one:
        return one
    else:
        q = Member.objects.filter(username_lower=str(name).lower())
        if len(q) == 1:
            one = q[0]
            memcache.set('Member::' + str(name).lower(), one, 86400)
            return one
        else:
            return False

def GetMemberByEmail(email):
    cache = 'Member::email::' + hashlib.md5(email.lower()).hexdigest()
    one = memcache.get(cache)
    if one:
        return one
    else:
        q = db.GqlQuery("SELECT * FROM Member WHERE email = :1", str(email).lower())
        if q.count() == 1:
            one = q[0]
            memcache.set(cache, one, 86400)
            return one
        else:
            return False

def ip2long(ip):
    ip_array = ip.split('.')
    ip_long = int(ip_array[0]) * 16777216 + int(ip_array[1]) * 65536 + int(ip_array[2]) * 256 + int(ip_array[3])
    return ip_long

def GetPlaceByIP(ip):
    cache = 'Place_' + ip
    place = memcache.get(cache)
    if place:
        return place
    else:
        q = Place.objects.filter(ip=ip)
        if len(q) == 1:
            place = q[0]
            memcache.set(cache, place, 86400)
            return place
        else:
            return False

def CreatePlaceByIP(ip):
    place = Place()
    q = Counter.objects.filter(name='place.max')
    if (len(q) == 1):
        counter = q[0]
        counter.value = counter.value + 1
    else:
        counter = Counter()
        counter.name = 'place.max'
        counter.value = 1
    q2 = Counter.objects.filter(name='place.total')
    if (len(q2) == 1):
        counter2 = q2[0]
        counter2.value = counter2.value + 1
    else:
        counter2 = Counter()
        counter2.name = 'place.total'
        counter2.value = 1
    place.num = ip2long(ip)
    place.ip = ip
    place.save()
    counter.save()
    counter2.save()
    return place

def GetSite():
    site = memcache.get('site')
    if site is not None:
        return site
    else:
        q = Site.objects.filter(num=1)
        if len(q) == 1:
            site = q[0]
            if site.l10n is None:
                site.l10n = 'en'
            if site.meta is None:
                site.meta = ''
            memcache.set('site', site, 86400)
            return site
        else:
            site = Site()
            site.num = 1
            site.title = 'iV2EX'
            site.domain = 'iv2ex.com'
            site.slogan = 'way to explore'
            site.l10n = 'en'
            site.description = ''
            site.meta = ''
            site.save()
            memcache.set('site', site, 86400)
            return site

# input is a compressed string
# output is an object
def GetUnpacked(data):
    decompressed = zlib.decompress(data)
    return pickle.loads(decompressed)

# input is an object
# output is an compressed string
def GetPacked(data):
    s = pickle.dumps(data)
    return zlib.compress(s)