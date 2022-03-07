# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-03-07 15:56:20 CEST -- HB David!
"""

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render, reverse
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import check_if_switchtender

from .. import models
from ..forms import PrivateNoteForm, PublicNoteForm
from ..utils import (can_administrate_project, can_manage_or_403,
                     can_manage_project,
                     get_notification_recipients_for_project,
                     is_regional_actor_for_project, set_active_project_id)


@login_required
def project_detail(request, project_id=None):
    """Set as active project, then redirect to knowledge page"""
    return redirect(reverse("projects-project-detail-knowledge", args=[project_id]))


@login_required
def project_detailx(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)

    # Set this project as active
    set_active_project_id(request, project.pk)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user.email != project.email:
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    try:
        survey = survey_models.Survey.objects.get(pk=1)  # XXX Hardcoded survey ID
        session, created = survey_models.Session.objects.get_or_create(
            project=project, survey=survey
        )
    except survey_models.Survey.DoesNotExist:
        session = None

    # Mark this project notifications unread
    project_ct = ContentType.objects.get_for_model(project)
    request.user.notifications.filter(
        target_content_type=project_ct.pk, target_object_id=project.pk
    ).mark_all_as_read()

    private_note_form = PrivateNoteForm()
    public_note_form = PublicNoteForm()

    recipients = get_notification_recipients_for_project(project)

    return render(request, "projects/project/", locals())


@login_required
def project_knowledge(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user.email != project.email:
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    try:
        survey = survey_models.Survey.objects.get(pk=1)  # XXX Hardcoded survey ID
        session, created = survey_models.Session.objects.get_or_create(
            project=project, survey=survey
        )
    except survey_models.Survey.DoesNotExist:
        session = None

    # Mark this project notifications unread
    project_ct = ContentType.objects.get_for_model(project)
    request.user.notifications.filter(
        target_content_type=project_ct.pk, target_object_id=project.pk
    ).mark_all_as_read()

    return render(request, "projects/project/knowledge.html", locals())


@login_required
def project_actions(request, project_id=None):
    """Action page for given project"""
    project = get_object_or_404(models.Project, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user.email != project.email:
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    return render(request, "projects/project/actions.html", locals())


@login_required
def project_conversations(request, project_id=None):
    """Action page for given project"""
    project = get_object_or_404(models.Project, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user.email != project.email:
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    public_note_form = PublicNoteForm()

    recipients = get_notification_recipients_for_project(project)

    return render(request, "projects/project/conversations.html", locals())


@login_required
def project_internal_followup(request, project_id=None):
    """Action page for given project"""
    project = get_object_or_404(models.Project, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user.email != project.email:
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    private_note_form = PrivateNoteForm()

    return render(request, "projects/project/internal_followup.html", locals())