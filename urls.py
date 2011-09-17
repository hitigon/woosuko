# coding=utf-8

from django.conf.urls.defaults import *

from django.contrib import admin
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
from iv2ex.woosuko import getdata2

admin.autodiscover()

urlpatterns = patterns('',
    # Example:

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    #(r'^admin/(.*)', admin.site.root),
    url(r'^admin/', include(admin.site.urls)),
    #(r"^(?i)upload/(?P<path>.*)$", "dynamic_media_serve.serve", {'document_root': settings.STATIC_UPLOAD}),
    # serve static medias
    (r'^(?i)media/(?P<path>.*)$',      'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT }),
    (r'^(?i)themes/(?P<path>.*)$',     'django.views.static.serve',{'document_root': settings.STATIC_THEMES}),
    (r'^(?i)img/(?P<path>.*)$',     'django.views.static.serve',{'document_root': settings.STATIC_IMAGE}),
    (r'^(?i)css/(?P<path>.*)$',        'django.views.static.serve',{'document_root': settings.STATIC_CSS}),
    (r'^(?i)js/(?P<path>.*)$',         'django.views.static.serve',{'document_root': settings.STATIC_JS}),
    (r'^(?i)upload/(?P<path>.*)$',     'django.views.static.serve',{'document_root': settings.STATIC_UPLOAD}),
    (r'^(?i)editor/(?P<path>.*)$',     'django.views.static.serve',{'document_root': settings.STATIC_EDITOR}),
    (r'^(?i)api_resources/(?P<path>.*)$',     'django.views.static.serve',{'document_root': settings.STATIC_API}),
)


from woosuko.iv2ex import views as iv
urlpatterns += patterns('',
    (r'^$', iv.HomeHandler),
    (r'^signup/', iv.SignupHandler),
    (r'^signin/', iv.SigninHandler),
    (r'^signout/', iv.SignoutHandler),
    (r'^go-graph/(?P<node_name>.*)$', iv.NodeGraphHandler),
    (r'^go/(?P<node_name>.*)$', iv.NodeHandler),

    (r'^planes/', iv.PlanesHandler),
    (r'^recent/', iv.RecentHandler),
#    ('/ua', UAHandler),
#    ('/signin', SigninHandler),
#    ('/signup', SignupHandler),
#    ('/signout', SignoutHandler),
#    ('/forgot', ForgotHandler),
#    ('/reset/([0-9]+)', PasswordResetHandler),
#    ('/go/([a-zA-Z0-9]+)', NodeHandler),
#    ('/n/([a-zA-Z0-9]+).json', NodeApiHandler),
#    ('/q/(.*)', SearchHandler),
#    ('/_dispatcher', DispatcherHandler),
    (r'^changes/', iv.ChangesHandler),
#    ('/(.*)', RouterHandler)
)

from woosuko.iv2ex import member as im
urlpatterns += patterns('',
    (r'^member/(?P<member_username>.*)$', im.MemberHandler),
    (r'^settings/', im.SettingsHandler),
#    ('/member/([a-z0-9A-Z\_\-]+).json', MemberApiHandler),
    (r'^settings-password/', im.SettingsPasswordHandler),
    (r'^settings-avatar/', im.SettingsAvatarHandler),
#    ('/block/(.*)', MemberBlockHandler),
#    ('/unblock/(.*)', MemberUnblockHandler)
#    ],
)

from woosuko.iv2ex import place as ip
urlpatterns += patterns('',
    (r'^place/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', ip.PlaceHandler),
    (r'^remove/place_message/(.*)', ip.PlaceMessageRemoveHandler),
)

from woosuko.iv2ex import backstage as ib
urlpatterns += patterns('',
    (r'^backstage/', ib.BackstageHomeHandler),
    (r'^backstage-site/', ib.BackstageSiteHandler),
    (r'^backstage-topic', ib.BackstageTopicHandler),
    (r'^backstage-new-section', ib.BackstageNewSectionHandler),
    (r'^backstage-section/(?P<section_name>.*)$', ib.BackstageSectionHandler),
    (r'^backstage-new-node/(?P<section_name>.*)$', ib.BackstageNewNodeHandler),
    (r'^backstage-node/(?P<node_name>.*)$', ib.BackstageNodeHandler),
    (r'^backstage-new-minisite', ib.BackstageNewMinisiteHandler),
    (r'^backstage-minisite/(.*)', ib.BackstageMinisiteHandler),
    (r'^backstage-new-page/(.*)', ib.BackstageNewPageHandler),
    (r'^backstage-page/(?P<page_key>.*)$', ib.BackstagePageHandler),
#    (r'^backstage/remove/minisite/(.*)', BackstageRemoveMinisiteHandler),
#    (r'^backstage/remove/page/(.*)', BackstageRemovePageHandler),
    (r'^backstage-node-avatar/(?P<node_name>.*)$', ib.BackstageNodeAvatarHandler),
    (r'^backstage-remove-reply/(?P<reply_num>.*)$', ib.BackstageRemoveReplyHandler),
    (r'^backstage-tidy-reply/(?P<reply_num>.*)$', ib.BackstageTidyReplyHandler),
    (r'^backstage-tidy-topic/(?P<topic_num>.*)$', ib.BackstageTidyTopicHandler),
#    (r'^backstage/deactivate/user/(.*)', BackstageDeactivateUserHandler),
    (r'^backstage-move-topic/(?P<topic_id>.*)$', ib.BackstageMoveTopicHandler),
#    (r'^backstage/remove/mc', BackstageRemoveMemcacheHandler),
    (r'^backstage-member/(?P<member_username>.*)$', ib.BackstageMemberHandler),
    (r'^backstage-members/', ib.BackstageMembersHandler),
    (r'^backstage-remove-notification/(?P<notification_id>.*)$', ib.BackstageRemoveNotificationHandler),
)

from woosuko.iv2ex import topic as it
urlpatterns += patterns('',
    (r'^new/(?P<node_name>.*)$', it.NewTopicHandler),
    (r'^t/([0-9]+)', it.TopicHandler),
#    (r'^index/topic/([0-9]+)', it.TopicIndexHandler),
    (r'^delete/topic/([0-9]+)', it.TopicDeleteHandler),
#    ('/t/([0-9]+).txt', TopicPlainTextHandler),
    (r'^edit-topic/([0-9]+)', it.TopicEditHandler),
    (r'^edit-reply/([0-9]+)', it.ReplyEditHandler),
    (r'^hit-topic/(?P<topic_id>.*)$', it.TopicHitHandler),
    (r'^hit-page/(?P<page_id>.*)$', it.PageHitHandler)
)

from woosuko.iv2ex import favorite as ifa
urlpatterns += patterns('',
    (r'^favorite-node/(?P<node_name>.*)$', ifa.FavoriteNodeHandler),
    (r'^unfavorite-node/(?P<node_name>.*)$', ifa.UnfavoriteNodeHandler),
    (r'^favorite-topic/(?P<topic_num>.*)$', ifa.FavoriteTopicHandler),
    (r'^unfavorite-topic/(?P<topic_num>.*)$', ifa.UnfavoriteTopicHandler),
    (r'^follow/(?P<one_num>.*)$', ifa.FollowMemberHandler),
    (r'^unfollow/(?P<one_num>.*)$', ifa.UnfollowMemberHandler)
)

from woosuko.iv2ex import my as imy
urlpatterns += patterns('',
    (r'^my-nodes/', imy.MyNodesHandler),
    (r'^my-topics/', imy.MyTopicsHandler),
    (r'^my-following/', imy.MyFollowingHandler)
)

from woosuko.iv2ex import notifications as ino
urlpatterns += patterns('',
    (r'^notifications/', ino.NotificationsHandler),
)

from woosuko.iv2ex import t as itw
urlpatterns += patterns('',
    (r'^twitter/$', itw.TwitterHomeHandler),
    (r'^twitter/mentions/$', itw.TwitterMentionsHandler),
    (r'^twitter/inbox/$', itw.TwitterDMInboxHandler),
    (r'^twitter/user/([a-zA-Z0-9\_]+)', itw.TwitterUserTimelineHandler),
    (r'^twitter/link/', itw.TwitterLinkHandler),
    (r'^twitter/unlink/$', itw.TwitterUnlinkHandler),
    (r'^twitter/oauth/$', itw.TwitterCallbackHandler),
    (r'^twitter/tweet/$', itw.TwitterTweetHandler),
    #(r'^twitter/api/$', itw.TwitterApiCheatSheetHandler),
)

from iv2ex.itaskqueue import ITaskQueueThread
itaskqueue =  ITaskQueueThread(2)
itaskqueue.start()