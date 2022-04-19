# Generated by Django 3.2.3 on 2022-04-19 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0047_alter_task_priority'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name="date d'invitation")),
                ('accepted_on', models.DateTimeField(blank=True, default=None, editable=False, null=True, verbose_name="date d'acceptation")),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField(blank=True, null=True)),
                ('role', models.CharField(choices=[('COLLABORATOR', 'Collaborateur·rice'), ('SWITCHTENDER', 'Aiguilleur·se')], default='COLLABORATOR', max_length=20)),
                ('inviter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='invitant')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='projects.project', verbose_name='projet')),
            ],
            options={
                'unique_together': {('email', 'project', 'role')},
            },
        ),
    ]
