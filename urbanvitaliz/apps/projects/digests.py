from itertools import groupby

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from urbanvitaliz import utils
from urbanvitaliz.apps.communication.api import send_email

from . import models


def send_digests_for_new_recommendations_by_user(user):
    """
    For a given user, send a digest email containing all new recommendation.
    Each project generates a single email.
    """
    project_ct = ContentType.objects.get_for_model(models.Project)

    notifications = (
        user.notifications.unsent()
        .filter(target_content_type=project_ct, verb="a recommandé l'action")
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return False

    skipped_projects = []
    for project_id, project_notifications in groupby(
        notifications, key=lambda x: x.target_object_id
    ):
        # Only treat notifications for project in DONE status
        project = models.Project.objects.get(pk=project_id)
        if project.status != "DONE":
            skipped_projects.append(project_id)
            continue

        recommendations = []
        notification_count = 0
        for notification in project_notifications:
            action = notification.action_object
            notification_count += 1

            action_link = utils.build_absolute_url(
                reverse("projects-project-detail", args=[action.project_id])
                + "#actions",
            )

            recommendations.append(
                {
                    "created_by": {
                        "first_name": action.created_by.first_name,
                        "last_name": action.created_by.last_name,
                        "organization": {
                            "name": action.created_by.profile.organization
                            and action.created_by.profile.organization.name
                            or None
                        },
                    },
                    "intent": action.intent,
                    "content": action.content,
                    "resource": {
                        "title": action.resource and action.resource.title or ""
                    },
                    "url": action_link,
                }
            )

        project_link = utils.build_absolute_url(
            reverse("projects-project-detail", args=[action.project_id])
        )
        email_params = {
            "notification_count": notification_count,
            "project": {
                "name": action.project.name,
                "url": project_link,
                "commune": {
                    "postal": action.project.commune
                    and action.project.commune.postal
                    or "",
                    "name": action.project.commune
                    and action.project.commune.name
                    or "",
                },
            },
            "recos": recommendations,
        }

        name = f"{user.first_name} {user.last_name}"
        if name.strip() == "":
            name = "Madame/Monsieur"

        send_email(
            "new_recommendations_digest",
            {"name": name, "email": user.email},
            params=email_params,
        )

    # Mark them as dispatched
    notifications.exclude(target_object_id__in=skipped_projects).mark_as_sent()

    return True


def send_digests_for_new_sites_by_user(user):
    project_ct = ContentType.objects.get_for_model(models.Project)

    notifications = (
        user.notifications.unsent()
        .filter(target_content_type=project_ct, verb="a été validé")
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return False

    for notification in notifications:
        project = notification.action_object
        project_link = utils.build_absolute_url(
            reverse("projects-project-detail", args=[project.pk])
        )
        email_params = {
            "project": {
                "name": project.name,
                "org_name": project.org_name,
                "url": project_link,
                "commune": {
                    "postal": project.commune.postal,
                    "name": project.commune.name,
                    "department": {
                        "code": project.commune.department.code,
                        "name": project.commune.department.name,
                    },
                },
            },
        }

        name = f"{user.first_name} {user.last_name}"
        if name.strip() == "":
            name = "Madame/Monsieur"

        send_email(
            "new_site_for_switchtender",
            {
                "name": name,
                "email": user.email,
            },
            params=email_params,
        )

    # Mark them as dispatched
    notifications.mark_as_sent()

    return True


def send_digest_for_non_switchtender_by_user(user):
    return send_digest_by_user(user, template_name="digest_for_non_switchtender")


def send_digest_for_switchtender_by_user(user):
    return send_digest_by_user(user, template_name="digest_for_switchtender")


def send_digest_by_user(user, template_name):
    """
    Digests for switchtenders. Should be run at the end, to collect
    remaining notifications
    """
    notifications = user.notifications.unsent().order_by("target_object_id")

    if notifications.count() == 0:
        return False

    email_params = {"projects": [], "notification_count": notifications.count()}

    for project_id, project_notifications in groupby(
        notifications, key=lambda x: x.target_object_id
    ):
        project = models.Project.objects.get(pk=project_id)
        project_link = utils.build_absolute_url(
            reverse("projects-project-detail", args=[project.pk])
        )

        email_project_params = {
            "name": project.name,
            "url": project_link,
            "commune": {
                "postal": project.commune.postal,
                "name": project.commune.name,
            },
            "notifications": [],
            "notification_count": 0,
        }

        notification_count = 0
        for notification in project_notifications:
            notification_count += 1

            email_project_params["notifications"].append(
                f"{notification.actor} {notification.verb} {notification.action_object}"
            )

        email_project_params["notification_count"] = notification_count
        email_params["projects"].append(email_project_params)

    name = f"{user.first_name} {user.last_name}"
    if name.strip() == "":
        name = "Madame/Monsieur"

    send_email(
        template_name,
        {"name": name, "email": user.email},
        params=email_params,
    )

    # Mark them as dispatched
    notifications.mark_as_sent()

    return True
