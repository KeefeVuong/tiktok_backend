from django.contrib import admin

from .models import Tiktok, WeeklyReport

class TiktokAdmin(admin.ModelAdmin):

    list_display = ("id", "weekly_report_id", "last_updated")


class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "start_date", "end_date")

admin.site.register(Tiktok, TiktokAdmin)
admin.site.register(WeeklyReport, WeeklyReportAdmin)