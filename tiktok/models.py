from djongo import models
from django.contrib.auth.models import User

class WeeklyReport(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    title = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

class Tiktok(models.Model):
    weekly_report = models.ForeignKey(WeeklyReport, on_delete=models.CASCADE)
    thumbnail = models.TextField()
    like_count = models.IntegerField()
    view_count = models.IntegerField()
    comment_count = models.IntegerField()
    favourite_count = models.IntegerField()
    improvement_like_count = models.IntegerField()
    improvement_view_count = models.IntegerField()
    improvement_comment_count = models.IntegerField()
    improvement_favourite_count = models.IntegerField()
    notes = models.TextField(null=True, blank=True)
    url = models.TextField()
    created = models.DateField()
    last_updated = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.thumbnail
