from django.contrib import admin

from .models import Tiktok, WeeklyReport

class TiktokAdmin(admin.ModelAdmin):

    list_display = ("id", "thumbnail", "like_count", "view_count", "comment_count", "notes", "created", "weekly_report_id", "last_updated")


class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "start_date", "end_date")

admin.site.register(Tiktok, TiktokAdmin)
admin.site.register(WeeklyReport, WeeklyReportAdmin)