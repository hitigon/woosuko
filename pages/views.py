#coding=utf-8
'''
Created on 2011-4-9

@author: JohnQiao
'''
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

def index(request):
    member = None

    site = None

    data = {
        'member' : member,
    }
    return render_to_response('desktop/index.html', data)

def signup(request):
    return render_to_response('desktop/signup.html')