# Generated by Django 3.2.3 on 2021-09-07 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0023_choice_priority"),
    ]

    operations = [
        migrations.AddField(
            model_name="questionset",
            name="color",
            field=models.CharField(
                blank=True, default="orange", max_length=10, verbose_name="Couleur"
            ),
        ),
    ]