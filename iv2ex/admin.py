#coding=utf-8
'''
Created on 11-9-12

@author: qiaoshun8888
'''

from django.contrib import admin

from iv2ex.models import Site, Topic
from iv2ex.models import Member
from iv2ex.models import Node, ITaskQueue, Notification

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'num', 'title', 'slogan', 'description')

class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'num', 'section_num', 'name', 'title')

class ITaskQueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'lock', 'date')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'payload', 'created')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


admin.site.register(Member, MemberAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(ITaskQueue, ITaskQueueAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Topic, TopicAdmin)