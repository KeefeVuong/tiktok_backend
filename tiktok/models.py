from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tiktok_account = models.TextField()

class WeeklyReport(models.Model):
    title = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    created_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.created_date = datetime.today().strftime('20%y-%m-%d')
        super().save(*args, **kwargs)

class Tiktok(models.Model):
    weekly_report = models.ForeignKey(WeeklyReport, on_delete=models.CASCADE)
    thumbnail = models.TextField(null=True, blank=True)
    like_count = models.IntegerField()
    view_count = models.IntegerField()
    comment_count = models.IntegerField()
    favourite_count = models.IntegerField()
    share_count = models.IntegerField()
    improvement_like_count = models.IntegerField()
    improvement_view_count = models.IntegerField()
    improvement_comment_count = models.IntegerField()
    improvement_favourite_count = models.IntegerField()
    notes = models.TextField(null=True, blank=True)
    hook = models.TextField(null=True, blank=True)
    improvements = models.TextField(null=True, blank=True)
    other_platform_notes = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    created = models.DateField()
    last_updated = models.DateField(null=True, blank=True)
    order = models.IntegerField()

    def __str__(self):
        return self.thumbnail
