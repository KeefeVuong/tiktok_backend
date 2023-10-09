
# import serializers from the REST framework
from rest_framework import serializers
 
# import the todo data model
from .models import Tiktok, WeeklyReport
 
# create a serializer class
class TiktokSerializer(serializers.ModelSerializer):
 
    # create a meta class
    class Meta:
        model = Tiktok
        fields = ("id","weekly_report", "thumbnail", "like_count", "view_count", "comment_count", "favourite_count", "improvement_like_count", "improvement_comment_count", "improvement_favourite_count", "improvement_view_count", "notes", "hook", "improvements", "manual", "url", "created", "last_updated")

# create a serializer class
class WeeklyReportSerializer(serializers.ModelSerializer):
 
    # create a meta class
    class Meta:
        model = WeeklyReport
        fields = ("id", "owner", "title")

