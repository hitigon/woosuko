#coding=utf-8
'''
Created on 11-9-13

@author: qiaoshun8888
'''
import re
import threading
import time
import sys
import datetime
from iv2ex.mail import send_register_email
from iv2ex.models import ITaskQueue, Topic, Page, Counter, Notification, Member, Reply
from v2ex.babel.da import GetMemberByUsername, GetKindByNum
from django.core.cache import cache as memcache

class ITaskID():
    NOTIFICATION_TOPIC = '/notifications/topic/'
    NOTIFICATION_REPLY = '/notifications/reply/'
    NOTIFICATION_CHECH = '/notifications/check/'
    REGISTER_EMAIL = '/register/mail/'

class ITaskQueueManage():

    def add(self, data=''):
        task = ITaskQueue()
        task.data = data
        task.lock = 0
        task.date = datetime.datetime.now()
        task.save()

class ITaskQueueThread(threading.Thread):
    
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval # 秒
        self.thread_stop = False

    def run(self):
        while not self.thread_stop:
            try:
                #print 'running....'
                ''' update() 更新结果集的缓存 '''
                ITaskQueue.objects.update()
                tasklist = ITaskQueue.objects.filter(lock=0)
                for task in tasklist:
                    # 判断当前任务是否处于锁定状态
                    if task.lock == 1:
                        continue;
                    # 不处于锁定状态则执行该任务，首先给当前任务加锁
                    task.lock = 1
                    task.save()
                    # 执行任务
                    if task.data.find(ITaskID.NOTIFICATION_TOPIC) != -1:
                        topic_id = int(task.data.replace(ITaskID.NOTIFICATION_TOPIC,''))
                        Task_NotificationsTopicHandler(topic_id)
                    elif task.data.find(ITaskID.NOTIFICATION_REPLY) != -1:
                        reply_id = int(task.data.replace(ITaskID.NOTIFICATION_REPLY,''))
                        Task_NotificationsReplyHandler(reply_id)
                    elif task.data.find(ITaskID.NOTIFICATION_CHECH) != -1:
                        check_id = int(task.data.replace(ITaskID.NOTIFICATION_CHECH,''))
                        Task_NotificationsCheckHandler(check_id)
                    elif task.data.find(ITaskID.REGISTER_EMAIL) != -1:
                        user_data = task.data.replace(ITaskID.REGISTER_EMAIL,'').split('###') # email | username | password
                        send_register_email(user_data[0], user_data[1], user_data[2])
                    else:
                        pass
                    # 执行完任务后删除
                    task.delete()
            except:
                print "itaskqueue.py error:" + str(sys.exc_info())
            time.sleep(self.interval)

    def stop(self):
        self.thread_stop = True

# ============================================================================================

# For mentions in topic title and content
def Task_NotificationsTopicHandler(topic_id):
        topic = Topic.objects.get(id=topic_id)
        combined = topic.title + " " + topic.content
        ms = re.findall('(@[a-zA-Z0-9\_]+\.?)\s?', combined)
        keys = []
        if (len(ms) > 0):
            for m in ms:
                m_id = re.findall('@([a-zA-Z0-9\_]+\.?)', m)
                if (len(m_id) > 0):
                    if (m_id[0].endswith('.') != True):
                        member_username = m_id[0]
                        member = GetMemberByUsername(member_username)
                        if member:
                            if member.id != topic.member.id and member.id not in keys:
                                q = Counter.objects.filter(name='notification.max')
                                if (len(q) == 1):
                                    counter = q[0]
                                    counter.value = counter.value + 1
                                else:
                                    counter = Counter()
                                    counter.name = 'notification.max'
                                    counter.value = 1
                                q2 = Counter.objects.filter(name='notification.total')
                                if (len(q2) == 1):
                                    counter2 = q2[0]
                                    counter2.value = counter2.value + 1
                                else:
                                    counter2 = Counter()
                                    counter2.name = 'notification.total'
                                    counter2.value = 1

                                notification = Notification()
                                notification.num = counter.value
                                notification.type = 'mention_topic'
                                notification.payload = topic.content
                                notification.label1 = topic.title
                                notification.link1 = '/t/' + str(topic.num) + '#reply' + str(topic.replies)
                                notification.member = topic.member
                                notification.for_member_num = member.num

                                keys.append(member.id)

                                counter.save()
                                counter2.save()
                                notification.save()
        ITQM = ITaskQueueManage()
        for k in keys:
            ITQM.add(data='/notifications/check/' + str(k))

# For mentions in reply content
def Task_NotificationsReplyHandler(reply_id):
    try:
        reply = Reply.objects.get(id=reply_id)
        topic = GetKindByNum('Topic', reply.topic_num)
        ms = re.findall('(@[a-zA-Z0-9\_]+\.?)\s?', reply.content)
        keys = []
        if (len(ms) > 0):
            for m in ms:
                m_id = re.findall('@([a-zA-Z0-9\_]+\.?)', m)
                if (len(m_id) > 0):
                    if (m_id[0].endswith('.') != True):
                        member_username = m_id[0]
                        member = GetMemberByUsername(member_username)
                        if member:
                            if member.id != topic.member.id and member.id != reply.member.id and member.id not in keys:
                                q = Counter.objects.filter(name='notification.max')
                                if (len(q) == 1):
                                    counter = q[0]
                                    counter.value = counter.value + 1
                                else:
                                    counter = Counter()
                                    counter.name = 'notification.max'
                                    counter.value = 1
                                q2 = Counter.objects.filter(name='notification.total')
                                if (len(q2) == 1):
                                    counter2 = q2[0]
                                    counter2.value = counter2.value + 1
                                else:
                                    counter2 = Counter()
                                    counter2.name = 'notification.total'
                                    counter2.value = 1

                                notification = Notification()
                                notification.num = counter.value
                                notification.type = 'mention_reply'
                                notification.payload = reply.content
                                notification.label1 = topic.title
                                notification.link1 = '/t/' + str(topic.num) + '#reply' + str(topic.replies)
                                notification.member = reply.member
                                notification.for_member_num = member.num

                                keys.append(member.id)

                                counter.save()
                                counter2.save()
                                notification.save()
        ITQM = ITaskQueueManage()
        for k in keys:
            ITQM.add(data='/notifications/check/' + str(k))
    except :
        print "itaskqueue.py - Task_NotificationsReplyHandler error:" + str(sys.exc_info())

def Task_NotificationsCheckHandler(member_id):
    member = Member.objects.get(id=int(member_id))
    if member:
        if member.notification_position is None:
            member.notification_position = 0
        q = Notification.objects.filter(for_member_num=member.num,num__gt=member.notification_position).order_by('-num')
        count = len(q)
        if count > 0:
            member.notifications = count
            member.save()
            memcache.set('Member_' + str(member.num), member, 86400)