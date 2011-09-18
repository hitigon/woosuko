#coding=utf-8
'''
Created on 11-9-15

@author: qiaoshun8888
'''
import hashlib
import os

import sys
import MySQLdb
import datetime
from django.contrib.auth.models import User
import time
from django.template.context import Context
from django.template.loader import get_template
from iv2ex.models import Member, Counter, Node, Section, Topic
from v2ex.babel.da import GetSite

reload(sys)
sys.setdefaultencoding('utf-8')

'''
    韩语学习 1215
'''
def getdata2 ():
    print 'getdata2() is running ...'
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='sacn', port=3306, charset='utf8')
        try:
            conn.ping(True)
            cur = conn.cursor()
            sql = r'select * from publish where publisherid=1215 and id>0'
            cur.execute(sql)
            allPerson = cur.fetchall()
        finally:
            cur.close()
            conn.close()


        for rec in allPerson:
            member = Member.objects.get(id=1208) # 1208 韩语学习  # 1151 七彩路
            id = int(rec[0])
            print "id: " + str(id)
#            if id>987 or id<740:
#                continue
            topic_title = rec[3]
            topic_content = rec[4]

            q = Node.objects.filter(name="korean_life")
            node = q[0]
            topic = Topic()
            topic.node = node
            q = Counter.objects.filter(name='topic.max')
            if (len(q) == 1):
                counter = q[0]
                counter.value = counter.value + 1
            else:
                counter = Counter()
                counter.name = 'topic.max'
                counter.value = 1
            q2 = Counter.objects.filter(name='topic.total')
            if (len(q2) == 1):
                counter2 = q2[0]
                counter2.value = counter2.value + 1
            else:
                counter2 = Counter()
                counter2.name = 'topic.total'
                counter2.value = 1
            topic.num = counter.value
            topic.title = topic_title
            topic.content = topic_content
            topic.content_rendered = topic_content
            if len(topic_content) > 0:
                topic.has_content = True
                topic.content_length = len(topic_content)
            else:
                topic.has_content = False
            topic.node = node
            topic.node_num = node.num
            topic.node_name = node.name
            topic.node_title = node.title
            topic.created_by = member.user.username
            topic.member = member
            topic.member_num = member.num
            topic.last_touched = datetime.datetime.now()
            topic.has_content = 1
            node.topics = node.topics + 1
            node.save()
            topic.save()
            counter.save()
            counter2.save()
            # Change newbie status?
            if member.newbie == 1:
                now = datetime.datetime.now()
                created = member.created
                diff = now - created
                if diff.seconds > (86400 * 60):
                    member.newbie = 0
                    member.save()
    #        break
    except Exception, e:
        print '数据库错误:', e
        return

if __name__ == '__main__':
    getdata2()