# coding:utf-8
from __future__ import unicode_literals
import operator

from rest_framework.compat import coreapi, coreschema
from django.db import models
from functools import reduce
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings
from django.template import loader
from django.utils.encoding import force_str


class FullWordSearchFilter(BaseFilterBackend):
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    search_title = 'Custom Full Word Search.'
    search_description = 'Custom Full Word Search.'

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        return params.replace(',', ' ').split()

    @staticmethod
    def construct_search(field_name):
        return ["{}__icontains".format(field_name),
                "{}__istartswith".format(field_name),
                "{}__iendswith".format(field_name),
                "{}__exact".format(field_name),
                "{}__istartswith".format(field_name),
                "{}__iendswith".format(field_name),
                "{}__icontains".format(field_name),
                "{}__icontains".format(field_name),
                ]

    @staticmethod
    def construct_term(term):
        return [" {} ".format(term),
                "{} ".format(term),
                " {}".format(term),
                term,
                "{}-".format(term),
                "-{}".format(term),
                "-{} ".format(term),
                " {}-".format(term)
                ]

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'word_fields', None)

        if not search_fields:
            return queryset

        orm_lookups = [self.construct_search(str(search_field))
                       for search_field in search_fields]

        search_term = request.query_params.get(self.search_param, '').split()

        if not search_term:
            return queryset

        lookup_list = list()
        for orm_lookup in orm_lookups:
            and_query = list()
            for term in search_term:
                if term.startswith('-') or term.endswith('-'):
                    term = term.replace('-', '')
                and_query.append(
                    reduce(operator.or_, [models.Q(**{lookup: prep_term})
                                          for lookup, prep_term in zip(orm_lookup, self.construct_term(term))]))
            lookup_list.append(reduce(operator.and_, and_query))
        queryset = queryset.filter(reduce(operator.or_, lookup_list))
        return queryset

    def to_html(self, request, queryset, view):
        term = request.query_params.get(self.search_param, '').split()
        if len(term) != 1:
            term_to_form = ' '.join(term)
        else:
            term_to_form = term[0]
        if not getattr(view, 'word_fields', None):
            return ''

        context = {
            'param': 'search',
            'term': term_to_form
        }
        template = loader.get_template(self.template)
        return template.render(context)

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_str(self.search_title),
                    description=force_str(self.search_description)
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': self.search_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.search_description),
                'schema': {
                    'type': 'string',
                },
            },
        ]
