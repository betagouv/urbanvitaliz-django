# Generated by Django 3.2.3 on 2022-02-02 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0019_resource_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='status',
            field=models.IntegerField(choices=[(0, 'Brouillon'), (1, 'A relire'), (2, 'Publié')], default=0, verbose_name='État'),
        ),
    ]