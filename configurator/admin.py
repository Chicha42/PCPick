from django.contrib import admin
from .models import Build

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('id', 'cpu', 'gpu', 'ram', 'mb', 'user', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'id')