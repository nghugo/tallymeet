# Generated by Django 4.2.3 on 2023-07-29 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0004_alter_pollresponderxref_poll_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='event_location',
            field=models.CharField(blank=True, max_length=4096, null=True),
        ),
    ]
