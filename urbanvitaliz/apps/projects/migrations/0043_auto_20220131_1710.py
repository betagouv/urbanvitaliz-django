# Generated by Django 3.2.3 on 2022-01-31 16:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0042_auto_20220118_1057"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "proposé"),
                    (1, "en cours"),
                    (2, "blocage"),
                    (3, "terminé"),
                    (4, "refusé"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="switchtenders",
            field=models.ManyToManyField(
                blank=True,
                related_name="projects_managed",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Aiguilleu·r·se·s",
            ),
        ),
        migrations.AlterField(
            model_name="taskfollowup",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "proposé"),
                    (1, "en cours"),
                    (2, "blocage"),
                    (3, "terminé"),
                    (4, "refusé"),
                ]
            ),
        ),
    ]