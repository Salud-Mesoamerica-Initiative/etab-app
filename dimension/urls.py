# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns(
    '',
    url(
        r'^$',
        view=views.IndexView.as_view(),
        name='index'
    ),
    url(
        r'^create/$',
        view=views.CreateAJAXView.as_view(),
        name='create-ajax'
    ),
    url(
        r'^update/$',
        view=views.UpdateAJAXView.as_view(),
        name='update-ajax'
    ),
    url(
        r'^delete/$',
        view=views.DeleteAJAXView.as_view(),
        name='delete-ajax'
    ),
    url(
        r'^(?P<dimension_id>\d+)/get/children/$',
        view=views.ChildrenListAJAXView.as_view(),
        name='children-list-ajax'
    ),
    url(
        r'^move/location/$',
        view=views.MoveLocationAJAXView.as_view(),
        name='move-location-ajax'
    ),
)
