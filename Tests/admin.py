from django.contrib import admin
from .models import Paper, Badge, Notification


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('unit_code', 'title', 'university', 'campus', 'year', 'exam_type', 'verified', 'downloads')
    list_filter = ('verified', 'university', 'year', 'campus', 'exam_type')
    search_fields = ('unit_code', 'title', 'course')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'earned')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_read', 'created_at')