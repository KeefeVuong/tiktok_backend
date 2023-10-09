from djongo import models
import uuid
from django.contrib.auth.models import User

class WeeklyReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class Tiktok(models.Model):
    weekly_report = models.ForeignKey(WeeklyReport, on_delete=models.CASCADE)
    thumbnail = models.TextField(null=True, blank=True)
    like_count = models.IntegerField()
    view_count = models.IntegerField()
    comment_count = models.IntegerField()
    favourite_count = models.IntegerField()
    improvement_like_count = models.IntegerField()
    improvement_view_count = models.IntegerField()
    improvement_comment_count = models.IntegerField()
    improvement_favourite_count = models.IntegerField()
    notes = models.TextField(null=True, blank=True)
    hook = models.TextField(null=True, blank=True)
    improvements = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    created = models.DateField()
    last_updated = models.DateField(null=True, blank=True)
    manual = models.BooleanField(default=False)

    def __str__(self):
        return self.thumbnail
