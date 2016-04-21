# -*- coding: utf-8 -*-

from braces import views as braces
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View, CreateView, UpdateView
from django.forms.models import modelform_factory

from core.models import Location
from utils.views import AJAXRequiredMixin
from .models import Dimension, DimensionTag


def dimension_tag_to_json(dimension_tag):
    return {
        'id': dimension_tag.id,
        'name': dimension_tag.name
    }


def dimension_to_json(dimension, add_parent_ids=True):
    ctx = {
        '_id': dimension.id,
        'name': dimension.name,
        'code': dimension.code,
        'dimension_tag': '',
        'dimension_tag_name': ''
    }

    if add_parent_ids:
        path = dimension.get_path()
        ctx.update({'_parentIds': path})

    if dimension.dimension_tag:
        ctx.update({
            'dimension_tag': dimension.dimension_tag.id,
            'dimension_tag_name': dimension.dimension_tag.name
        })
    return ctx


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
            serialize_dimension = {
                'collapsed': True,
                'module': dimension.name,
                'children': [],
                '_has_children': Dimension.objects.filter(parent=dimension).exists()
            }
            serialize_dimension.update(dimension_to_json(dimension, False))
            tree.append(serialize_dimension)

        tags = []
        for tag in DimensionTag.objects.all().order_by('name'):
            tags.append({
                'id': tag.id,
                'name': tag.name
            })
        ctx['js_data'] = {
            'tree': {
                '_id': 0,
                'module': 'Locations',
                'children': tree
            },
            'tags': tags
        }
        return ctx


class CreateUpdateMixin(object):
    http_method_names = ['post']
    form_class = modelform_factory(Dimension, fields=('name', 'parent', 'code', 'dimension_tag'))

    def form_valid(self, form):
        obj = form.save()
        cx = {
            'items': [dimension_to_json(obj)]
        }
        cx['_parentIds'] = cx['items'][0]['_parentIds']
        return self.render_json_response(cx)

    def form_invalid(self, form):
        cx = {
            'errors': form.errors
        }
        return self.render_json_response(cx, status=400)


class CreateAJAXView(braces.LoginRequiredMixin,
                     braces.JSONResponseMixin,
                     AJAXRequiredMixin,
                     CreateUpdateMixin,
                     CreateView):
    pass


class UpdateAJAXView(braces.LoginRequiredMixin,
                     braces.JSONResponseMixin,
                     AJAXRequiredMixin,
                     CreateUpdateMixin,
                     UpdateView):
    form_class = modelform_factory(Dimension, fields=('name', 'code', 'dimension_tag'))

    def get_object(self):
        obj = get_object_or_404(Dimension, pk=self.data['id'])
        return obj

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
            .filter(dimensionpath__dimension=parent_id, members=request.user) \
            .order_by('title')
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

            serialize_dimension = {
                'collapsed': True,
                '_has_children': Dimension.objects.filter(parent=dimension).exists()
            }
            serialize_dimension.update(dimension_to_json(dimension, False))
            tree.append(serialize_dimension)

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
        location = get_object_or_404(Location, pk=self.data['location_id'])
        new_dimension = get_object_or_404(Dimension, pk=self.data['new_parent_id'])
        location.change_dimension(new_dimension)
        return self.render_json_response(location_to_json(location))


class CreateUpdateDimensionTagMixin(object):
    http_method_names = ['post']
    form_class = modelform_factory(DimensionTag, fields=('name',))

    def form_valid(self, form):
        obj = form.save()
        return self.render_json_response(dimension_tag_to_json(obj))

    def form_invalid(self, form):
        cx = {
            'errors': form.errors
        }
        return self.render_json_response(cx, status=400)


class CreateDimensionTagAJAXView(braces.LoginRequiredMixin,
                                 braces.JSONResponseMixin,
                                 AJAXRequiredMixin,
                                 CreateUpdateDimensionTagMixin,
                                 CreateView):
    pass


class UpdateDimensionTagAJAXView(braces.LoginRequiredMixin,
                                 braces.JSONResponseMixin,
                                 AJAXRequiredMixin,
                                 CreateUpdateDimensionTagMixin,
                                 UpdateView):
    def get_object(self):
        obj = get_object_or_404(DimensionTag, pk=self.data['id'])
        return obj


class DeleteDimensionTagAJAXView(braces.LoginRequiredMixin,
                                 braces.JSONResponseMixin,
                                 AJAXRequiredMixin,
                                 View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(DimensionTag, pk=self.data['id'])
        data = dimension_tag_to_json(obj)
        obj.delete()
        return self.render_json_response(data)
