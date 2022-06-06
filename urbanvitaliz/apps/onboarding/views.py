from django.contrib.auth import models as auth
from django.shortcuts import render, reverse
from django.views.generic.edit import CreateView
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import models as projects
from urbanvitaliz.apps.projects.utils import generate_ro_key
from urbanvitaliz.utils import get_site_config_or_503

from . import forms, models


def onboarding(request):
    """Return the onboarding page"""
    site_config = get_site_config_or_503(request.site)

    # Fetch the onboarding form associated with the current site
    form = forms.OnboardingResponseForm(request.POST or None)
    onboarding_instance = models.Onboarding.objects.get(pk=site_config.onboarding.pk)
    # Add fields in JSON to dynamic form rendering field.
    form.fields["response"].add_fields(onboarding_instance.form)

    if request.method == "POST":
        if form.is_valid():
            onboarding_response = form.save(commit=False)
            onboarding_response.onboarding = onboarding_instance
            onboarding_response.save()

            project = projects.Project()
            project.ro_key = generate_ro_key()
            insee = form.cleaned_data.get("insee", None)
            if insee:
                project.commune = geomatics.Commune.get_by_insee_code(insee)
            else:
                postcode = form.cleaned_data.get("postcode")
                project.commune = geomatics.Commune.get_by_postal_code(postcode)

            project.save()
            project.sites.add(request.site)

            user, _ = auth.User.objects.get_or_create(
                username=form.cleaned_data.get("email"),
                defaults={
                    "email": form.cleaned_data.get("email"),
                    "first_name": form.cleaned_data.get("first_name"),
                    "last_name": form.cleaned_data.get("last_name"),
                },
            )

            # Make her project owner
            models.ProjectMember.objects.create(
                member=user, project=project, is_owner=True
            )

            log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # Create initial public note
            models.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.impediments}",
                public=True,
            ).save()

            # All green, notify
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

    return render(request, "onboarding/onboarding.html", locals())


class OnboardingView(CreateView):
    model = models.OnboardingResponse
    fields = ("response",)
    template_name = "projects/onboarding.html"

    form_model = models.Onboarding
    form_field = "form"
    form_pk_url_kwarg = "pk"
    response_form_fk_field = None
    response_field = "response"

    def _get_object_containing_form(self, pk):
        return form

    def form_valid(self, form):
        action = form.save(commit=False)
        action.survey = self.form_instance
        action.save()
        return super().form_valid(form)
