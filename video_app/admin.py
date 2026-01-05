from django.contrib import admin
from .models import Video

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'category')
    fields = ('created_at', 'title', 'description', 'category', 'original_file')
    readonly_fields = ('created_at', 'status')

admin.site.register(Video, VideoAdmin)
