# Generated by Django 4.2.3 on 2023-07-23 15:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("polloption", "0013_alter_polloptionresponse_response"),
    ]

    operations = [
        migrations.AddField(
            model_name="polloptionresponse",
            name="responder_name",
            field=models.CharField(default="x", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="polloptionresponse",
            name="responder_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
