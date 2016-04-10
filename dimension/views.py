# -*- coding: utf-8 -*-
import json

from braces import views as braces
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View

from core.models import Location
from utils.views import AJAXRequiredMixin
from .models import Dimension


def dimension_to_json(dimension):
    path = dimension.get_path()
    return {
        '_id': dimension.id,
        'name': dimension.name,
        '_parentIds': path,
    }


def location_to_json(location):
    return {
        'id': location.id,
        'name': location.title,
        'parent': location.dimension.name
    }


class IndexView(braces.LoginRequiredMixin, TemplateView):
    template_name = 'dimension/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        qs = Dimension.objects.filter(parent__isnull=True)
        tree = []
        for dimension in qs:
            tree.append({
                'collapsed': True,
                'module': dimension.name,
                '_id': dimension.id,
                'children': [],
                '_has_children': Dimension.objects.filter(parent=dimension).exists()
            })
        ctx['js_data'] = {
            'tree': {
                '_id': 0,
                'module': 'Locations',
                'children': tree
            }
        }
        return ctx


class CreateAJAXView(braces.LoginRequiredMixin,
                     braces.JSONResponseMixin,
                     AJAXRequiredMixin,
                     View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data = self.data
        parent_id = data['parent_id']
        name = data['name']
        # TODO: validar que nombre no este vacio

        parent = None
        if parent_id:
            try:
                parent = Dimension.objects.get(id=parent_id)
            except Dimension.DoesNotExist:
                parent = None

        dimension = Dimension.objects.create(name=name, parent=parent)
        cx = {
            'items': [dimension_to_json(dimension)]
        }
        cx['_parentIds'] = cx['items'][0]['_parentIds']
        return self.render_json_response(cx)


class UpdateAJAXView(braces.LoginRequiredMixin,
                     braces.JSONResponseMixin,
                     AJAXRequiredMixin,
                     View):
    http_method_names = ['post']
    UPDATE_TYPES = dict(name='NAME', change_parent='CHANGE_PARENT')

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Dimension, pk=self.data['id'])
        if self.data['type'] == self.UPDATE_TYPES['name']:
            return self.render_json_response(self.update_name(obj))
        elif self.data['type'] == self.UPDATE_TYPES['change_parent']:
            return self.render_json_response(self.change_parent(obj))

        raise Http404

    def update_name(self, obj):
        # TODO: validar nombre
        obj.name = self.data['name']
        obj.save(update_fields=['name'])
        return dimension_to_json(obj)

    def change_parent(self, obj):
        parent = None
        if 'new_parent_id' in self.data:
            parent = get_object_or_404(Dimension, pk=self.data['new_parent_id'])
        obj.change_parent(parent)
        return dimension_to_json(obj)


class DeleteAJAXView(braces.LoginRequiredMixin,
                     braces.JSONResponseMixin,
                     AJAXRequiredMixin,
                     View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Dimension, pk=self.data['id'])
        data = dimension_to_json(obj)
        obj.delete()
        return self.render_json_response(data)


class ChildrenListAJAXView(braces.LoginRequiredMixin,
                           braces.JSONResponseMixin,
                           AJAXRequiredMixin,
                           View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        parent_id = self.kwargs['dimension_id']
        dimension_qs = Dimension.objects.filter(parent=parent_id).order_by('name')
        locations_qs = Location.objects.select_related('dimension') \
            .filter(dimensionpath__dimension=parent_id).order_by('title')
        ctx = {
            'locations': {
                'items': []
            }
        }
        tree = []
        path = []
        for dimension in dimension_qs:
            if not path:
                path = dimension.get_path()
            tree.append({
                'collapsed': True,
                'name': dimension.name,
                '_id': dimension.id,
                '_has_children': Dimension.objects.filter(parent=dimension).exists()
            })
        ctx['items'] = tree
        ctx['_parentIds'] = path

        for location in locations_qs:
            ctx['locations']['items'].append(location_to_json(location))

        ctx['locations']['total'] = len(ctx['locations']['items'])

        return self.render_json_response(ctx)


class ChildrenLocationListAJAXView(braces.LoginRequiredMixin,
                                   braces.JSONResponseMixin,
                                   AJAXRequiredMixin,
                                   View):
    http_method_names = ['get']
    DIRECT = 'direct'

    def get(self, request, *args, **kwargs):
        dimension_id = self.kwargs['dimension_id']
        params = self.request.GET
        filters = {}
        if params.get('kind', '') == self.DIRECT:
            filters['dimension'] = dimension_id
        else:
            filters['dimensionpath__dimension'] = dimension_id
        locations_qs = Location.objects.select_related('dimension') \
            .filter(**filters) \
            .order_by('title')

        ctx = {
            'items': []
        }

        for location in locations_qs:
            ctx['items'].append(location_to_json(location))

        return self.render_json_response(ctx)


class MoveLocationAJAXView(braces.LoginRequiredMixin,
                           braces.JSONResponseMixin,
                           AJAXRequiredMixin,
                           View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        location = get_object_or_404(Location=self.data['location_id'])
        new_dimension = get_object_or_404(Dimension, pk=self.data['new_parent_id'])
        location.change_dimension(new_dimension)
        return self.render_json_response(location_to_json(location))
