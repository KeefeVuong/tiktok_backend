from django.contrib import admin

from .models import Tiktok, WeeklyReport, Client

class TiktokAdmin(admin.ModelAdmin):
    list_display = ("id", "weekly_report_id", "thumbnail", "last_updated", "order")


class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "platform")

class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tiktok_account")

admin.site.register(Tiktok, TiktokAdmin)
admin.site.register(WeeklyReport, WeeklyReportAdmin)
admin.site.register(Client, ClientAdmin)