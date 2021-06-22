# encoding: utf-8

"""
Urls for resources application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-16 11:05:44 CEST
"""


from django.urls import path

from . import views


urlpatterns = [
    path(r"resource/", views.resource_search, name="resources-resource-search"),
    path(
        r"resource/create/",
        views.resource_create,
        name="resources-resource-create",
    ),
    path(
        r"resource/<int:resource_id>/",
        views.resource_detail,
        name="resources-resource-detail",
    ),
    path(
        r"resource/<int:resource_id>/update/",
        views.resource_update,
        name="resources-resource-update",
    ),
]

# eof