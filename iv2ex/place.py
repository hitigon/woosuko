#coding=utf-8
'''
Created on 11-9-12

@author: qiaoshun8888
'''
import os
import random
from django.shortcuts import render_to_response
from iv2ex.models import PlaceMessage
from v2ex.babel.da import GetSite, GetPlaceByIP, CreatePlaceByIP
from v2ex.babel.l10n import GetMessages
from v2ex.babel.security import CheckAuth


def PlaceHandler(request, ip):
    if request.method == 'GET':
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        member = CheckAuth(request)
        if member:
            template_values['member'] = member
        l10n = GetMessages(member, site)
        template_values['l10n'] = l10n
        template_values['ip'] = ip
        substance = GetPlaceByIP(ip)
        if substance:
            template_values['substance'] = substance
            template_values['messages'] = PlaceMessage.objects.filter(place=substance).order_by('-created')[:30]
        else:
            if member:
                if member.ip == ip:
                    substance = CreatePlaceByIP(ip)
                    template_values['substance'] = substance
        can_post = False
        can_see = True
        if member:
            if member.ip == ip:
                can_post = True
                can_see = True
            else:
                can_see = False
        else:
            if 'X-Real-IP' in request.META:
                ip_guest = request.META['X-Real-IP']
            else:
                ip_guest = request.META['REMOTE_ADDR']
            if ip_guest == ip:
                can_see = True
            else:
                can_see = False
        template_values['can_post'] = can_post
        template_values['can_see'] = can_see
        if member:
            template_values['ip_guest'] = member.ip
        else:
            template_values['ip_guest'] = ip_guest
        template_values['page_title'] = site.title + u' › ' + ip
        path = os.path.join('desktop', 'place.html')
        return render_to_response(path, template_values)

    def post(self, ip):
        site = GetSite()
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/place'
        member = CheckAuth(self)
        place = GetPlaceByIP(ip)
        say = self.request.get('say').strip()
        if len(say) > 0 and len(say) < 280 and member and place:
            if member.ip == ip:
                message = PlaceMessage()
                q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place_message.max')
                if (q.count() == 1):
                    counter = q[0]
                    counter.value = counter.value + 1
                else:
                    counter = Counter()
                    counter.name = 'place_message.max'
                    counter.value = 1
                q2 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place_message.total')
                if (q2.count() == 1):
                    counter2 = q2[0]
                    counter2.value = counter2.value + 1
                else:
                    counter2 = Counter()
                    counter2.name = 'place_message.total'
                    counter2.value = 1
                message.num = counter.value
                message.place = place
                message.place_num = place.num
                message.member = member
                message.content = say
                message.put()
                counter.put()
                counter2.put()
        self.redirect(go)

def PlaceMessageRemoveHandler(request):
    def get(self, key):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/place'
        member = CheckAuth(self)
        if member:
            message = db.get(db.Key(key))
            if message:
                if message.member.num == member.num:
                    message.delete()
                    q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place_message.total')
                    if (q.count() == 1):
                        counter = q[0]
                        counter.value = counter.value - 1
                        counter.put()
        self.redirect(go)

#def main():
#    application = webapp.WSGIApplication([
#    ('/place/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', PlaceHandler),
#    ('/remove/place_message/(.*)', PlaceMessageRemoveHandler)
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()