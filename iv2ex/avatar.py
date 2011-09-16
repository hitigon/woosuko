#coding=utf-8
'''
Created on 11-9-12

@author: qiaoshun8888
'''
from v2ex.babel.security import *
from v2ex.babel.da import *
#
#def AvatarHandler(request, member_num, size):
#    avatar = GetKindByName('Avatar', 'avatar_' + str(member_num) + '_' + str(size))
#    if avatar is not None:
#        self.response.headers['Content-Type'] = "image/png"
#        self.response.headers['Cache-Control'] = "max-age=172800, public, must-revalidate"
#        self.response.headers['Expires'] = "Sun, 25 Apr 2011 20:00:00 GMT"
#        self.response.out.write(avatar.content)
#    else:
#        self.error(404)
#
#def NodeAvatarHandler(request, node_num, size):
#    avatar = GetKindByName('Avatar', 'node_' + str(node_num) + '_' + str(size))
#    if avatar is not None:
#        self.response.headers['Content-Type'] = "image/png"
#        self.response.headers['Cache-Control'] = "max-age=172800, public, must-revalidate"
#        self.response.headers['Expires'] = "Sun, 25 Apr 2011 20:00:00 GMT"
#        self.response.out.write(avatar.content)
#    else:
#        self.error(404)
            
#
#def main():
#    application = webapp.WSGIApplication([
#    ('/avatar/([0-9]+)/(large|normal|mini)', AvatarHandler),
#    ('/navatar/([0-9]+)/(large|normal|mini)', NodeAvatarHandler)
#    ],
#                                         debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()
