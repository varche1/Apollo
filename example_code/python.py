# -*- coding: utf-8 -*-

import logging
import traceback
import simplejson
import json
import datetime
from functools import wraps

from django.http import HttpResponse
from django.db import models

from rest import Params, FindParser, RESTHandler

class ParamsMiddleware(Params):
    """

    """
    @staticmethod
    def standart_get(request):
        limit = int(request.GET.get('limit', 1000))
        start = int(request.GET.get('start', 0))
        filter_parent, filter = ParamsMiddleware._filter(request)
        sort = ParamsMiddleware._sort(request)
    
        return (limit, start, filter_parent, filter, sort)
class ParamsMiddleware2(Params):

    @staticmethod
    def _filter(request, *args, **kwargs):
        """
        Get filter merged with 'find' paramert
        """
        native_filter = ParamsMiddleware._named_params(request, 'filter')
        find = FindParserMiddleware.parse_find(request, 'find')
        
        return (native_filter, find)

    @staticmethod
    def _filtere2r(request, *args, **kwargs):
        """
        Get filter merged with 'find' paramert
        """
        native_filter = ParamsMiddleware._named_params(request, 'filter')
        find = FindParserMiddleware.parse_find(request, 'find')
        
        return (native_filter, find)
