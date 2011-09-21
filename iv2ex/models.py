#coding=utf-8
'''
Created on 2011-9-12

@author: JohnQiao
'''

from django.db import models
from django.core.cache import cache as memcache
from django.contrib.auth.models import User
import datetime
import hashlib

class Member(models.Model):
    user = models.OneToOneField(User)

    username_editable = models.IntegerField(max_length=2, blank=True, default=1) # 1 editable  0 not editable

    num = models.IntegerField()
    auth = models.CharField(max_length=255, blank=False)
    deactivated = models.IntegerField(blank=False, default=0)
    username_lower = models.CharField(max_length=255, blank=True, default='')

    oldpassword = models.CharField(max_length=50, blank=True, default='')
    truename = models.CharField(max_length=255, blank=True, default='')
    sex = models.CharField(max_length=10, blank=True, default='')
    birthday = models.CharField(max_length=15, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')

    email_verified = models.IntegerField(blank=True, default=0)
    website = models.CharField(max_length=255, blank=True, default='')
    psn = models.CharField(max_length=255, blank=True, default='')
    
    twitter = models.CharField(max_length=255, blank=True, default='')
    twitter_oauth = models.IntegerField(blank=True, default=0)
    twitter_oauth_key = models.CharField(max_length=255, blank=True)
    twitter_oauth_secret = models.CharField(max_length=255, blank=True)
    twitter_oauth_string = models.CharField(max_length=255, blank=True)
    twitter_sync = models.IntegerField(blank=True, default=0)
    twitter_id = models.IntegerField(blank=True, null=True, default=0)
    twitter_name = models.CharField(max_length=255, blank=True)
    twitter_screen_name = models.CharField(max_length=255, blank=True)
    twitter_location = models.CharField(max_length=255, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_profile_image_url = models.CharField(max_length=255, blank=True)
    twitter_url = models.CharField(max_length=255, blank=True)
    twitter_statuses_count = models.IntegerField(blank=True, null=True, default=0)
    twitter_followers_count = models.IntegerField(blank=True, null=True, default=0)
    twitter_friends_count = models.IntegerField(blank=True, null=True, default=0)
    twitter_favourites_count = models.IntegerField(blank=True, null=True, default=0)

    use_my_css = models.IntegerField(blank=True, default=0)
    my_css = models.TextField(blank=True, default='')
    my_home = models.CharField(max_length=255, blank=True, null=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    tagline = models.TextField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    avatar_large_url = models.CharField(max_length=255, blank=True)
    avatar_normal_url = models.CharField(max_length=255, blank=True)
    avatar_mini_url = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_signin = models.DateTimeField(auto_now=True)
    blocked = models.TextField(blank=True, default='')
    l10n = models.CharField(max_length=255, default='en')
    favorited_nodes = models.IntegerField(blank=False, default=0)
    favorited_topics = models.IntegerField(blank=False, default=0)
    favorited_members = models.IntegerField(blank=False, default=0)
    followers_count = models.IntegerField(blank=False, default=0)
    level = models.IntegerField(blank=False, default=1000)
    notifications = models.IntegerField(blank=False, default=0)
    notification_position = models.IntegerField(blank=False, default=0)
    private_token = models.CharField(max_length=255, blank=True)
    ua = models.CharField(max_length=255, blank=True, default='')
    newbie = models.IntegerField(blank=False, default=0)
    noob = models.IntegerField(blank=False, default=0)
    show_home_top = models.IntegerField(blank=False, default=1)
    show_quick_post = models.IntegerField(blank=False, default=0)
    btc = models.CharField(max_length=255, blank=True, default='')

    def hasFavorited(self, something):
        if type(something).__name__ == 'Node':
            n = 'r/n' + str(something.num) + '/m' + str(self.num)
            r = memcache.get(n)
            if r:
                return r
            else:
                q = NodeBookmark.objects.filter(node=something, member=self)
                if len(q) > 0:
                    memcache.set(n, True, 86400 * 14)
                    return True
                else:
                    memcache.set(n, False, 86400 * 14)
                    return False
        else:
            if type(something).__name__ == 'Topic':
                n = 'r/t' + str(something.num) + '/m' + str(self.num)
                r = memcache.get(n)
                if r:
                    return r
                else:
                    q = TopicBookmark.objects.filter(topic=something, member=self)
                    if len(q) > 0:
                        memcache.set(n, True, 86400 * 14)
                        return True
                    else:
                        memcache.set(n, False, 86400 * 14)
                        return False
            else:
                if type(something).__name__ == 'Member':
                    n = 'r/m' + str(something.num) + '/m' + str(self.num)
                    r = memcache.get(n)
                    if r:
                        return r
                    else:
                        q = MemberBookmark.objects.filter(one=something, member_num=self.num)
                        if len(q) > 0:
                            memcache.set(n, True, 86400 * 14)
                            return True
                        else:
                            memcache.set(n, False, 86400 * 14)
                            return False
                else:
                    return False

class Counter(models.Model):
    name = models.CharField(max_length=255, blank=True)
    value = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    last_increased = models.DateTimeField(auto_now=True)

class Section(models.Model):
    num = models.IntegerField()
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    title_alternative = models.CharField(max_length=255, blank=True)
    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    nodes = models.IntegerField(default=0)
    created= models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class Node(models.Model):
    num = models.IntegerField()
    section_num = models.IntegerField()
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    title_alternative = models.CharField(max_length=255, blank=True)
    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    sidebar = models.TextField(blank=True)
    sidebar_ads = models.TextField(blank=True)
    category = models.CharField(max_length=255, blank=True)
    topics = models.IntegerField(default=0)
    parent_node_name = models.CharField(max_length=255, blank=True)
    avatar_large_url = models.CharField(max_length=255, blank=True)
    avatar_normal_url = models.CharField(max_length=255, blank=True)
    avatar_mini_url = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class Topic(models.Model):
    num = models.IntegerField()
    node = models.ForeignKey(Node)
    node_num = models.IntegerField()
    node_name = models.TextField(blank=True)
    node_title = models.TextField(blank=True)
    member = models.ForeignKey(Member)
    member_num = models.IntegerField()
    title = models.TextField(blank=True, )
    content = models.TextField(blank=True)
    content_rendered = models.TextField(blank=True)
    content_length = models.IntegerField(blank=False, default=0)
    has_content = models.BooleanField(blank=False, default=True)
    #has_image = models.BooleanField(blank=False, default=False)
    #preview_image = models.TextField()
    hits = models.IntegerField(default=0)
    stars = models.IntegerField(blank=False, default=0)
    replies = models.IntegerField(default=0)
    created_by = models.TextField(blank=True)
    last_reply_by = models.TextField(blank=True)
    source = models.TextField(blank=True)
    type = models.TextField(blank=True)
    type_color = models.TextField(blank=True)
    explicit = models.IntegerField(blank=False, default=0)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_touched = models.DateTimeField()

class Reply(models.Model):
    num = models.IntegerField()
    topic = models.ForeignKey(Topic)
    topic_num = models.IntegerField()
    member = models.ForeignKey(Member)
    member_num = models.IntegerField()
    content = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    created_by = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    highlighted = models.IntegerField(blank=False, default=0)

class Note(models.Model):
    num = models.IntegerField()
    member = models.ForeignKey(Member)
    member_num = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    body = models.TextField(blank=True)
    length = models.IntegerField(default=0)
    edits = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class PasswordResetToken(models.Model):
    token = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    member = models.ForeignKey(Member)
    valid = models.IntegerField(blank=True, default=1)
    timestamp = models.IntegerField(blank=True, default=0)

class Place(models.Model):
    num = models.IntegerField(blank=True)
    ip = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    visitors = models.IntegerField(blank=True, default=0)
    longitude = models.FloatField(blank=True, default=0.0)
    latitude = models.FloatField(blank=True, default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class PlaceMessage(models.Model):
    num = models.IntegerField()
    place = models.ForeignKey(Place)
    place_num = models.IntegerField()
    member = models.ForeignKey(Member)
    content = models.TextField(blank=True)
    #in_reply_to = models.ForeignKey(self.PlaceMessage)
    source = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class Checkin(models.Model):
    place = models.ForeignKey(Place)
    member = models.ForeignKey(Member)
    last_checked_in = models.DateTimeField(auto_now=True)

class Site(models.Model):
    num = models.IntegerField(blank=True)
    title = models.CharField(max_length=255, blank=True)
    slogan = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    domain = models.CharField(max_length=255, blank=True)
    analytics = models.CharField(max_length=255, blank=True)
    home_categories = models.TextField(blank=True)
    meta = models.TextField(blank=True, default='')
    home_top = models.TextField(blank=True, default='')
    theme = models.CharField(max_length=255, blank=True, default='default')
    l10n = models.CharField(max_length=255, default='en')
    use_topic_types = models.BooleanField(default=False)
    topic_types = models.TextField(default='')
    topic_view_level = models.IntegerField(blank=False, default=-1)
    topic_create_level = models.IntegerField(blank=False, default=1000)
    topic_reply_level = models.IntegerField(blank=False, default=1000)

class Minisite(models.Model):
    num = models.IntegerField(blank=True)
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(default='')
    pages = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class Page(models.Model):
    num = models.IntegerField(blank=True)
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    minisite = models.ForeignKey(Minisite)
    content = models.TextField(default='')
    content_rendered = models.TextField(default='')
    content_type = models.CharField(max_length=255, default='text/html')
    weight = models.IntegerField(blank=False, default=0)
    mode = models.IntegerField(blank=False, default=0)
    hits = models.IntegerField(blank=False, default=0)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class NodeBookmark(models.Model):
    node = models.ForeignKey(Node)
    member = models.ForeignKey(Member)
    created = models.DateTimeField(auto_now_add=True)

class TopicBookmark(models.Model):
    topic = models.ForeignKey(Topic)
    member = models.ForeignKey(Member)
    created = models.DateTimeField(auto_now_add=True)

class MemberBookmark(models.Model):
    one = models.ForeignKey(Member)
    member_num = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

# Notification type: mention_topic, mention_reply, reply
class Notification(models.Model):
    num = models.IntegerField(blank=True)
    member = models.ForeignKey(Member)
    for_member_num = models.IntegerField(blank=True)
    type = models.CharField(max_length=255, blank=True, )
    payload = models.TextField(blank=True, default='')
    label1 = models.CharField(max_length=255, blank=True)
    link1 = models.CharField(max_length=255, blank=True)
    label2 = models.CharField(max_length=255, blank=True)
    link2 = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class ITaskQueue(models.Model):
    data = models.TextField(blank=True, null=True, default='')
    lock = models.IntegerField(blank=True, null=True, default=0)
    date = models.DateTimeField(auto_now_add=True)

class KoreanGrammar(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, default='')
    content = models.TextField()