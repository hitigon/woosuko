#coding=utf-8
'''
Created on 11-9-15

@author: qiaoshun8888
'''
import hashlib

import sys
import MySQLdb
import datetime
from django.contrib.auth.models import User
import time
from iv2ex.models import Member, Counter
from v2ex.babel.da import GetSite

reload(sys)
sys.setdefaultencoding('utf-8')

def getdata ():
    print 'getdata() is running ...'
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='sacn', port=3306, charset='utf8')
        try:
            cur = conn.cursor()
            sql = r'select * from user'
            cur.execute(sql)
            allPerson = cur.fetchall()
        finally:
            cur.close()
            conn.close()
    except Exception, e:
        print '数据库错误:', e
        return

    PASSWORD = 'woosuko.com'
    site = GetSite()

    for rec in allPerson:
        id = int(rec[0])
        print "id: " + str(id)
        if id==1469 or id==1440 or id==1439 or id==1432 or id==1374 or id==1281 or id==1248 or id==1239 or id==1159 or id== 1147 or id == 1061:
            continue
        member_username = rec[1]
        member_email = rec[2]
        member_oldpassword = rec[4]
        if not member_username:
            member_username = ''
        if not member_email:
            member_email = ''
        if len(member_username)==0 and len(member_email)==0:
            continue
        if len(member_username)==0 and len(member_email)!=0:
            member_username = member_email.split('@')[0]
        truename = rec[8]
        sex = rec[9]
        birthday = rec[10]
        phone = rec[21]
        #print rec[0],rec[1]
        member = Member()
        q = Counter.objects.filter(name='member.max')
        if (len(q) == 1):
            counter = q[0]
            counter.value = counter.value + 1
        else:
            counter = Counter()
            counter.name = 'member.max'
            counter.value = 1
        q2 = Counter.objects.filter(name='member.total')
        if (len(q2) == 1):
            counter2 = q2[0]
            counter2.value = counter2.value + 1
        else:
            counter2 = Counter()
            counter2.name = 'member.total'
            counter2.value = 1

        user = User.objects.create_user(member_username, member_email.lower(), PASSWORD)
        member.num = counter.value
        member.username_lower = member_username.lower()
        member.oldpassword = member_oldpassword
        member.truename = truename
        member.sex = sex
        member.birthday = birthday
        member.phone = phone

        member.auth = hashlib.sha1(str(member.num) + ':' + user.password).hexdigest()
        member.l10n = site.l10n
        member.newbie = 1
        member.noob = 0
        if member.num == 1:
            member.level = 0
        else:
            member.level = 1000
        user.save()
        member.user = user
        member.save()
        counter.save()
        counter2.save()

if __name__ == '__main__':
    getdata()