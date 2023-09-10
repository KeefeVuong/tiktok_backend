# Generated by Django 4.2.5 on 2023-09-10 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tiktok", "0012_tiktok_owner"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tiktok",
            name="owner",
        ),
        migrations.AddField(
            model_name="weeklyreport",
            name="owner",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
