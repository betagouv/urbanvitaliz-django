# Generated by Django 3.2.3 on 2021-07-19 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("geomatics", "0003_alter_department_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
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
                ("name", models.CharField(max_length=90)),
                (
                    "departments",
                    models.ManyToManyField(
                        blank=True,
                        to="geomatics.Department",
                        verbose_name="Départements concernés",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Contact",
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
                ("first_name", models.CharField(blank=True, max_length=50)),
                ("last_name", models.CharField(blank=True, max_length=50)),
                ("phone_no", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                (
                    "division",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Service"
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contacts",
                        to="addressbook.organization",
                    ),
                ),
            ],
        ),
    ]
