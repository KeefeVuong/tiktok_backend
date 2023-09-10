# Generated by Django 4.2.4 on 2023-09-05 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tiktok', '0003_weeklyreport_tiktok_weekly_report_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tiktok',
            name='weekly_report_id',
        ),
        migrations.AddField(
            model_name='tiktok',
            name='weekly_report',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tiktok.weeklyreport'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tiktok',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
