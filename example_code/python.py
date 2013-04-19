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

    @staticmethod
    def _filter(request, *args, **kwargs):
        """
        Get filter merged with 'find' paramert
        """
        native_filter = ParamsMiddleware._named_params(request, 'filter')
        find = FindParserMiddleware.parse_find(request, 'find')
        
        return (native_filter, find)
        
    @staticmethod
    def _sort(request, *args, **kwargs):
        """
        Get sort
        """
        wet_sort = json.loads(request.GET.get('sort', "[]"))
        
        result = []
        for item in wet_sort:
            sorted = {'key': lambda k: k[item["property"]]}

            if(item["direction"] == "DESC"):
                sorted["reverse"] = True

            result.append(sorted)
            
        return result
    
    @staticmethod
    def _named_params(request, key, *args, **kwargs):
        """
        Provides reorganazing list of dict of items, like:
            [{"property":"categories__id","value":null}]
        to:
            {"categories__id": null}
        """
        wet_params = json.loads(request.GET.get(key, "[]"))
        
        result = {}
        for item in wet_params:
            result[item["property"]] = item["value"]
            
        return result
    
class FindParserMiddleware:
    """
    Class to parse GET find parameter.
    """
    @staticmethod
    def parse_find(request, par_name, *args, **kwargs):
        result = list()
        
        find = json.loads(request.GET.get(par_name, "[]"))
        for item in find:
            if item["type"] == "numeric":
                result.append(FindParserMiddleware._parse_numeric(item))
            elif item["type"] == "string":
                result.append(FindParserMiddleware._parse_string(item))
            elif item["type"] == "date":
                result.append(FindParserMiddleware._parse_date(item))
            elif item["type"] == "list":
                result.append(FindParserMiddleware._parse_list(item))
            elif item["type"] == "boolean":
                result.append(FindParserMiddleware._parse_boolean(item))
        
        return result
                
    @staticmethod
    def _parse_numeric(item):
        if item["comparison"] == 'lt':
            return {'function': lambda k: k[item["field"]] < item["value"]}
        elif item["comparison"] == 'gt':
            return {'function': lambda k: k[item["field"]] > item["value"]}
        elif item["comparison"] == 'eq':
            return {'function': lambda k: k[item["field"]] == item["value"]}
            
    @staticmethod
    def _parse_string(item):
        return {'function': lambda k: k[item["field"]].find(item["value"])}
        
    @staticmethod
    def _parse_date(item):
        wet_date = item["value"].split('/')
        
        year = int(wet_date[2])
        month = int(wet_date[0])
        day = int(wet_date[1])
        
        date = datetime.date(year, month, day)
        
        if item["comparison"] == 'lt':
            return {'function': lambda k: k[item["field"]] < date}
        elif item["comparison"] == 'gt':
            return {'function': lambda k: k[item["field"]] > date}
        elif item["comparison"] == 'eq':
            return {'function': lambda k: k[item["field"]] == date}
        
    @staticmethod
    def _parse_list(item):
        return {'function': lambda k: k[item["field"]] in item["value"]}
        
    @staticmethod
    def _parse_boolean(item):
        return {'function': lambda k: k[item["field"]] == item["value"]}

    
class RESTHandlerMiddleware(RESTHandler):
    """
    
    """

    model = None
    
    format = None
    
    limit = None
    start = None
    filter_parent = None
    filter = None
    sort = None
    
    data = None
    
    m2m = None
    
    annotate_fields=None
    aggregate_fields=None
    
    element_id = None

    cache_generator = None
    
    def __init__(self, request, model, m2m=None, annotate_fields=None, aggregate_fields=None, element_id=None, cache_generator=None):
        # django model's class
        self.model = model
        
        # GET/POST/PUT/DELETE
        self.format = request.method
        
        # set get params if exist
        self.limit, self.start, \
        self.filter_parent, self.filter, \
        self.sort = ParamsMiddleware.standart_get(request)
        
        # set POST, PUT params if exist
        self.data = ParamsMiddleware.standart_post(request)
        
        # dict of related many to namy fields. {'category_id': ('categories', Category)}
        if m2m:
            self.m2m = m2m
        else:
            self.m2m = {}
            
        # dict of fields that contain Count, Sum , etc. {'count': models.Count('keysets')}
        if annotate_fields:
            self.annotate_fields = annotate_fields
        else:
            self.annotate_fields = {}
        
        # DOES NOT USE YET    
        # dict of fields that contain Min, Max , etc. {'max_price': models.Max('price')}
        if aggregate_fields:
            self.aggregate_fields = aggregate_fields
        else:
            self.aggregate_fields = {}
        
        # element id if exists
        self.element_id = element_id

        # class to generate cache if need
        self.cache_generator = cache_generator
    
    def read(self, json_field, extra_fields=None, extra_filters=None, cache_generator_field=None):
        """
        Handle GET method
        """
        response = dict(results=[], totalCount=0)

        # generate cache if need
        if self.cache_generator and self.filter[cache_generator_field]:
            self.cache_generator.generate(self.filter[cache_generator_field])

        model = self.model

        parent_items = model.objects.filter(**self.filter_parent)

        for parent_item in parent_items:
            try:
                items = simplejson.loads(getattr(parent_item, json_field))
            except Exception, e:
                raise Exception("Can't get json_field: {0} of parent".format(json_field))
                
            for item in items:
                fields = {}

                # all annotate fields
                for field_name in self.annotate_fields.keys():
                    value = getattr(item, field_name)
                    fields[field_name] = value
                    
                # set extra fields. You can rewrite standart fields
                if extra_fields:
                    for field, function in extra_fields.items():
                        fields[field] = function(item)

                item.update(fields)
            
            response["results"].extend(items)

        for filter in self.filter:
            response["results"] = response["results"].filter(**self.filter)

        for sorter in self.sort:
            response["results"] = sorted(response["results"], **sorter)

        # If the standard filters is not enough
        if extra_filters:
            for function in extra_filters:
                response["results"] = [item for item in response["results"] if function(item)]
        
        response["totalCount"] = len(response["results"])
        response["results"] = response["results"][self.start : self.start + self.limit] 
        
        return response