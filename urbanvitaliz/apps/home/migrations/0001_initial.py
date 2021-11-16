# Generated by Django 3.2.9 on 2021-11-16 09:15
# Updated for migration of existing data

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_user_profiles(apps, schema_editor):
    """Create the profiles for existing users"""
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("home", "UserProfile")
    db_alias = schema_editor.connection.alias
    for user in User.objects.using(db_alias).all():
        UserProfile.objects.using(db_alias).get_or_create(user=user)


def delete_user_profiles(apps, schema_editor):
    """Delete the profiles for existing users"""
    pass  # table will be deleted


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("geomatics", "0003_alter_department_code"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("deleted", models.DateTimeField(blank=True, null=True)),
                (
                    "departments",
                    models.ManyToManyField(
                        related_name="user_profiles", to="geomatics.Department"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "profil utilisateur",
                "verbose_name_plural": "profils utilisateurs",
            },
        ),
        migrations.RunPython(create_user_profiles, delete_user_profiles),
    ]
