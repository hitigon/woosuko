#coding=utf-8
'''
Created on 11-9-21

@author: qiaoshun8888
'''
import os
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.cache import cache as memcache
from iv2ex.models import KoreanGrammar

@login_required
def TopicHandler(request):
    if request.method == 'GET':
        template_values = {}
        path = os.path.join('desktop', 'korean_grammar.html')
        return render_to_response(path, template_values)
    else:
        template_values = {}
        if 'key_word' in request.POST:
            key_word = request.POST['key_word']
            if 't' in request.POST:
                t = request.POST['t']
            else:
                t = '0'
            if key_word == '':
                return HttpResponseRedirect('/korean/grammar/')
            topic_list = memcache.get('Korean_grammar_' + key_word.replace(' ','#'))
            if topic_list is None:
                if t == '0':
                    topic_list = KoreanGrammar.objects.filter(title__contains=key_word)
                else:
                    topic_list = KoreanGrammar.objects.filter(Q(title__contains=key_word) | Q(content__contains=key_word))
                memcache.set('Korean_grammar_' + key_word.replace(' ','#'), topic_list, 86400)
            for topic in topic_list:
                topic.title = topic.title.replace(key_word,"<span style='color:red'>"+key_word+"</span>")
                topic.content = topic.content.replace(key_word,"<span style='color:red'>"+key_word+"</span>")
            template_values['topic_list'] = topic_list
            template_values['topic_list_size'] = len(topic_list)
            path = os.path.join('desktop', 'korean_grammar.html')
            return render_to_response(path, template_values)