# Generated by Django 5.2 on 2025-05-19 18:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nikkuapp', '0003_ticket'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('ticket_created', 'New Ticket Created'), ('ticket_updated', 'Ticket Updated'), ('ticket_assigned', 'Ticket Assigned'), ('ticket_resolved', 'Ticket Resolved'), ('comment_added', 'New Comment Added')], max_length=20)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='nikkuapp.ticket')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
