# encoding: utf-8

__all__ = ["rest", "feeds", "notes", "sharing", "tasks"]

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

import csv
import datetime

from django.contrib import messages
from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import digests
from urbanvitaliz.utils import (build_absolute_url, is_staff_or_403,
                                is_switchtender_or_403)

from .. import models, signals
from ..forms import OnboardingForm, ProjectForm, SelectCommuneForm
from ..utils import (can_administrate_or_403, can_manage_project,
                     format_switchtender_identity, generate_ro_key,
                     get_active_project, get_switchtenders_for_project,
                     is_project_moderator, is_project_moderator_or_403,
                     is_regional_actor_for_project_or_403,
                     refresh_user_projects_in_session, set_active_project_id)

########################################################################
# On boarding
########################################################################


def onboarding(request):
    """Return the onboarding page"""
    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.emails.append(project.email)
            project.ro_key = generate_ro_key()
            insee = form.cleaned_data.get("insee", None)
            if insee:
                project.commune = geomatics.Commune.get_by_insee_code(insee)
            else:
                postcode = form.cleaned_data.get("postcode")
                project.commune = geomatics.Commune.get_by_postal_code(postcode)

            project.save()
            project.sites.add(request.site)

            models.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.impediments}",
                public=True,
            ).save()

            user, _ = auth.User.objects.get_or_create(
                username=project.email,
                defaults={
                    "email": project.email,
                    "first_name": form.cleaned_data.get("first_name"),
                    "last_name": form.cleaned_data.get("last_name"),
                },
            )
            log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")

            signals.project_submitted.send(
                sender=models.Project, submitter=user, project=project
            )

            # NOTE check if commune is unique for code postal
            if not insee and project.commune:
                communes = geomatics.Commune.objects.filter(
                    postal=project.commune.postal
                )
                if communes.count() > 1:
                    url = reverse(
                        "projects-onboarding-select-commune", args=[project.id]
                    )
                    return redirect(url)

            response = redirect("survey-project-session", project_id=project.id)
            response["Location"] += "?first_time=1"
            return response
    else:
        form = OnboardingForm()
    return render(request, "projects/onboarding.html", locals())


def create_project_prefilled(request):
    """Create a new project for someone else"""
    is_switchtender_or_403(request.user)

    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.status = "TO_PROCESS"
            project.emails.append(project.email)
            project.ro_key = generate_ro_key()
            postcode = form.cleaned_data.get("postcode")
            project.commune = geomatics.Commune.get_by_postal_code(postcode)
            project.save()
            project.switchtenders.add(request.user)
            project.sites.add(request.site)
            project.save()

            models.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.impediments}",
                public=True,
            ).save()

            user, _ = auth.User.objects.get_or_create(
                username=project.email,
                defaults={
                    "email": project.email,
                    "first_name": form.cleaned_data.get("first_name"),
                    "last_name": form.cleaned_data.get("last_name"),
                },
            )

            messages.success(
                request,
                "Un courriel d'invitation à rejoindre le projet a été envoyé à {0}.".format(
                    project.email
                ),
                extra_tags=["email"],
            )

            send_email(
                template_name="sharing invitation",
                recipients=[{"email": project.email}],
                params={
                    "sender": {"email": request.user.email},
                    "project": digests.make_project_digest(project),
                },
            )

            signals.project_submitted.send(
                sender=models.Project, submitter=user, project=project
            )

            # NOTE check if commune is unique for code postal
            if project.commune:
                communes = geomatics.Commune.objects.filter(
                    postal=project.commune.postal
                )
                if communes.count() > 1:
                    url = reverse(
                        "projects-onboarding-select-commune", args=[project.id]
                    )
                    return redirect(url)

            return redirect("projects-project-detail-knowledge", project_id=project.id)

    else:
        form = OnboardingForm()

    return render(request, "projects/project/create_prefilled.html", locals())


@login_required
def select_commune(request, project_id=None):
    """Intermediate screen to select proper insee number of commune"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    response = redirect("survey-project-session", project_id=project.id)
    response["Location"] += "?first_time=1"
    if not project.commune:
        return response
    communes = geomatics.Commune.objects.filter(postal=project.commune.postal)
    if request.method == "POST":
        form = SelectCommuneForm(communes, request.POST)
        if form.is_valid():
            project.commune = form.cleaned_data["commune"]
            project.save()
            return response
    else:
        form = SelectCommuneForm(communes)
    return render(request, "projects/select-commune.html", locals())


########################################################################
# Switchtender
########################################################################


@login_required
@ensure_csrf_cookie
def project_list_export_csv(request):
    """Export the projects for the switchtender as CSV"""
    is_switchtender_or_403(request.user)

    projects = (
        models.Project.on_site.for_user(request.user)
        .exclude(status="DRAFT")
        .order_by("-created_on")
    )

    today = datetime.datetime.today().date()

    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="urbanvitaliz-projects-{today}.csv"'
        },
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "departement",
            "commune_insee",
            "nom_friche",
            "detail_adresse",
            "date_contact",
            "contact_dossier",
            "mail",
            "tel",
            "conseillers",
            "statut_conseil",
            "nb_reco",
            "lien_projet",
        ]
    )

    for project in projects:
        switchtenders = get_switchtenders_for_project(project)
        switchtenders_txt = ", ".join(
            [format_switchtender_identity(u) for u in switchtenders]
        )

        writer.writerow(
            [
                project.commune.department.code if project.commune else "??",
                project.commune.insee if project.commune else "??",
                project.name,
                project.location,
                project.created_on.date(),
                f"{project.first_name} {project.last_name}",
                project.email,
                project.phone,
                switchtenders_txt,
                project.status,
                project.tasks.exclude(public=False).count(),
                build_absolute_url(
                    reverse("projects-project-detail", args=[project.id])
                ),
            ]
        )

    return response


@login_required
@ensure_csrf_cookie
def project_list(request):
    """Return the projects for the switchtender"""
    is_switchtender_or_403(request.user)

    project_moderator = is_project_moderator(request.user)

    draft_projects = []
    if is_project_moderator:
        draft_projects = (
            models.Project.on_site.in_departments(
                request.user.profile.departments.all()
            )
            .filter(status="DRAFT")
            .order_by("-created_on")
        )
    return render(request, "projects/project/list.html", locals())


def project_detail_from_sharing_link(request, project_ro_key):
    """Return a special view of the project using the sharing link"""
    try:
        project = models.Project.objects.filter(ro_key=project_ro_key)[0]
    except Exception:
        raise Http404()

    can_manage = can_manage_project(project, request.user)

    return render(request, "projects/project/detail-ro.html", locals())


@login_required
def project_update(request, project_id=None):
    """Update the base information of a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    can_administrate_or_403(project, request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            instance = form.save(commit=False)
            # postcode = form.cleaned_data.get("postcode")
            # project.commune = geomatics.Commune.get_by_postal_code(postcode)
            instance.updated_on = timezone.now()
            instance.save()
            form.save_m2m()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        if project.commune:
            postcode = project.commune.postal
        else:
            postcode = None
        form = ProjectForm(instance=project, initial={"postcode": postcode})
    return render(request, "projects/project/update.html", locals())


@login_required
def project_accept(request, project_id=None):
    """Update project as accepted for processing"""
    is_project_moderator_or_403(request.user)

    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.status = "TO_PROCESS"
        project.updated_on = timezone.now()
        project.save()

        signals.project_validated.send(
            sender=models.Project, moderator=request.user, project=project
        )

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_switchtender_join(request, project_id=None):
    """Join switchtender"""
    is_switchtender_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    is_regional_actor_for_project_or_403(project, request.user, allow_national=True)

    if request.method == "POST":
        project.switchtenders.add(request.user)
        project.updated_on = timezone.now()
        project.save()

        signals.project_switchtender_joined.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_switchtender_leave(request, project_id=None):
    """Leave switchtender"""
    is_switchtender_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    is_regional_actor_for_project_or_403(project, request.user, allow_national=True)

    if request.method == "POST":
        project.switchtenders.remove(request.user)
        project.updated_on = timezone.now()
        project.save()

        signals.project_switchtender_leaved.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_delete(request, project_id=None):
    """Mark project as deleted in the DB"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.deleted = project.updated_on = timezone.now()
        project.save()
    return redirect(reverse("projects-project-list"))


########################################################################
# Login methods and signals
########################################################################
@receiver(user_logged_in)
def post_login_set_active_project(sender, user, request, **kwargs):
    # store my projects in the session
    refresh_user_projects_in_session(request, user)

    # Needed since get_active_project expects a user attribute
    request.user = user

    active_project = get_active_project(request)

    if not active_project:
        # Try to fetch a project
        active_project = models.Project.on_site.filter(email=user.email).first()
        if active_project:
            set_active_project_id(request, active_project.id)


@login_required
def redirect_user_to_project(request):
    """Redirect user to project page given her context"""
    active_project = get_active_project(request)

    if active_project:
        return redirect(reverse("projects-project-detail", args=[active_project.id]))
    else:
        return redirect(reverse("home"))


# eof
